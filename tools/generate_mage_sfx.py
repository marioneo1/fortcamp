"""Reproducible local elemental SFX; standard-library stereo PCM, no API key."""
from pathlib import Path
from math import sin,pi,exp,sqrt
from random import Random
from array import array
import wave
SR=44100
OUT=Path(__file__).resolve().parents[1]/'frontend/public/assets/sfx'
def noise(n,lo,hi,seed):
 rng=Random(seed);a=1-exp(-2*pi*hi/SR);b=1-exp(-2*pi*lo/SR);low=bottom=0;out=[]
 for _ in range(n):
  low+=a*(rng.uniform(-1,1)-low);bottom+=b*(low-bottom);out.append(low-bottom)
 rms=sqrt(sum(v*v for v in out)/n) or 1
 return [v/rms for v in out]
def make(kind,length,seed):
 n=int(SR*length);high=noise(n,260 if kind=='lightning' else 900 if kind=='freeze' else 30 if kind=='gravity' else 80,2200 if kind=='lightning' else 2600 if kind=='freeze' else 400 if kind=='gravity' else 1800 if kind=='fireball' else 1300,seed)
 lows=noise(n,40,180,seed+1);out=[]
 for i in range(n):
  t=i/SR
  if kind=='lightning':
   pulses=sum(exp(-(t-at)*60) for at in (.015,.065,.11,.155) if t>=at);value=.20*high[i]*pulses+.32*sin(2*pi*(90*t+10*sin(17*t)))*exp(-t*13)
  elif kind=='freeze':
   value=.13*high[i]*exp(-t*6)+.25*lows[i]*exp(-t*9)
   for at,f in ((.015,1250),(.055,1740),(.13,880),(.18,2100)):
    if t>=at:value+=.07*sin(2*pi*f*(t-at))*exp(-(t-at)*22)
  elif kind=='gravity':
   env=sin(pi*min(1,t/length))**.6;value=(.23*high[i]+.16*sin(2*pi*(65*t-8*t*t)))*env
  elif kind=='fireball':value=.3*high[i]*exp(-t*7)+.4*sin(2*pi*(95*t-25*t*t))*exp(-t*8)+.07*high[i]*exp(-t*4)*max(0,sin(70*t))
  else:value=.23*high[i]*(sin(pi*t/length)**.8)*(1+.2*sin(2*pi*9*t))
  value*=min(1,t/.006)*min(1,max(0,(length-t)/.08));pan=.17*sin(2*pi*t/length);out.extend((value*(1-pan),value*(1+pan)))
 peak=max(abs(v) for v in out);gain=min(1,.85/max(peak,1e-6));data=array('h',(round(max(-1,min(1,v*gain))*32767) for v in out))
 with wave.open(str(OUT/('mage_'+kind+'.wav')),'wb') as f:f.setparams((2,2,SR,n,'NONE','not compressed'));f.writeframes(data.tobytes())
 print(kind,length,'seconds','peak',round(peak*gain,3))
if __name__=='__main__':
 for i,(kind,length) in enumerate([('lightning',.34),('freeze',.44),('gravity',.65),('fireball',.50),('typhoon',.62)]):make(kind,length,831+i)
