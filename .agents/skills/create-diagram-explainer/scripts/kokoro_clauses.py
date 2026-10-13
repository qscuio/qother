#!/usr/bin/env python3
"""Optional adapter for an existing local sherpa-onnx Kokoro v1.1 model."""
import argparse
import copy
import json
from pathlib import Path
from diagram import check_project, read_json, require, write_json, write_wav


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project",type=Path);ap.add_argument("--model",type=Path,required=True)
    ap.add_argument("--speaker-id",type=int,required=True);ap.add_argument("--speed",type=float,default=1.0)
    ap.add_argument("--threads",type=int,default=2);ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    p=read_json(args.project);check_project(p)
    require(args.speed>0 and args.threads>0 and args.speaker_id>=0,"Invalid voice/runtime parameters")
    m=args.model.resolve()
    for name in ["model.int8.onnx","voices.bin","tokens.txt","lexicon-us-en.txt","lexicon-zh.txt","espeak-ng-data"]:
        require((m/name).exists(),f"Required existing model asset missing: {name}")
    import numpy as np
    import sherpa_onnx
    config=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(m/"model.int8.onnx"),voices=str(m/"voices.bin"),tokens=str(m/"tokens.txt"),data_dir=str(m/"espeak-ng-data"),lexicon=f"{m/'lexicon-us-en.txt'},{m/'lexicon-zh.txt'}"),
        num_threads=args.threads,provider="cpu",debug=False),max_num_sentences=1)
    require(config.validate(),"Invalid local TTS configuration")
    tts=sherpa_onnx.OfflineTts(config)
    args.out.mkdir(parents=True,exist_ok=True)
    p=copy.deepcopy(p)
    if p.get("font"):p["font"]=str((args.project.resolve().parent/p["font"]).resolve())
    for si,s in enumerate(p["scenes"]):
        for ci,c in enumerate(s["clauses"]):
            audio=tts.generate(text=c.get("spoken_text",c["text"]),sid=args.speaker_id,speed=args.speed)
            a=np.asarray(audio.samples,dtype=np.float32)
            require(len(a)>0 and np.isfinite(a).all() and np.max(np.abs(a))>.001,"Invalid/silent speech output")
            require(np.max(np.abs(a))<1,"Clipped speech output; inspect provider settings")
            name=f"scene_{si+1:02}_clause_{ci+1:02}.wav"
            write_wav(args.out/name,(a*32767).round().astype("<i2").tobytes(),audio.sample_rate)
            c["wav"]=name
    p["audio_kind"]="narration"
    p["audio_provenance"]={"provider":"local sherpa-onnx","runtime_version":sherpa_onnx.__version__,"model_layout":"Kokoro multilingual v1.1","model_file":m.name,"speaker_id":args.speaker_id,"speed":args.speed,"synthetic":True,"voice_character":"Verify selected preset from exact model documentation and by listening"}
    write_json(args.out/"project.json",p)
    print(args.out/"project.json")


if __name__=="__main__":main()
