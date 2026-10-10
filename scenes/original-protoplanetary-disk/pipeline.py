"""Run with system Python; Blender handles bpy authoring and rendering."""
import argparse, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True, help='New directory for generated files')
    p.add_argument('--blender', default='blender')
    p.add_argument('--threads', type=int, default=8)
    p.add_argument('--build-only', action='store_true')
    p.add_argument('--smoke', action='store_true', help='320x180 / 8 samples, technical test only')
    p.add_argument('--view', choices=['hero','side','both'], default='both')
    a = p.parse_args()
    if a.threads < 1: p.error('--threads must be positive')
    out = a.output.resolve()
    if out.exists() and any(out.iterdir()): p.error('--output must be new or empty; existing results are never overwritten')
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, SCENE_OUTPUT=str(out), SCENE_STAGE_RENDERS='0')
    for name in ['build_scene.py','refine_volume.py','refine_art.py','finalize_scene.py']:
        subprocess.run([a.blender,'-b','-t',str(a.threads),'--python-exit-code','1','--python',str(HERE/'authoring'/name)], env=env, check=True)
    if not a.build_only:
        cmd=[a.blender,'-b','-t',str(a.threads),'--python-exit-code','1','--python',str(HERE/'render.py'),'--','--output',str(out),'--view',a.view]
        if a.smoke: cmd.append('--smoke')
        subprocess.run(cmd, check=True)

if __name__ == '__main__': main()
