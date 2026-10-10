import bpy, math
from mathutils import Vector
from pathlib import Path
D=Path(__import__("os").environ["SCENE_OUTPUT"]);bpy.ops.wm.open_mainfile(filepath=str(D/'original-disk-v2.blend'));s=bpy.context.scene
ob=bpy.data.objects['continuous irregular gas and dust disk'];m=ob.data.materials[0];n=m.node_tree.nodes;l=m.node_tree.links;v=n.get('Principled Volume');pos=n.get('Texture Coordinate').outputs['Object']
for node in n:
 if node.bl_idname=='ShaderNodeMath' and node.operation=='MULTIPLY' and node.inputs[1].default_value==.75:node.inputs[1].default_value=.23
 # actual exact float comparison protected below
 if node.bl_idname=='ShaderNodeVectorRotate':
  q=node.inputs['Angle'].links[0].from_node;q.inputs[1].default_value=.27
 if node.bl_idname=='ShaderNodeVectorMath' and node.operation=='MULTIPLY':node.inputs[1].default_value=(1,2.1,3)
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.2;noise.inputs['Detail'].default_value=5;noise.inputs['Roughness'].default_value=.7;l.new(pos,noise.inputs['Vector'])
r=n.new('ShaderNodeMapRange');r.clamp=True;r.inputs['From Min'].default_value=.30;r.inputs['From Max'].default_value=.68;r.inputs['To Min'].default_value=.01;r.inputs['To Max'].default_value=1.2;l.new(noise.outputs['Fac'],r.inputs['Value'])
prev=v.inputs['Density'].links[0].from_socket;q=n.new('ShaderNodeMath');q.operation='MULTIPLY';l.new(prev,q.inputs[0]);l.new(r.outputs[0],q.inputs[1]);l.new(q.outputs[0],v.inputs['Density'])
# Limit self-light to inner warm dust; outer dust appears mainly by scattering.
length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';l.new(pos,length.inputs[0]);rad=length.outputs['Value']
heat=n.new('ShaderNodeMapRange');heat.clamp=True;heat.inputs['From Min'].default_value=.1;heat.inputs['From Max'].default_value=2.1;heat.inputs['To Min'].default_value=.20;heat.inputs['To Max'].default_value=.003;l.new(rad,heat.inputs['Value'])
q2=n.new('ShaderNodeMath');q2.operation='MULTIPLY';l.new(q.outputs[0],q2.inputs[0]);l.new(heat.outputs[0],q2.inputs[1]);l.new(q2.outputs[0],v.inputs['Emission Strength']);v.inputs['Emission Color'].default_value=(1,.57,.25,1)
bpy.data.objects['central warm illumination'].data.energy=500;bpy.data.objects['soft neutral upper fill'].data.energy=500;bpy.data.objects['far-side warm rim'].data.energy=700
for vert in ob.data.vertices:vert.co.z*=1.8
s.camera.location=(9,-13,7.2);s.camera.rotation_euler=(-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.rotation_euler.rotate_axis('Z',-.16);s.camera.data.lens=39;s.camera.data.shift_y=.015
s.cycles.samples=128;s.render.filepath=str(D/'disk-v3-preview.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'original-disk-v3.blend'));(__import__("os").environ.get("SCENE_STAGE_RENDERS") == "1") and bpy.ops.render.render(write_still=True)
