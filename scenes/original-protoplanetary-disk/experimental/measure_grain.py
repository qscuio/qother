# Experimental: does not constitute animation or playback acceptance.
import bpy,time,json
from pathlib import Path
D=Path(__import__("os").environ["SCENE_OUTPUT"]);O=D/'motion-benchmark';O.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(D/'H10-original-disk.blend'));s=bpy.context.scene
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.cycles.samples=256;s.cycles.adaptive_min_samples=64;s.cycles.seed=46110
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.25;s.render.border_max_x=.75;s.render.border_min_y=.15;s.render.border_max_y=.65
s.render.filepath=str(O/'independent-seed-grain-crop.png');t=time.perf_counter();bpy.ops.render.render(write_still=True);(O/'grain-render-seconds.json').write_text(json.dumps({'seconds':time.perf_counter()-t,'seed':46110,'comparison_seed':46109,'purpose':'independent-seed Monte Carlo display-luminance noise estimate at identical camera and world state'}))
