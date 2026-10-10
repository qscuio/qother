"""Final-camera rendering; invoke through Blender with arguments after --."""
import argparse, hashlib, json, sys, time
from pathlib import Path
import bpy
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--view', choices=['hero','side','both'], default='both')
p.add_argument('--smoke', action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=a.output.resolve()
bpy.ops.wm.open_mainfile(filepath=str(out/'H10-original-disk.blend'))
s=bpy.context.scene
assert not [im for im in bpy.data.images if im.source=='FILE'], 'Unexpected external image'
assert s.cycles.seed==46109
assert bpy.data.objects['diffuse luminous protostellar envelope'].hide_render
assert len(bpy.data.objects['continuous irregular gas and dust disk'].data.vertices)==230400
reports=[]
for view in (['hero','side'] if a.view=='both' else [a.view]):
    s.camera=bpy.data.objects['hero observer' if view=='hero' else 'independent side observer']
    s.render.resolution_percentage=100 if view=='hero' else 60
    s.cycles.samples=512 if view=='hero' else 256
    if a.smoke:
        s.render.resolution_x=320;s.render.resolution_y=180;s.render.resolution_percentage=100
        s.cycles.samples=8;s.cycles.adaptive_min_samples=0
    name=('smoke-' if a.smoke else '')+('H10-original-disk-clean.png' if view=='hero' else 'H10-original-disk-second-view.png')
    target=out/name
    if target.exists(): raise FileExistsError(target)
    s.render.filepath=str(target)
    t=time.perf_counter();bpy.ops.render.render(write_still=True)
    reports.append({'view':view,'file':name,'seconds':time.perf_counter()-t,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'samples':s.cycles.samples,'seed':s.cycles.seed,'blender':bpy.app.version_string,'smoke':a.smoke,'camera_location':list(s.camera.location),'world_state':'unchanged','visual_quality':'not evaluated by this program'})
(out/('smoke-render-report.json' if a.smoke else 'render-report.json')).write_text(json.dumps(reports,indent=2)+'\n')
