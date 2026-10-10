#include <cmath>
#include <algorithm>
#include <omp.h>
#include <vector>
static std::vector<double> cache;static int cw=0,ch=0;
static inline double cl(double v,double a,double b){return std::max(a,std::min(v,b));}
static inline float sample(const float *n,double x,double y,double z){
 double a[3]={std::fmod(z*13+44+9600,96),std::fmod(y*13+40+9600,96),std::fmod(x*13+46+9600,96)};
 int i[3];double f[3];for(int k=0;k<3;k++){if(a[k]>95)a[k]-=95;i[k]=int(a[k]);f[k]=a[k]-i[k];}
 double v=0;for(int dz=0;dz<2;dz++)for(int dy=0;dy<2;dy++)for(int dx=0;dx<2;dx++){
 int zi=std::min(95,i[0]+dz),yi=std::min(95,i[1]+dy),xi=std::min(95,i[2]+dx);
 v+=n[(zi*96+yi)*96+xi]*(dz?f[0]:1-f[0])*(dy?f[1]:1-f[1])*(dx?f[2]:1-f[2]);}
 return float(v);
}
extern "C" void galaxy_render(const float *noise,float *out,int w,int h,double phase,int history,double zoom,int threads){
 bool use_cache=history&&zoom==1;bool prepare=use_cache&&(cw!=w||ch!=h);
 if(prepare){cache.resize(size_t(w)*h*52*3);cw=w;ch=h;}
 double ca=std::cos(1.04),sa=std::sin(1.04),cb=std::cos(.35),sb=std::sin(.35);
 #pragma omp parallel for num_threads(threads) schedule(static)
 for(int iy=0;iy<h;iy++)for(int ix=0;ix<w;ix++){
 float X=(float(ix)/float(w)-float(.47))*float(10),Y=(float(iy)/float(h)-float(.52))*float(5.625);
 float c0=0,c1=0,c2=0,tr=1;
 for(int k=0;k<52;k++){
 double zz=-4.+8.*k/51.;double x=double(X)/zoom*(1+.035*zoom*zz),y=double(Y)/zoom*(1+.035*zoom*zz);
 double dy=y*ca+zz*sa,dz=-y*sa+zz*ca,rr=std::sqrt(x*x+dy*dy);float nf=(use_cache&&!prepare)?0:sample(noise,x,dy,dz);double n=nf;
 double e,bulge,baseabs;
 size_t ci=((size_t(iy)*w+ix)*52+k)*3;
 if(use_cache&&!prepare){e=cache[ci];bulge=cache[ci+1];baseabs=cache[ci+2];}
 else{
 double theta=std::atan2(dy,x),wave=2*theta-6*std::log(rr+.35)+double(float(nf*float(.38)));
 double sn=std::sin(wave),sn2=std::sin(wave+.23);
 double arm=std::exp(-sn*sn/.10)*(1-std::exp(-std::pow(rr/.75,3)));
 double dustarm=std::exp(-sn2*sn2/.055)*(1-std::exp(-std::pow(rr/.7,3)));
 double disk=std::exp(-rr/1.7)*std::exp(-std::pow(dz/.22,2))*double(cl(float(1+nf*float(.35)),.1,2))*std::exp(-std::pow(rr/3.4,8));
 double bx=x*cb+dy*sb,by=dy*cb-x*sb;
 bulge=std::exp(-(std::pow(bx/.43,2)+std::pow(by/1.3,2)+std::pow(dz/.32,2))*1.4);
 if(history)disk*=.6;
 double dust=disk*(double(float(cl(float(nf-float(.05)),0,2)*float(2.5)))+dustarm*8);
 e=disk*(.48+1.6*arm);baseabs=disk*.23+bulge*.17+dust;
 if(use_cache){cache[ci]=e;cache[ci+1]=bulge;cache[ci+2]=baseabs;}
 }
 double sat=0;
 if(history){double dx=2.5*(1-phase),ddy=.7*(1-phase);sat=.7*std::exp(-(std::pow((x-dx)/.8,2)+std::pow((dy-ddy)/.7,2)+std::pow((dz-.2)/.36,2))*1.6);bulge+=sat;}
 double alpha=1-std::exp(-(baseabs+sat*.17)*.23);
 c0=float(double(c0)+double(tr)*(e*.64+bulge*2.65)*.17);
 c1=float(double(c1)+double(tr)*(e*.76+bulge*1.77)*.17);
 c2=float(double(c2)+double(tr)*(e*1.09+bulge*.94)*.17);tr=float(double(tr)*(1-alpha));
 }
 auto p=(iy*w+ix)*3;out[p]=c0;out[p+1]=c1;out[p+2]=c2;
 }
}
