import bpy, math, json, random
from mathutils import Vector
from pathlib import Path
D=Path(__import__("os").environ["SCENE_OUTPUT"]);bpy.ops.wm.open_mainfile(filepath=str(D/'original-disk-v3.blend'));s=bpy.context.scene
ob=bpy.data.objects['continuous irregular gas and dust disk'];m=ob.data.materials[0];n=m.node_tree.nodes;l=m.node_tree.links;v=n.get('Principled Volume');pos=n.get('Texture Coordinate').outputs['Object']
# Fine three-dimensional dusty substructure, no image texture.
noise=n.new('ShaderNodeTexNoise');noise.name='resolved dusty substructure';noise.inputs['Scale'].default_value=6;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.8;l.new(pos,noise.inputs['Vector'])
r=n.new('ShaderNodeMapRange');r.clamp=True;r.inputs['From Min'].default_value=.28;r.inputs['From Max'].default_value=.72;r.inputs['To Min'].default_value=.35;r.inputs['To Max'].default_value=1.4;l.new(noise.outputs['Fac'],r.inputs['Value'])
prev=v.inputs['Density'].links[0].from_socket;q=n.new('ShaderNodeMath');q.operation='MULTIPLY';l.new(prev,q.inputs[0]);l.new(r.outputs[0],q.inputs[1]);l.new(q.outputs[0],v.inputs['Density'])
# Slight material variation between denser ash-gray dust and warm illuminated dust.
color=n.new('ShaderNodeValToRGB');color.color_ramp.elements[0].position=.25;color.color_ramp.elements[0].color=(.24,.22,.20,1);color.color_ramp.elements[1].position=.78;color.color_ramp.elements[1].color=(.48,.34,.21,1);l.new(noise.outputs['Fac'],color.inputs[0]);l.new(color.outputs[0],v.inputs['Color'])
# Broader transparent lanes separate foreground dust from the far side.
for node in n:
 if node.bl_idname=='ShaderNodeMapRange' and abs(node.inputs['To Max'].default_value-1.2)<.001:
  node.inputs['From Min'].default_value=.36
  node.inputs['From Max'].default_value=.66
# Core has a small photosphere embedded within a soft luminous 3D envelope.
star=bpy.data.objects['forming protostar'];star.scale=(.4,.4,.4)
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=.22,location=star.location)
halo=bpy.context.object;halo.name='diffuse luminous protostellar envelope'
hm=bpy.data.materials.new('radially fading core envelope');hm.use_nodes=True;hn=hm.node_tree.nodes;hn.clear();hl=hm.node_tree.links
ho=hn.new('ShaderNodeOutputMaterial');hv=hn.new('ShaderNodeVolumePrincipled');hv.inputs['Color'].default_value=(.85,.64,.38,1);hv.inputs['Density'].default_value=.4;hv.inputs['Emission Color'].default_value=(1,.72,.40,1)
ht=hn.new('ShaderNodeTexCoord');hs=hn.new('ShaderNodeVectorMath');hs.operation='SUBTRACT';hs.inputs[1].default_value=(.5,.5,.5);hl.new(ht.outputs['Generated'],hs.inputs[0]);he=hn.new('ShaderNodeVectorMath');he.operation='LENGTH';hl.new(hs.outputs[0],he.inputs[0]);hf=hn.new('ShaderNodeMapRange');hf.clamp=True;hf.inputs['From Min'].default_value=0;hf.inputs['From Max'].default_value=.5;hf.inputs['To Min'].default_value=14;hf.inputs['To Max'].default_value=0;hl.new(he.outputs['Value'],hf.inputs['Value']);hl.new(hf.outputs[0],hv.inputs['Emission Strength']);hl.new(hv.outputs[0],ho.inputs['Volume']);halo.data.materials.append(hm)
halo.hide_render=True
s.node_tree.nodes.get('Glare').mix=0
s.node_tree.nodes.get('Glare').threshold=1
s.node_tree.nodes.get('Glare').size=8
s.cycles.samples=512;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.02;s.cycles.adaptive_min_samples=96;s.cycles.volume_step_rate=.4;s.cycles.seed=46109
s.render.resolution_percentage=100;s.render.filepath=str(D/'H10-original-disk-clean.png')
hero=s.camera
bpy.ops.object.camera_add(location=(-10,-10,5.3));alt=bpy.context.object;alt.name='independent side observer';alt.rotation_euler=(Vector((0,0,0))-alt.location).to_track_quat('-Z','Y').to_euler();alt.data.lens=35;alt.data.shift_y=.01
s.camera=hero
bpy.ops.wm.save_as_mainfile(filepath=str(D/'H10-original-disk.blend'))
settings={'scene':'H10 original protoplanetary disk static candidate','seed':46109,'blender':bpy.app.version_string,'geometry':'Closed warped disk volume plus central protostar and distant stellar mesh points; all self-authored procedural geometry and shaders','external_bitmaps_in_scene':len([im for im in bpy.data.images if im.source=='FILE']),'world_state':'identical in both camera views','simulation':False,'scale':'not calibrated; illustrative, not to scale','dynamics':'none; no collapse or rotation simulation claimed','camera_views':{},'samples':512,'adaptive_threshold':.02}
for c in [hero,alt]:settings['camera_views'][c.name]={'location':list(c.location),'rotation_euler':list(c.rotation_euler),'lens_mm':c.data.lens,'shift_x':c.data.shift_x,'shift_y':c.data.shift_y}
(D/'settings.json').write_text(json.dumps(settings,indent=2))
(__import__("os").environ.get("SCENE_STAGE_RENDERS") == "1") and bpy.ops.render.render(write_still=True)
s.camera=alt;s.render.resolution_percentage=60;s.cycles.samples=256;s.render.filepath=str(D/'H10-original-disk-second-view.png');(__import__("os").environ.get("SCENE_STAGE_RENDERS") == "1") and bpy.ops.render.render(write_still=True)
