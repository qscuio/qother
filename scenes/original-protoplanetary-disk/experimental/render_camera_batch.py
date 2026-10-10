"""Bounded 48-frame true-3D camera test. No object evolution or frame interpolation."""
import bpy, math, time, json, shutil, hashlib
from pathlib import Path
D=Path(__import__("os").environ["SCENE_OUTPUT"]);O=D/'camera-motion-48';F=O/'frames';F.mkdir(parents=True,exist_ok=False)
source=D/'H10-original-disk.blend';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;c=s.camera
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.cycles.samples=256;s.cycles.adaptive_min_samples=64;s.cycles.seed=46109;s.cycles.use_animated_seed=False
s.render.fps=24;s.frame_start=1;s.frame_end=48
radius=math.hypot(c.location.x,c.location.y);start=math.atan2(c.location.y,c.location.x);height=c.location.z
for frame in range(1,49):
 t=(frame-1)/47;u=t*t*(3-2*t);angle=start+math.radians(15)*u;c.location=(radius*math.cos(angle),radius*math.sin(angle),height);c.rotation_euler=(-c.location).to_track_quat('-Z','Y').to_euler();c.rotation_euler.rotate_axis('Z',-.16);c.keyframe_insert(data_path='location',frame=frame);c.keyframe_insert(data_path='rotation_euler',frame=frame)
s.frame_set(1);s.render.filepath=str(F/'frame-');bpy.ops.wm.save_as_mainfile(filepath=str(O/'H10-camera-orbit-test.blend'))
status={'purpose':'Two-second actual 3D camera demonstration; not a physical evolution or final science clip','world_state':'unchanged','frame_count':48,'fps':24,'duration_seconds':2,'orbit_degrees':15,'resolution':[1280,720],'samples_max':256,'samples_min':64,'denoising':False,'frame_interpolation':False,'seed':46109,'source_blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reused_actual_benchmark_frames':[],'started_unix':time.time(),'renders':[],'status':'running'}
for frame in range(1,49):
 path=F/('frame-%03d.png'%frame)
 if path.exists():continue
 s.frame_set(frame);s.render.filepath=str(path);a=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-a
 status['renders'].append({'frame':frame,'seconds':elapsed,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});status['completed_frames']=len(list(F.glob('frame-*.png')));(O/'status.json').write_text(json.dumps(status,indent=2));print('COMPLETED_FRAME',frame,'SECONDS',elapsed,'TOTAL',status['completed_frames'],flush=True)
status['status']='rendered';status['finished_unix']=time.time();status['completed_frames']=len(list(F.glob('frame-*.png')));(O/'status.json').write_text(json.dumps(status,indent=2));print('ALL_48_ACTUAL_FRAMES_RENDERED',flush=True)
