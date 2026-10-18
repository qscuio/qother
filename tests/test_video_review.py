import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('video_review', ROOT / 'scripts/validate_video_review.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def ready():
    # Synthetic record for structural tests; no actual media review is asserted.
    return dict(version=1, artifact='fixture.mp4', author='maker', reviewer='reviewer',
                review_kind='cold', decision='ready', checks=[dict(id='test', required=True,
                status='pass', evidence=['synthetic test fixture'])], issues=[])


def issue(severity='S1', status='open'):
    return dict(id='I1', severity=severity, status=status, location='scene-1/frame-24',
                finding='synthetic finding', evidence='synthetic evidence')


class ReviewTests(unittest.TestCase):
    def test_ready_record(self):
        self.assertEqual(module.validate(ready()), [])

    def test_example_is_conditional(self):
        record = json.loads((ROOT / 'docs/video-production/review.example.json').read_text())
        self.assertEqual(record['decision'], 'conditional')
        self.assertEqual(module.validate(record), [])

    def test_missing_evidence(self):
        r = ready(); r['checks'][0]['evidence'] = []
        self.assertTrue(module.validate(r))

    def test_pending_required_cannot_be_ready(self):
        r = ready(); r['checks'][0].update(status='not_run', evidence=[], limitation='not played')
        self.assertTrue(module.validate(r))

    def test_optional_pending_can_be_ready(self):
        r = ready(); r['checks'].append(dict(id='music', required=False, status='not_run', evidence=[], limitation='no music requested'))
        self.assertEqual(module.validate(r), [])

    def test_blockers_cannot_be_waived(self):
        for severity in ('S0', 'S1'):
            r = ready(); r['issues'] = [issue(severity, 'deferred')]
            r['issues'][0]['disposition'] = 'try to waive'
            self.assertTrue(module.validate(r))

    def test_fixed_needs_recheck(self):
        r = ready(); r['issues'] = [issue(status='fixed')]
        self.assertTrue(module.validate(r))
        r['issues'][0]['recheck'] = 'synthetic recheck'
        self.assertEqual(module.validate(r), [])

    def test_low_issue_needs_disposition(self):
        r = ready(); r['issues'] = [issue('S3', 'deferred')]
        self.assertTrue(module.validate(r))
        r['issues'][0]['disposition'] = 'retain stable layout to aid comparison'
        self.assertEqual(module.validate(r), [])

    def test_cold_cannot_be_author(self):
        r = ready(); r['reviewer'] = r['author']
        self.assertTrue(module.validate(r))

    def test_duplicate_check(self):
        r = ready(); r['checks'].append(copy.deepcopy(r['checks'][0]))
        self.assertTrue(module.validate(r))

    def test_malformed_types_fail_cleanly(self):
        for r in (None, [], {'checks': [None], 'issues': [None]}, {'version': True}, {'checks': 'bad'}):
            self.assertTrue(module.validate(r))

    def test_required_is_boolean(self):
        r = ready(); r['checks'][0]['required'] = 'yes'
        self.assertTrue(module.validate(r))

    def test_failed_required_is_not_ready(self):
        r = ready(); r['checks'][0]['status'] = 'fail'
        self.assertTrue(module.validate(r))

    def test_failed_required_cannot_be_conditional(self):
        r = ready(); r.update(decision='conditional', limitations='known failure')
        r['checks'][0]['status'] = 'fail'
        self.assertTrue(module.validate(r))
        r['decision'] = 'blocked'
        self.assertEqual(module.validate(r), [])

    def test_blocked_report_valid(self):
        r = ready(); r.update(decision='blocked', limitations='repair failure and recheck')
        r['issues'] = [issue()]
        self.assertEqual(module.validate(r), [])


if __name__ == '__main__':
    unittest.main()
