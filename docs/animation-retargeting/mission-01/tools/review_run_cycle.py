import json,time,sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8790/docs/animation-retargeting/mission-01/'
out=(Path(__file__).resolve().parents[1]/'evidence/motion-ownership');out.mkdir(exist_ok=True)
o=webdriver.ChromeOptions();o.binary_location='/usr/bin/chromium'
for a in ['--headless=new','--no-sandbox','--disable-dev-shm-usage']:o.add_argument(a)
o.set_capability('goog:loggingPrefs',{'browser':'ALL'})
d=webdriver.Chrome(service=Service('/usr/bin/chromedriver'),options=o)
def js(s):return d.execute_script(s)
def event(t,x=None,y=None):d.execute_cdp_cmd('Input.dispatchTouchEvent',{'type':t,'touchPoints':[] if x is None else [{'x':x,'y':y,'id':1}]})
def start():event('touchStart',180,410);event('touchMove',275,410)
def stop():event('touchEnd')
def state():return js('return {mode:window.__spellMovement.mode,speed:window.__spellMovement.speed,motion:window.__spellMovement.motion,position:window.__spellMovement.position,moving:window.__spellMovement.moving,hands:window.__spellMovement.handEffects,warning:window.__spellCombat.warning,channel:window.__spellCombat.channelActive,action:window.__spellMovement.action}')
def shot(n):d.save_screenshot(str(out/n))
def arms():
 return js("""
 const model=window.__spellRig.model,bound=new Set();
 model.traverse(o=>{if(o.isSkinnedMesh)for(const b of o.skeleton.bones)bound.add(b)});
 const bones=[...bound],find=s=>bones.find(b=>b.name.toLowerCase().endsWith(s)),p=b=>b.getWorldPosition(b.position.clone()).toArray();
 const h=window.__spellMovement.heading,f=[Math.sin(h),0,Math.cos(h)];
 return ['left','right'].map(side=>{
 const upper=find(side+'arm')||find(side+'upperarm'),lower=find(side+'forearm'),hand=find(side+'hand'),hip=find(side+'upleg'),knee=find(side+'leg');
 const a=p(upper),b=p(lower),c=p(hand),d=p(hip),e=p(knee),v=b.map((x,i)=>x-a[i]),leg=e.map((x,i)=>x-d[i]);
 const finger=n=>hand.children.find(b=>b.isBone&&b.name.toLowerCase().includes(n+'1'));
 const mid=p(finger('middle')),idx=p(finger('index')),pink=p(finger('pinky'));
 const fd=mid.map((x,i)=>x-c[i]),fore=c.map((x,i)=>x-b[i]),width=idx.map((x,i)=>x-pink[i]);
 const fingerAlignment=fd.reduce((v,x,i)=>v+x*fore[i],0)/Math.hypot(...fd)/Math.hypot(...fore);
 return {fingerAlignment,thumbSideUp:width[1]/Math.hypot(...width),side,shoulder:a,elbow:b,hand:c,upperDown:v[1]/Math.hypot(...v),upperForward:(v[0]*f[0]+v[2]*f[2])/Math.hypot(...v),legForward:(leg[0]*f[0]+leg[2]*f[2])/Math.hypot(...leg)};
 });""")
def checkArms(pose):
 assert all(a['fingerAlignment']>.95 and a['thumbSideUp']>.75 and a['upperDown']<-.7 and a['hand'][1]<a['shoulder'][1]-.08 for a in pose),pose


from PIL import Image,ImageDraw
import io,math
r={'url':base,'poses':[]}
try:
 d.set_window_size(390,844)
 d.get(base+'motion-review.html');WebDriverWait(d,60).until(lambda _:js('return window.__motionReview?.ready'))
 sheet=Image.new('RGB',(8*220,3*420),'#152027');labels=ImageDraw.Draw(sheet)
 for row,(view,angle) in enumerate([('front',0),('right',-1.57079632679),('back',3.14159265359)]):
  js('window.__motionReview.setView('+str(angle)+')')
  for i in range(8):
   phase=i*.7333333492279053/8;js('window.__motionReview.setTime('+str(phase)+')');time.sleep(.08)
   data=js('return window.__motionReview.bones');r['poses'].append({'view':view,'time':phase,'bones':data})
   im=Image.open(io.BytesIO(d.get_screenshot_as_png())).convert('RGB');im.thumbnail((220,390));sheet.paste(im,(i*220,row*420+25));labels.text((i*220+4,row*420+5),view+' '+str(i)+'/8',fill='white')
 sheet.save(out/'baked-run-cycle.png')
 r['errors']=[m['message'] for m in d.get_log('browser') if m['level']=='SEVERE'];assert not r['errors'],r['errors'];r['complete']=True
 print('FULL_CYCLE_REVIEW_READY',flush=True)
finally:
 (out/'cycle-review.json').write_text(json.dumps(r,indent=2));d.quit()
