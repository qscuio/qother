import bpy, math
from pathlib import Path
D=Path(__import__("os").environ["SCENE_OUTPUT"])
bpy.ops.wm.open_mainfile(filepath=str(D/'original-disk.blend'))
s=bpy.context.scene
for o in bpy.data.objects:
 if o.name.startswith('lifted dusty'):o.hide_render=True
ob=bpy.data.objects['continuous irregular gas and dust disk']
import bmesh
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(ob.data);bm.free()
m=ob.data.materials[0];n=m.node_tree.nodes;l=m.node_tree.links
p=n.get('Principled BSDF');out=n.get('Material Output')
for link in list(out.inputs['Surface'].links):l.remove(link)
v=n.new('ShaderNodeVolumePrincipled');v.inputs['Color'].default_value=(.42,.34,.25,1);v.inputs['Anisotropy'].default_value=.35;l.new(v.outputs[0],out.inputs['Volume'])
tex=n.get('Texture Coordinate');pos=tex.outputs['Object'];noi=n.get('Noise Texture')
def mathn(op,a,b=None):
 q=n.new('ShaderNodeMath');q.operation=op
 if hasattr(a,'bl_idname'):l.new(a,q.inputs[0])
 else:q.inputs[0].default_value=a
 if b is not None:
  if hasattr(b,'bl_idname'):l.new(b,q.inputs[1])
  else:q.inputs[1].default_value=b
 return q.outputs[0]
# Break the continuous spiral into much broader asymmetric dusty clouds.
noi.inputs['Scale'].default_value=1.35
for node in n:
 if node.bl_idname=='ShaderNodeVectorMath' and node.operation=='MULTIPLY':node.inputs[1].default_value=(1,1.8,3)
for node in n:
 if node.bl_idname=='ShaderNodeMath' and node.operation=='MULTIPLY' and node.inputs[1].default_value==1.8:node.inputs[1].default_value=.75
length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';l.new(pos,length.inputs[0]);rad=length.outputs['Value']
fall=n.new('ShaderNodeMapRange');fall.clamp=True;fall.inputs['From Min'].default_value=4.4;fall.inputs['From Max'].default_value=6.4;fall.inputs['To Min'].default_value=1;fall.inputs['To Max'].default_value=0;l.new(rad,fall.inputs['Value'])
con=n.new('ShaderNodeMapRange');con.clamp=True;con.inputs['From Min'].default_value=.28;con.inputs['From Max'].default_value=.72;con.inputs['To Min'].default_value=.01;con.inputs['To Max'].default_value=1;l.new(noi.outputs['Fac'],con.inputs['Value'])
den=mathn('MULTIPLY',mathn('POWER',con.outputs[0],2.5),14);den=mathn('MULTIPLY',den,fall.outputs[0]);l.new(den,v.inputs['Density'])
v.inputs['Emission Color'].default_value=(.62,.36,.15,1);l.new(mathn('MULTIPLY',den,.018),v.inputs['Emission Strength'])
s.cycles.samples=64;s.cycles.volume_step_rate=.5
s.camera.location=(9,-13,9);s.camera.rotation_euler=(-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=38
bpy.data.objects['soft neutral upper fill'].data.energy=1100;bpy.data.objects['far-side warm rim'].data.energy=2000
s.render.filepath=str(D/'disk-volume-preview.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'original-disk-v2.blend'));(__import__("os").environ.get("SCENE_STAGE_RENDERS") == "1") and bpy.ops.render.render(write_still=True)
