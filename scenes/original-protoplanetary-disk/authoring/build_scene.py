import bpy, math, random, json, os
from mathutils import Vector, noise
from pathlib import Path
D=Path(__import__("os").environ["SCENE_OUTPUT"])
random.seed(46109)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=False;s.cycles.max_bounces=6
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.025,.032,.045,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.17
# Actual warped volumetric-thickness geometry, no imported images.
N=640;R=180;verts=[];faces=[]
for side in [1,-1]:
 for j in range(R):
  rr=.12+6.3*(j/(R-1))**1.3
  for i in range(N):
   a=i/N*2*math.pi
   edge=1+.04*math.sin(a*3+.3)+.025*math.sin(a*7+2)
   r=rr*edge
   q=noise.noise_vector(Vector((r*math.cos(a)*.75,r*math.sin(a)*.75,.8)))
   z=side*(.025+.18*(r/6)**1.3)*(1+.3*q.z)+.07*math.sin(a*2+r*.4)*(r/6)**1.2
   z+=.012*math.sin(a*9-r*4)+.007*q.x
   verts.append((r*math.cos(a),r*math.sin(a),z))
 for j in range(R-1):
  for i in range(N):
   k=(i+1)%N;off=0 if side==1 else R*N
   f=(off+j*N+i,off+j*N+k,off+(j+1)*N+k,off+(j+1)*N+i)
   faces.append(f if side==1 else f[::-1])
for i in range(N):
 k=(i+1)%N
 faces.append(((R-1)*N+i,(R-1)*N+k,(2*R-1)*N+k,(2*R-1)*N+i))
mesh=bpy.data.meshes.new('warped disk topology');mesh.from_pydata(verts,[],faces);mesh.update();disk=bpy.data.objects.new('continuous irregular gas and dust disk',mesh);s.collection.objects.link(disk)
for p in mesh.polygons:p.use_smooth=True
m=bpy.data.materials.new('turbulent dusty filament surface');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
out=n.new('ShaderNodeOutputMaterial');p=n.new('ShaderNodeBsdfPrincipled');l.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Roughness'].default_value=.95
tex=n.new('ShaderNodeTexCoord');pos=tex.outputs['Object']
def mathn(op,a,b=None):
 q=n.new('ShaderNodeMath');q.operation=op
 if hasattr(a,'bl_idname'):l.new(a,q.inputs[0])
 else:q.inputs[0].default_value=a
 if b is not None:
  if hasattr(b,'bl_idname'):l.new(b,q.inputs[1])
  else:q.inputs[1].default_value=b
 return q.outputs[0]
length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';l.new(pos,length.inputs[0]);rad=length.outputs['Value']
rot=n.new('ShaderNodeVectorRotate');rot.rotation_type='AXIS_ANGLE';rot.inputs['Axis'].default_value=(0,0,1);l.new(pos,rot.inputs['Vector']);l.new(mathn('MULTIPLY',rad,1.8),rot.inputs['Angle'])
scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1,4,2);l.new(rot.outputs[0],scale.inputs[0])
noise1=n.new('ShaderNodeTexNoise');noise1.inputs['Scale'].default_value=2.3;noise1.inputs['Detail'].default_value=5;noise1.inputs['Roughness'].default_value=.78;l.new(scale.outputs[0],noise1.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1]);
for ix,(v,c) in enumerate([(.22,(.018,.012,.009,1)),(.40,(.072,.052,.038,1)),(.52,(.20,.15,.108,1)),(.66,(.42,.34,.25,1)),(.8,(.57,.50,.40,1))]):
 e=ramp.color_ramp.elements[0] if ix==0 else ramp.color_ramp.elements.new(v);e.position=v;e.color=c
l.new(noise1.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=110;fine.inputs['Detail'].default_value=3;l.new(pos,fine.inputs['Vector'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.45;bump.inputs['Distance'].default_value=.022;l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
heat=mathn('DIVIDE',.065,mathn('POWER',mathn('ADD',rad,.1),2));l.new(heat,p.inputs['Emission Strength']);p.inputs['Emission Color'].default_value=(1,.39,.10,1)
disk.data.materials.append(m)
# Broken, lifted fine filaments add genuine occlusion and parallax above the surface.
def mat(name,color,em=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=1;p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=em;return m
filamentmats=[mat('dust filament '+str(i),c) for i,c in enumerate([(.10,.071,.05),(.24,.18,.13),(.38,.30,.22)])]
for k in range(210):
 r0=random.uniform(.35,6);a0=random.uniform(0,math.tau);span=random.uniform(.09,.65)
 cu=bpy.data.curves.new('broken turbulent filament','CURVE');cu.dimensions='3D';cu.resolution_u=2;cu.bevel_depth=random.uniform(.004,.015);cu.bevel_resolution=1;sp=cu.splines.new('POLY');sp.points.add(31)
 for j,pt in enumerate(sp.points):
  t=j/31;a=a0+span*t;r=r0+.16*math.sin(t*2+a0)+.10*t
  z=.05+.18*(r/6)**1.3+.07*math.sin(a*2+r*.4)*(r/6)**1.2+.02*math.sin(t*9+k)
  pt.co=(r*math.cos(a),r*math.sin(a),z,1);pt.radius=math.sin(math.pi*t)**.6+.03
 ob=bpy.data.objects.new('lifted dusty thread %03d'%k,cu);s.collection.objects.link(ob);ob.data.materials.append(random.choice(filamentmats))
# Central young luminous object: modest size, no black hole or planet population.
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=.105,location=(0,0,.09));star=bpy.context.object;star.name='forming protostar';star.data.materials.append(mat('soft ivory stellar emission',(1,.77,.48),28))
for p in star.data.polygons:p.use_smooth=True
bpy.ops.object.light_add(type='POINT',location=(0,0,.35));bpy.context.object.name='central warm illumination';bpy.context.object.data.energy=105;bpy.context.object.data.color=(1,.69,.40);bpy.context.object.data.shadow_soft_size=.16
for name,loc,power,size,color in [('soft neutral upper fill',(-3,-4,8),1550,9,(.83,.89,1)),('far-side warm rim',(1,5,3),1400,7,(1,.77,.52))]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
# Sparse actual background star geometry, fixed seed.
starmats=[mat('background stars '+str(i),(.38,.43,.52),i) for i in [1,2,4]]
for k in range(150):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=random.uniform(.003,.014),location=(random.uniform(-18,18),random.uniform(8,15),random.uniform(-7,12)));bpy.context.object.data.materials.append(random.choice(starmats))
bpy.ops.object.camera_add(location=(9,-13,8.4));cam=bpy.context.object;cam.name='hero observer';cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=43;cam.data.shift_x=.025;cam.data.shift_y=.025;s.camera=cam
# A restrained optical bloom, no streaks or flare art.
s.use_nodes=True;n=s.node_tree.nodes;n.clear();l=s.node_tree.links;rl=n.new('CompositorNodeRLayers');gl=n.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.quality='HIGH';gl.threshold=2;gl.size=7;gl.mix=-.92;out=n.new('CompositorNodeComposite');l.new(rl.outputs['Image'],gl.inputs['Image']);l.new(gl.outputs['Image'],out.inputs['Image'])
s.render.filepath=str(D/'disk-preview.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'original-disk.blend'));(__import__("os").environ.get("SCENE_STAGE_RENDERS") == "1") and bpy.ops.render.render(write_still=True)
