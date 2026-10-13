#!/usr/bin/env python3
"""Deterministic contract/state regressions. All generated fixtures stay in temp dirs."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from diagram import assemble, check_project, preflight, read_json, Renderer, state_at, validate_timeline, wav_info, write_json, write_wav

ROOT=Path(__file__).resolve().parents[1]


class DiagramTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="diagram-skill-test-")
        self.root=Path(self.tmp.name)
        self.project=read_json(ROOT/"assets/queue-example.json")
        self.source=self.root/"project.json"
        write_json(self.source,self.project)
        self.timeline=assemble(self.source,self.root/"build",preview=True)
    def tearDown(self):self.tmp.cleanup()
    def test_exact_narration_coverage(self):
        p=copy.deepcopy(self.project);p["scenes"][0]["narration"]+="Missing caption."
        with self.assertRaisesRegex(ValueError,"coverage"):check_project(p)
    def test_duplicate_identity_rejected(self):
        p=copy.deepcopy(self.project);p["scenes"][0]["elements"].append(copy.deepcopy(p["scenes"][0]["elements"][-1]))
        with self.assertRaisesRegex(ValueError,"identity"):check_project(p)
    def test_direction_mismatch_rejected(self):
        p=copy.deepcopy(self.project);e=p["scenes"][0]["elements"][5];e["from"],e["to"]=e["to"],e["from"]
        with self.assertRaisesRegex(ValueError,"geometry"):check_project(p)
    def test_gate_before_movement(self):
        p=copy.deepcopy(self.timeline)
        e=next(e for e in p["scenes"][0]["events"] if e["id"]=="grant-state");e["value"]="blocked"
        with self.assertRaisesRegex(ValueError,"gate not satisfied"):validate_timeline(p)
    def test_single_object_moves_and_queue_changes(self):
        s=self.timeline["scenes"][0]
        before=state_at(s,4.2);after=state_at(s,15.2)
        self.assertEqual(before["job"]["inside_queue"],"waiting")
        self.assertEqual(before["waiting"]["count"],1)
        self.assertIsNone(after["job"]["inside_queue"])
        self.assertEqual(after["waiting"]["count"],0)
        self.assertEqual(after["job"]["position"],[1095,350])
        self.assertEqual(sum(x["kind"]=="token" for x in after.values()),1)
    def test_missing_queue_count_rejected(self):
        p=copy.deepcopy(self.timeline)
        e=next(e for e in p["scenes"][0]["events"] if e["id"]=="count-arrival");e["count"]=0
        with self.assertRaisesRegex(ValueError,"Queue count"):validate_timeline(p)
    def test_concurrent_motion_rejected(self):
        p=copy.deepcopy(self.timeline);e=copy.deepcopy(p["scenes"][0]["events"][0]);e["id"]="duplicate-move";p["scenes"][0]["events"].append(e)
        with self.assertRaisesRegex(ValueError,"Concurrent"):validate_timeline(p)
    def test_preview_cannot_be_final(self):
        with self.assertRaisesRegex(ValueError,"preview"):preflight(self.root/"build/timeline.json")
        preflight(self.root/"build/timeline.json",preview=True)
    def test_silent_wav_rejected(self):
        f=self.root/"silent.wav";write_wav(f,b"\x00\x00"*24000,24000)
        with self.assertRaisesRegex(ValueError,"Silent"):wav_info(f)
    def test_audio_replacement_rejected(self):
        f=self.root/"build/narration.wav"
        b=bytearray(f.read_bytes());b[-1]=1;f.write_bytes(b)
        with self.assertRaisesRegex(ValueError,"hash changed"):preflight(self.root/"build/timeline.json",preview=True)
    def test_deterministic_frames_and_safe_text(self):
        r=Renderer(self.timeline)
        a=r.frame(9.8);b=r.frame(9.8)
        self.assertEqual(hashlib.sha256(a.tobytes()).digest(),hashlib.sha256(b.tobytes()).digest())
        self.assertNotEqual(a.tobytes(),r.frame(1.4).tobytes())
        p=copy.deepcopy(self.timeline);p["title"]="Too long "*50
        with self.assertRaisesRegex(ValueError,"too wide"):Renderer(p).frame(1)
    def supplied_fixture(self):
        # Artificial PCM only tests byte preservation; never rendered or presented as speech.
        p=copy.deepcopy(self.project);p["audio_provenance"]={"test_fixture":"Artificial PCM for byte-preservation regression, not speech"}
        rate=24000;lead=3840;gap=2880;tail=18000;parts=[b"\x00\x00"*lead];offset=lead;captions=[]
        for i,c in enumerate(p["scenes"][0]["clauses"]):
            pcm=struct.pack("<hh",1000+i,-1000-i)*36000
            f=self.root/f"clause-{i}.wav";write_wav(f,pcm,rate);c["wav"]=f.name
            captions.append({"text":c["text"],"start":offset/rate,"end":(offset+72000)/rate,"sample_count":72000})
            parts.append(pcm);offset+=72000
            if i<len(p["scenes"][0]["clauses"])-1:parts.append(b"\x00\x00"*gap);offset+=gap
        parts.append(b"\x00\x00"*tail);offset+=tail
        master=self.root/"supplied.wav";write_wav(master,b"".join(parts),rate)
        t={"duration":offset/rate,"sample_count":offset,"sample_rate":rate,"scenes":[{"id":"different-audio-id","start":0,"end":offset/rate,"duration":offset/rate,"narration":p["scenes"][0]["narration"],"captions":captions}]}
        timing=self.root/"supplied.json";write_json(timing,t);write_json(self.source,p)
        return master,timing,t
    def test_supplied_master_preserves_padding_gaps_and_bytes(self):
        master,timing,t=self.supplied_fixture()
        tl=assemble(self.source,self.root/"retained",master=master,timing=timing)
        self.assertEqual(master.read_bytes(),(self.root/"retained/narration.wav").read_bytes())
        self.assertEqual(tl["sample_count"],t["sample_count"])
        for c,expected in zip(tl["scenes"][0]["clauses"],t["scenes"][0]["captions"]):
            self.assertEqual((c["start"],c["end"]),(expected["start"],expected["end"]))
        self.assertEqual(tl["scenes"][0]["clauses"][0]["start"],.16)
        preflight(self.root/"retained/timeline.json")
    def test_supplied_caption_mismatch_rejected(self):
        master,timing,t=self.supplied_fixture();t["scenes"][0]["captions"][0]["text"]="Unrelated words"
        write_json(timing,t)
        with self.assertRaisesRegex(ValueError,"caption text differs"):
            assemble(self.source,self.root/"retained",master=master,timing=timing)
    def test_supplied_pcm_mismatch_rejected(self):
        master,timing,t=self.supplied_fixture();p=read_json(self.source)
        f=self.root/p["scenes"][0]["clauses"][0]["wav"];write_wav(f,struct.pack("<h",1500)*72000,24000)
        with self.assertRaisesRegex(ValueError,"PCM bytes"):
            assemble(self.source,self.root/"retained",master=master,timing=timing)

    def test_second_topic_and_multiscene(self):
        # An invented parcel process uses the same renderer, without networking-specific functions.
        p=copy.deepcopy(self.project);p["title"]="An illustrative parcel process";p["example_notice"]="Invented teaching example"
        s=p["scenes"][0];s["title"]="Arrival, waiting, release, dispatch"
        texts=["A parcel enters a holding area. ","The loading bay is occupied. ","The bay sends permission to proceed. ","The parcel moves to loading, so waiting count falls."]
        for c,text in zip(s["clauses"],texts):c["text"]=text
        s["narration"]="".join(texts)
        labels={"source":"Reception","waiting":"Holding area","worker":"Loading bay","job":"Parcel A","incoming":"Parcel","outgoing":"Parcel","control":"Permission"}
        for e in s["elements"]:
            e["label"]=labels[e["id"]]
            if e.get("state"):e["state"]="Waiting" if e["kind"]=="queue" else "Busy"
        for e in s["events"]:
            if e["kind"]=="state":e["value"]="Ready" if e["id"]=="grant-state" else "Loading"
            for gate in e.get("requires",[]):gate["state"]="Ready"
        s2=copy.deepcopy(s);s2["id"]="parcel-repeat";p["scenes"].append(s2)
        write_json(self.source,p);tl=assemble(self.source,self.root/"parcels",preview=True)
        self.assertEqual(len(tl["scenes"]),2)
        self.assertEqual(tl["scenes"][1]["start"],tl["scenes"][0]["end"])
        Renderer(tl).frame(tl["scenes"][1]["start"]+9.8)


if __name__=="__main__":unittest.main(verbosity=2)
