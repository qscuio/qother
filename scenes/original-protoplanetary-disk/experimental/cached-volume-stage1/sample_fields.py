"""Evaluate canonical Blender material fields, without reimplementing procedural noise."""
import bpy, numpy as np, time, json, sys, hashlib, bmesh, argparse, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
parser=argparse.ArgumentParser(description='Stage 1 only: sample authored fields; no full bake or scene render.')
parser.add_argument('--scene',type=Path,required=True,help='Canonical H10-original-disk.blend produced by the existing pipeline')
parser.add_argument('--output',type=Path,required=True,help='New directory for diagnostic results')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
SOURCE=args.scene.resolve();D=args.output.resolve()
if not SOURCE.is_file():parser.error('--scene must exist')
D.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
# Derive the existing camera-only test path in memory, without rendering or saving it.
# Static geometry and shader graphs remain unchanged; metadata records derived poses.
s.camera=bpy.data.objects['hero observer'];c=s.camera
c.animation_data_clear();c.location=(9,-13,7.2)
radius=math.hypot(c.location.x,c.location.y);start=math.atan2(c.location.y,c.location.x);height=c.location.z
for frame in range(1,49):
 t=(frame-1)/47;u=t*t*(3-2*t);angle=start+math.radians(15)*u;c.location=(radius*math.cos(angle),radius*math.sin(angle),height);c.rotation_euler=(-c.location).to_track_quat('-Z','Y').to_euler();c.rotation_euler.rotate_axis('Z',-.16);c.keyframe_insert(data_path='location',frame=frame);c.keyframe_insert(data_path='rotation_euler',frame=frame)
s.frame_set(1)
ob=bpy.data.objects['continuous irregular gas and dust disk'];mat=ob.data.materials[0];vol=mat.node_tree.nodes.get('Principled Volume')
ng=bpy.data.node_groups.new('canonical fields evaluated on sample vertices','GeometryNodeTree')
ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
n=ng.nodes;l=ng.links;inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');pos=n.new('GeometryNodeInputPosition');mapping={}
def clone(old):
 if old.name in mapping:return mapping[old.name]
 if old.bl_idname=='ShaderNodeTexCoord':mapping[old.name]=pos;return pos
 new=n.new(old.bl_idname);mapping[old.name]=new;new.name=old.name
 for prop in old.bl_rna.properties:
  k=prop.identifier
  if k in {'name','location','parent','select','dimensions','width','height','label','rna_type','type','bl_idname','bl_label','bl_description','bl_icon','bl_static_type'} or prop.is_readonly:continue
  if prop.type in {'BOOLEAN','INT','FLOAT','STRING','ENUM'}:
   try:setattr(new,k,getattr(old,k))
   except (AttributeError,TypeError):pass
 if old.bl_idname=='ShaderNodeValToRGB':
  a=old.color_ramp;b=new.color_ramp;b.interpolation=a.interpolation;b.color_mode=a.color_mode;b.hue_interpolation=a.hue_interpolation
  while len(b.elements)>1:b.elements.remove(b.elements[-1])
  for i,e in enumerate(a.elements):
   q=b.elements[0] if i==0 else b.elements.new(e.position);q.position=e.position;q.color=e.color
 for i,a in enumerate(old.inputs):
  if hasattr(a,'default_value'):
   try:new.inputs[i].default_value=a.default_value
   except (AttributeError,TypeError):pass
  if a.is_linked:
   link=a.links[0];src=clone(link.from_node);oi=0 if link.from_node.bl_idname=='ShaderNodeTexCoord' else list(link.from_node.outputs).index(link.from_socket);l.new(src.outputs[oi],new.inputs[i])
 return new
geom=inp.outputs['Geometry']
for name,socket,dtype in [('density','Density','FLOAT'),('emission','Emission Strength','FLOAT'),('color','Color','FLOAT_COLOR')]:
 st=n.new('GeometryNodeStoreNamedAttribute');st.data_type=dtype;st.domain='POINT';st.inputs['Name'].default_value=name;l.new(geom,st.inputs['Geometry']);geom=st.outputs['Geometry'];link=vol.inputs[socket].links[0];node=clone(link.from_node);l.new(node.outputs[list(link.from_node.outputs).index(link.from_socket)],st.inputs['Value'])
l.new(geom,out.inputs['Geometry'])
mesh=bpy.data.meshes.new('field sample positions');sample=bpy.data.objects.new('temporary samples',mesh);s.collection.objects.link(sample);sample.matrix_world=ob.matrix_world.copy();mod=sample.modifiers.new('canonical field sampler','NODES');mod.node_group=ng

