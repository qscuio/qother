import bpy,json,time,hashlib,sys,argparse
from pathlib import Path
parser=argparse.ArgumentParser(description='Three isolated Cycles performance settings; does not save or alter the input blend.')
parser.add_argument('--scene',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=args.scene.resolve();D=args.output.resolve()
if D.exists() and any(D.iterdir()):raise RuntimeError('Output directory must be empty; refusing to overwrite prior evidence.')
D.mkdir(parents=True,exist_ok=True)
configs=[('A-step1.6',1.6,256,64,.02),('B-step3.2',3.2,256,64,.02),('C-step1.6-s128',1.6,128,32,.03)]
results=[]
for name,step,samples,min_samples,threshold in configs:
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
 baseline={k:getattr(s.cycles,k) for k in ['samples','adaptive_min_samples','adaptive_threshold','volume_step_rate','volume_max_steps','max_bounces','volume_bounces','use_denoising']}
 s.cycles.samples=samples;s.cycles.adaptive_min_samples=min_samples;s.cycles.adaptive_threshold=threshold;s.cycles.volume_step_rate=step;s.cycles.seed=46109;s.cycles.use_animated_seed=False
 s.render.filepath=str(D/(name+'.png'))
 t=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-t
 results.append(dict(name=name,seconds=elapsed,baseline_saved_scene=baseline,changes=dict(volume_step_rate=step,samples=samples,adaptive_min_samples=min_samples,adaptive_threshold=threshold),camera_location=list(s.camera.location),camera_rotation=list(s.camera.rotation_euler),resolution=[1280,720],source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
 (D/'timings.json').write_text(json.dumps(results,indent=2));print('PILOT_DONE',name,elapsed,flush=True)
