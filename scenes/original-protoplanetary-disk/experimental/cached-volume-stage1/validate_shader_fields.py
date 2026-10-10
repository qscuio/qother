"""Independent Cycles shader evaluation versus Geometry Nodes attribute field evaluation."""
from pathlib import Path
import sys
sampler=Path(__file__).with_name('sample_fields.py')
exec(compile(sampler.read_text(),str(sampler),'exec'))
# Explicit constant object-space samples on separated quads avoid AA/location ambiguity.
N=32;points=np.load(D/'probe.npz')['points'][:N*N];expected=evaluate(points)
for o in list(s.objects):o.hide_render=True
verts=[];faces=[]
for j in range(N):
 for i in range(N):
  k=len(verts);verts.extend([(i,j,0),(i+1,j,0),(i+1,j+1,0),(i,j+1,0)]);faces.append((k,k+1,k+2,k+3))
m=bpy.data.meshes.new('constant-coordinate shader validation quads');m.from_pydata(verts,[],faces);m.update();attribute=m.attributes.new('probe_position','FLOAT_VECTOR','POINT');attribute.data.foreach_set('vector',np.repeat(points,4,axis=0).ravel());o=bpy.data.objects.new('shader probe',m);s.collection.objects.link(o)
ma=mat.copy();ma.name='canonical material independent emission field test';m.materials.append(ma);nodes=ma.node_tree.nodes;links=ma.node_tree.links;attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='probe_position';tex=nodes.get('Texture Coordinate')
for link in list(tex.outputs['Object'].links):links.new(attr.outputs['Vector'],link.to_socket)
v=nodes.get('Principled Volume');combine=nodes.new('ShaderNodeCombineColor');combine.mode='RGB'
for index,socket in enumerate(['Density','Emission Strength']):links.new(v.inputs[socket].links[0].from_socket,combine.inputs[index])
sep=nodes.new('ShaderNodeSeparateColor');links.new(v.inputs['Color'].links[0].from_socket,sep.inputs['Color']);links.new(sep.outputs[0],combine.inputs[2]);emit=nodes.new('ShaderNodeEmission');links.new(combine.outputs[0],emit.inputs['Color']);out=nodes.get('Material Output')
for link in list(out.inputs['Volume'].links):links.remove(link)
links.new(emit.outputs[0],out.inputs['Surface'])
bpy.ops.object.camera_add(location=(N/2,N/2,10));c=bpy.context.object;c.rotation_euler=(0,0,0);c.data.type='ORTHO';c.data.ortho_scale=N;c.data.shift_x=0;c.data.shift_y=0;s.camera=c
s.render.resolution_x=N;s.render.resolution_y=N;s.render.resolution_percentage=100;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=False;s.cycles.filter_width=.01;s.use_nodes=False;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(D/'shader-probe.exr');bpy.ops.render.render(write_still=True)
im=bpy.data.images.load(str(D/'shader-probe.exr'),check_existing=False);actual=np.asarray(im.pixels[:]).reshape(-1,4)[:,:3];target=np.column_stack([expected['density'],expected['emission'],expected['color'][:,0]]);delta=abs(actual-target)
report={'method':'Cycles emission shader on constant-coordinate quads versus copied Geometry Nodes fields, 1024 random object-space positions','maximum_absolute_error_per_channel':delta.max(axis=0).tolist(),'mean_absolute_error_per_channel':delta.mean(axis=0).tolist(),'channels':['density','emission_strength','color_red'],'passed':bool(delta.max()<1e-4),'acceptance_rule':'Predeclared strict absolute max error < 1e-4; false remains a failure under this rule','samples':len(points),'cycles_samples':1}
report['maximum_relative_error_per_channel_nonzero']=np.max(np.divide(delta,abs(target),out=np.zeros_like(delta),where=abs(target)>0),axis=0).tolist()
report['posthoc_mixed_tolerance_diagnostic']={'rtol':1e-4,'atol':2e-5,'passed':bool(np.allclose(actual,target,rtol=1e-4,atol=2e-5)),'predeclared_acceptance':False}
(D/'shader-exactness.json').write_text(json.dumps(report,indent=2));np.savez(D/'shader-exactness.npz',actual=actual,expected=target);print('EXACTNESS',report,flush=True)