def evaluate(points):
 mesh.clear_geometry();mesh.vertices.add(len(points));mesh.vertices.foreach_set('co',np.asarray(points,dtype=np.float32).ravel());mesh.update();bpy.context.view_layer.update();evaluated=sample.evaluated_get(bpy.context.evaluated_depsgraph_get());me=evaluated.to_mesh();res={}
 for key,width,prop in [('density',1,'value'),('emission',1,'value'),('color',4,'color')]:
  arr=np.empty(len(points)*width,np.float32);me.attributes[key].data.foreach_get(prop,arr);res[key]=arr.reshape(-1,width) if width>1 else arr
 evaluated.to_mesh_clear();return res

verts=np.array([v.co[:] for v in ob.data.vertices]);lo=verts.min(axis=0)-.015;hi=verts.max(axis=0)+.015
bm=bmesh.new();bm.from_mesh(ob.data);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free();bvh=BVHTree.FromObject(ob,bpy.context.evaluated_depsgraph_get())

def columns(xs,ys):
 lows=np.full((len(ys),len(xs)),np.nan,np.float32);highs=lows.copy();counts=np.zeros_like(lows,dtype=np.int32)
 for j,y in enumerate(ys):
  for i,x in enumerate(xs):
   start=Vector((float(x),float(y),float(lo[2]-1)));hits=[]
   for _ in range(8):
    loc,norm,idx,dist=bvh.ray_cast(start,Vector((0,0,1)),float(hi[2]-lo[2]+2))
    if loc is None:break
    hits.append(loc.z);start=loc+Vector((0,0,1e-5))
   counts[j,i]=len(hits)
   if len(hits)==2:lows[j,i],highs[j,i]=hits
 return lows,highs,counts

meta={'source_file':SOURCE.name,'camera_metadata':'Derived existing 15-degree camera-only path; no image render or physical evolution','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'bounds':[lo.tolist(),hi.tolist()],'object_matrix':list(map(list,ob.matrix_world)),'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'material_nodes_copied':list(mapping),'anisotropy':vol.inputs['Anisotropy'].default_value,'emission_color':list(vol.inputs['Emission Color'].default_value)[:3],'cameras':{},'lights':[],'background_stars':[],'world_color':[.025*.17,.032*.17,.045*.17]}
for frame in [1,25,48]:
 s.frame_set(frame);meta['cameras'][str(frame)]={'matrix_world':list(map(list,s.camera.matrix_world)),'view_frame':[list(v) for v in s.camera.data.view_frame(scene=s)],'position':list(s.camera.location)}
for o in s.objects:
 if o.hide_render:continue
 if o.type=='LIGHT':meta['lights'].append({'name':o.name,'position':list(o.location),'color':list(o.data.color),'energy':o.data.energy,'type':o.data.type,'size':o.data.size if o.data.type=='AREA' else o.data.shadow_soft_size,'matrix_world':list(map(list,o.matrix_world))})
 if o.name=='forming protostar':meta['protostar']={'position':list(o.location),'radius':.105*float(o.scale[0]),'emission':[28,28*.77,28*.48]}
 if o.type=='MESH' and o.name.startswith('Icosphere'):
  p=o.data.materials[0].node_tree.nodes.get('Principled BSDF');meta['background_stars'].append({'position':list(o.location),'radius':max(v.co.length for v in o.data.vertices),'emission':[v*p.inputs['Emission Strength'].default_value for v in p.inputs['Emission Color'].default_value[:3]]})
(D/'metadata.json').write_text(json.dumps(meta,indent=2))
points=np.random.default_rng(46109).uniform(lo,hi,(2048,3)).astype(np.float32);a=evaluate(points);b=evaluate(points)
low,high,counts=columns(np.linspace(lo[0],hi[0],64),np.linspace(lo[1],hi[1],64))
report={'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'column_crossing_histogram':{str(x):int((counts==x).sum()) for x in np.unique(counts)},'repeat_max_error':{k:float(np.max(abs(a[k]-b[k]))) for k in a},'density_range':[float(a['density'].min()),float(a['density'].max())],'color_range':[float(a['color'].min()),float(a['color'].max())],'independent_emission_density_correlation':float(np.corrcoef(a['density'],a['emission'])[0,1]),'fine_noise':{'scale':mat.node_tree.nodes['resolved dusty substructure'].inputs['Scale'].default_value,'detail':mat.node_tree.nodes['resolved dusty substructure'].inputs['Detail'].default_value}}
np.savez(D/'probe.npz',points=points,**a);(D/'probe.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
