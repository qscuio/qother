#!/usr/bin/env python3
"""Prepare separate spoken text from a versioned lexicon; never synthesize audio."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

DEFAULT_LEXICON = Path(__file__).resolve().parents[1] / 'pronunciation/technical-zh-CN.v1.json'
HYPHENS = '-\u2010\u2011'


class PendingPronunciationError(ValueError):
    """A requested replacement has not been auditioned for this voice profile."""


def _nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be a nonempty string')
    return value


def validate_lexicon(data):
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('Unsupported lexicon schema_version')
    _nonempty(data.get('version'), 'version')
    _nonempty(data.get('language'), 'language')
    entries = data.get('entries')
    if not isinstance(entries, list) or not entries:
        raise ValueError('entries must be a nonempty list')
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError('Each entry must be an object')
        term = _nonempty(entry.get('display'), 'display')
        _nonempty(entry.get('oral_reading'), f'{term}: oral_reading')
        aliases = entry.get('aliases', [])
        if not isinstance(aliases, list):
            raise ValueError(f'{term}: aliases must be a list')
        for spelling in [term, *aliases]:
            _nonempty(spelling, 'spelling')
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9\-\u2010\u2011]*', spelling):
                raise ValueError('Spellings must be explicit technical tokens, not regex or prose')
            if spelling in seen:
                raise ValueError(f'Duplicate spelling: {spelling}')
            seen.add(spelling)
        tts = entry.get('tts')
        if not isinstance(tts, dict):
            raise ValueError(f'{term}: missing tts object')
        _nonempty(tts.get('input'), f'{term}: tts.input')
        _nonempty(tts.get('engine'), f'{term}: tts.engine')
        audition = tts.get('audition')
        if not isinstance(audition, dict) or audition.get('status') not in {'pending', 'accepted'}:
            raise ValueError(f'{term}: invalid audition status')
        if audition['status'] == 'accepted':
            _nonempty(audition.get('profile'), f'{term}: accepted profile')
            _nonempty(audition.get('evidence'), f'{term}: accepted evidence')
            _nonempty(audition.get('input'), f'{term}: accepted input snapshot')
            _nonempty(audition.get('engine'), f'{term}: accepted engine snapshot')
    return data


def load_lexicon(path=DEFAULT_LEXICON):
    return validate_lexicon(json.loads(Path(path).read_text(encoding='utf-8')))


def _is_cjk(char):
    point = ord(char)
    return (0x3400 <= point <= 0x4DBF or 0x4E00 <= point <= 0x9FFF or
            0xF900 <= point <= 0xFAFF or 0x20000 <= point <= 0x323AF)


def _identifier_char(char):
    # Hanzi may touch a technical term. Other letters/digits/marks are boundaries
    # only when separated, so MACsec, éMAC, MAC_1 and unknown compounds survive.
    return bool(char) and (char in '_' + HYPHENS or
        ((char.isalnum() or unicodedata.category(char).startswith('M')) and not _is_cjk(char)))


def _token_boundary(text, start, end):
    left = text[start - 1] if start else ''
    right = text[end] if end < len(text) else ''
    if _identifier_char(left) or _identifier_char(right):
        return False
    if left == '.' and start > 1 and _identifier_char(text[start - 2]):
        return False
    if right == '.' and end + 1 < len(text) and _identifier_char(text[end + 1]):
        return False
    if text[max(0, start - 2):start] == '::' or text[end:end + 2] == '::':
        return False
    if right == '(':
        return False  # likely a function call; author its narration explicitly
    return True


def _protected_spans(text):
    """Conservatively protect Markdown code, URLs, and explicit file paths."""
    spans = []
    # Unclosed code fences/spans protect to EOF rather than changing code.
    fence = re.compile(r'(?m)^ {0,3}(`{3,}|~{3,})[^\n]*\n?')
    position = 0
    while match := fence.search(text, position):
        marker = match.group(1)
        closing = re.compile(r'(?m)^ {0,3}' + re.escape(marker[0]) + '{' + str(len(marker)) + r',}[ \t]*(?:\n|$)')
        close = closing.search(text, match.end())
        end = close.end() if close else len(text)
        spans.append((match.start(), end))
        position = end
    position = 0
    while match := re.search(r'`+', text[position:]):
        start = position + match.start(); marker = match.group()
        close = re.search(r'(?<!`)' + re.escape(marker) + r'(?!`)', text[start + len(marker):])
        end = start + len(marker) + close.end() if close else len(text)
        spans.append((start, end)); position = end
    for pattern in (r'(?i)\b(?:https?://|www\.)[^\s<>]+',
                    r'(?<![\w])(?:\.{0,2}/|[A-Za-z]:\\)[^\s<>]+'):
        spans.extend((m.start(), m.end()) for m in re.finditer(pattern, text))
    return spans


def prepare_spoken_text(display_text, lexicon, *, allow_pending=False, profile=None):
    """Return display_text, spoken_text and auditable original-offset matches.

    Case-sensitive, longest-first, single-pass substitution. This accepts prose,
    not a source-code parser. Code/URLs/path spans are kept verbatim. Pending
    candidates require explicit opt-in; acceptance is scoped to an exact profile.
    """
    if not isinstance(display_text, str):
        raise ValueError('display_text must be a string')
    validate_lexicon(lexicon)
    spellings = {spelling: entry for entry in lexicon['entries']
                 for spelling in [entry['display'], *entry.get('aliases', [])]}
    pattern = re.compile('|'.join(re.escape(s) for s in sorted(spellings, key=lambda s: (-len(s), s))))
    protected = _protected_spans(display_text)
    replacements = []
    pending = set()
    def replace(match):
        start, end = match.span()
        if not _token_boundary(display_text, start, end) or any(start < b and end > a for a, b in protected):
            return match.group()
        entry = spellings[match.group()]; tts = entry['tts']; audition = tts['audition']
        accepted = (audition['status'] == 'accepted' and profile is not None and
                    audition['profile'] == profile and audition['input'] == tts['input'] and
                    audition['engine'] == tts['engine'])
        if not accepted:
            pending.add(entry['display'])
        replacements.append({'display': entry['display'], 'matched': match.group(),
            'start': start, 'end': end, 'spoken': tts['input'], 'engine': tts['engine'],
            'audition_status': 'accepted_for_profile' if accepted else 'pending_for_profile'})
        return tts['input']
    spoken = pattern.sub(replace, display_text)
    if pending and not allow_pending:
        raise PendingPronunciationError('Pronunciation audition required: ' + ', '.join(sorted(pending)) +
            '. Use allow_pending only to prepare a clearly labeled audition/draft.')
    return {'lexicon_version': lexicon['version'], 'display_text': display_text,
            'spoken_text': spoken, 'profile': profile, 'replacements': replacements,
            'pending_terms': sorted(pending),
            'pronunciation_status': 'pending_audition' if pending else 'no_pending_replacements',
            'audio_generated': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--text', type=Path, required=True, help='Canonical UTF-8 prose, never overwritten')
    parser.add_argument('--lexicon', type=Path, default=DEFAULT_LEXICON)
    parser.add_argument('--out', type=Path, required=True, help='New private directory outside the public checkout')
    parser.add_argument('--allow-pending', action='store_true', help='Prepare candidate text for audition; does not approve audio production')
    parser.add_argument('--profile', help='Exact private reviewed model/voice/configuration identity')
    args = parser.parse_args(argv)
    if args.out.exists():
        raise ValueError('Output already exists; choose a new directory')
    original = args.text.read_bytes()
    lexicon_bytes = args.lexicon.read_bytes()
    lexicon = validate_lexicon(json.loads(lexicon_bytes.decode('utf-8')))
    result = prepare_spoken_text(original.decode('utf-8'), lexicon,
                               allow_pending=args.allow_pending, profile=args.profile)
    result['lexicon_sha256'] = hashlib.sha256(lexicon_bytes).hexdigest()
    args.out.mkdir(mode=0o700, parents=True, exist_ok=False)
    (args.out / 'display.txt').write_bytes(original)
    (args.out / 'spoken.txt').write_bytes(result['spoken_text'].encode('utf-8'))
    (args.out / 'pronunciation-report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['pronunciation_status'], 'replacements': len(result['replacements']),
                      'audio_generated': False}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(2)
