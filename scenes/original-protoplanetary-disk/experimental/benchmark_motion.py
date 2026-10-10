# Experimental: does not constitute animation or playback acceptance.
import bpy, math, time, json
from pathlib import Path
from mathutils import Vector
D=Path(__import__("os").environ["SCENE_OUTPUT"]);O=D/'motion-benchmark';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(D/'H10-original-disk.blend'));s=bpy.context.scene;c=s.camera
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.cycles.samples=256;s.cycles.adaptive_min_samples=64
radius=math.hypot(c.location.x,c.location.y);start=math.atan2(c.location.y,c.location.x);height=c.location.z
results=[]
for frame in [1,25,48]:
 t=(frame-1)/47;u=t*t*(3-2*t);angle=start+math.radians(15)*u;c.location=(radius*math.cos(angle),radius*math.sin(angle),height);c.rotation_euler=(-c.location).to_track_quat('-Z','Y').to_euler();c.rotation_euler.rotate_axis('Z',-.16)
 s.render.filepath=str(O/('camera-test-%03d.png'%frame));a=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-a
 results.append({'frame':frame,'render_seconds':elapsed,'camera_location':list(c.location),'camera_rotation':list(c.rotation_euler),'world_state':'unchanged','path':s.render.filepath});(O/'timings.json').write_text(json.dumps(results,indent=2));print('BENCHMARK_FRAME',frame,'SECONDS',elapsed,flush=True)
(D/'motion-plan.json').write_text(json.dumps({'purpose':'Verify genuine 3D spatial parallax only, not formation dynamics','frames':48,'fps':24,'duration_seconds':2,'camera_orbit_degrees':15,'resolution':[1280,720],'cycles_samples_max':256,'samples_min':64,'seed':46109,'world_state':'identical static state throughout','timings':results,'batch_status':'not started'},indent=2))
