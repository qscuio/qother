"""Run: python -m unittest discover -s staged/scripts -p 'test_review_sidecar.py' -v"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from validate_review_sidecar import ValidationError, load, main, validate

EXAMPLES = Path(__file__).resolve().parents[1] / 'examples'


class SidecarTests(unittest.TestCase):
    def setUp(self):
        self.doc = load(EXAMPLES / 'review-sidecar.valid.json')

    def invalid(self, path):
        with self.assertRaises(ValidationError) as cm:
            validate(self.doc)
        self.assertIn(path, str(cm.exception))

    def test_valid(self):
        validate(self.doc)

    def test_invalid_fixtures(self):
        for path in sorted(EXAMPLES.glob('review-sidecar.invalid-*.json')):
            with self.subTest(path=path.name), self.assertRaises(ValidationError):
                validate(load(path))

    def test_missing(self):
        del self.doc['shots'][0]['rate']
        self.invalid('$.shots[0].rate')

    def test_integer_frames_reject_boolean_float_nan(self):
        for value in (True, 0.0, float('nan'), float('inf')):
            with self.subTest(value=value):
                self.doc['shots'][0]['source_range']['start'] = value
                self.invalid('$.shots[0].source_range.start')

    def test_nonfinite_seconds(self):
        for value in (True, float('nan'), float('inf'), -float('inf')):
            with self.subTest(value=value):
                self.doc['shots'][0]['source_range']['start_seconds'] = value
                self.invalid('$.shots[0].source_range.start_seconds')

    def test_rational_invalid(self):
        for value in (0, -1, True, 1.0, float('nan')):
            with self.subTest(value=value):
                self.doc['shots'][0]['rate']['num'] = value
                self.invalid('$.shots[0].rate.num')

    def test_inconsistent_seconds(self):
        self.doc['shots'][0]['source_range']['start_seconds'] = 1
        self.invalid('$.shots[0].source_range.start_seconds')

    def test_mismatched_retime(self):
        self.doc['shots'][1]['rate']['num'] = 3
        self.invalid('$.shots[1].rate')

    def test_source_bounds(self):
        self.doc['sources'][0]['duration_frames'] = 100
        self.invalid('$.shots[1].source_range.end')

    def test_timeline_bounds(self):
        self.doc['timeline']['duration_frames'] = 100
        self.invalid('$.shots[1].timeline_range.end')

    def test_duplicate_ids_across_types(self):
        self.doc['cues'][0]['id'] = 'shot-a'
        self.invalid('$.cues[0].id')

    def test_invalid_references(self):
        for entry, field, path in ((self.doc['shots'][0], 'source_id', '$.shots[0].source_id'),
                                   (self.doc['cues'][0], 'shot_id', '$.cues[0].shot_id')):
            with self.subTest(field=field):
                old = entry[field]
                entry[field] = 'missing'
                self.invalid(path)
                entry[field] = old

    def test_overlap_requires_policy(self):
        self.doc['shots'].append(dict(deepcopy(self.doc['shots'][0]), id='overlap'))
        self.invalid('timeline overlap')
        self.doc['policy'] = {'allow_overlaps': True}
        validate(self.doc)

    def test_gap_requires_policy(self):
        self.doc['timeline']['duration_frames'] += 1
        self.invalid('trailing gap')
        self.doc['policy'] = {'allow_gaps': True}
        validate(self.doc)

    def test_leading_gap_requires_policy(self):
        self.doc['cues'] = []
        self.doc['audio_groups'] = []
        self.doc['timeline']['duration_frames'] += 5
        for shot in self.doc['shots']:
            for field in ('start', 'end'):
                shot['timeline_range'][field] += 5
        self.invalid('timeline gap')
        self.doc['policy'] = {'allow_gaps': True}
        validate(self.doc)

    def test_caption_coverage_gap(self):
        self.doc['cues'][0]['coverage_source_ranges'] = [{'start': 12, 'end': 20}, {'start': 21, 'end': 36}]
        self.invalid('source coverage gap')

    def test_caption_coverage_required(self):
        del self.doc['cues'][0]['coverage_source_ranges']
        self.invalid('coverage_source_ranges')

    def test_caption_mapping_agreement(self):
        self.doc['cues'][0]['timeline_range']['end'] -= 1
        self.invalid('does not agree')

    def test_caption_partial_is_not_timeline_coverage_requirement(self):
        self.doc['cues'] = []
        self.doc['audio_groups'] = []
        validate(self.doc)

    def test_audio_role(self):
        self.doc['audio_groups'][0]['role'] = 'music'
        self.invalid('role does not match')

    def test_audio_missing_reference(self):
        self.doc['audio_groups'][0]['cue_ids'] = ['missing']
        self.invalid('unknown cue reference')

    def test_audio_duplicate_reference(self):
        self.doc['audio_groups'][0]['cue_ids'] *= 2
        self.invalid('already assigned')

    def test_unknown_unit_field(self):
        self.doc['shots'][0]['source_range']['unit'] = 'seconds'
        self.invalid('unknown field')

    def test_fractional_fps_exact(self):
        self.doc['timeline']['fps'] = {'num': 30000, 'den': 1001}
        self.doc['sources'][0]['fps'] = {'num': 24000, 'den': 1001}
        validate(self.doc)

    def test_loader_duplicate_key_nonfinite(self):
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'bad.json'
                path.write_text(text)
                with self.assertRaises(ValidationError):
                    load(path)


if __name__ == '__main__':
    unittest.main()
