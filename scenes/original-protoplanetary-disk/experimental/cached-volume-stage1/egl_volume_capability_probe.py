import ctypes as C, ctypes.util, os, json
os.environ.setdefault('MESA_SHADER_CACHE_DISABLE','true')
E=C.CDLL(ctypes.util.find_library('EGL'))
def e(name,rest,args):
 f=getattr(E,name);f.restype=rest;f.argtypes=args;return f
p=e('eglGetProcAddress',C.c_void_p,[C.c_char_p])
def gl(name,rest,*args):return C.CFUNCTYPE(rest,*args)(p(name.encode()))
f=C.CFUNCTYPE(C.c_void_p,C.c_uint,C.c_void_p,C.POINTER(C.c_int))(p(b'eglGetPlatformDisplayEXT'))
d=f(0x31DD,None,None);a=C.c_int();b=C.c_int();assert e('eglInitialize',C.c_uint,[C.c_void_p,C.POINTER(C.c_int),C.POINTER(C.c_int)])(d,C.byref(a),C.byref(b))
assert e('eglBindAPI',C.c_uint,[C.c_uint])(0x30A2)
attrs=(C.c_int*13)(0x3033,1,0x3040,8,0x3024,8,0x3023,8,0x3022,8,0x3021,8,0x3038);cfg=C.c_void_p();n=C.c_int();assert e('eglChooseConfig',C.c_uint,[C.c_void_p,C.POINTER(C.c_int),C.POINTER(C.c_void_p),C.c_int,C.POINTER(C.c_int)])(d,attrs,C.byref(cfg),1,C.byref(n)) and n.value
s=e('eglCreatePbufferSurface',C.c_void_p,[C.c_void_p,C.c_void_p,C.POINTER(C.c_int)])(d,cfg,(C.c_int*5)(0x3057,16,0x3056,16,0x3038))
c=e('eglCreateContext',C.c_void_p,[C.c_void_p,C.c_void_p,C.c_void_p,C.POINTER(C.c_int)])(d,cfg,None,(C.c_int*1)(0x3038));assert e('eglMakeCurrent',C.c_uint,[C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p])(d,s,s,c)
get=gl('glGetString',C.c_char_p,C.c_uint);report={label:get(key).decode() for label,key in [('vendor',0x1F00),('renderer',0x1F01),('version',0x1F02),('glsl',0x8B8C)]}
def shader(kind,src):
 sh=gl('glCreateShader',C.c_uint,C.c_uint)(kind);st=C.c_char_p(src.encode());gl('glShaderSource',None,C.c_uint,C.c_int,C.POINTER(C.c_char_p),C.c_void_p)(sh,1,C.byref(st),None);gl('glCompileShader',None,C.c_uint)(sh);ok=C.c_int();gl('glGetShaderiv',None,C.c_uint,C.c_uint,C.POINTER(C.c_int))(sh,0x8B81,C.byref(ok));assert ok.value,'shader compilation failed';return sh
vs=shader(0x8B31,'#version 330\nvoid main(){vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2);gl_Position=vec4(p*2.0-1.0,0,1);}')
fs=shader(0x8B30,'#version 330\nuniform sampler3D density;out vec4 color;void main(){float d=texture(density,vec3(0.5)).r;color=vec4(d,d*0.5,0.75,1);}')
prog=gl('glCreateProgram',C.c_uint)();attach=gl('glAttachShader',None,C.c_uint,C.c_uint);attach(prog,vs);attach(prog,fs);gl('glLinkProgram',None,C.c_uint)(prog);ok=C.c_int();gl('glGetProgramiv',None,C.c_uint,C.c_uint,C.POINTER(C.c_int))(prog,0x8B82,C.byref(ok));assert ok.value
tex=C.c_uint();gl('glGenTextures',None,C.c_int,C.POINTER(C.c_uint))(1,C.byref(tex));gl('glBindTexture',None,C.c_uint,C.c_uint)(0x806F,tex)
param=gl('glTexParameteri',None,C.c_uint,C.c_uint,C.c_int)
for key in [0x2801,0x2800]:param(0x806F,key,0x2601)
data=(C.c_float*8)(*([0.5]*8));gl('glTexImage3D',None,C.c_uint,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint,C.c_uint,C.c_void_p)(0x806F,0,0x822E,2,2,2,0,0x1903,0x1406,data)
gl('glUseProgram',None,C.c_uint)(prog);gl('glViewport',None,C.c_int,C.c_int,C.c_int,C.c_int)(0,0,16,16);gl('glDrawArrays',None,C.c_uint,C.c_int,C.c_int)(4,0,3)
pixel=(C.c_ubyte*4)();gl('glReadPixels',None,C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint,C.c_uint,C.c_void_p)(8,8,1,1,0x1908,0x1401,pixel);report['sampled_3d_texture_pixel']=list(pixel);report['expected_pixel']=[128,64,191,255];report['gl_error']=gl('glGetError',C.c_uint)();report['passed']=all(abs(x-y)<=1 for x,y in zip(pixel,report['expected_pixel'])) and report['gl_error']==0
print(json.dumps(report,indent=2));assert report['passed']
