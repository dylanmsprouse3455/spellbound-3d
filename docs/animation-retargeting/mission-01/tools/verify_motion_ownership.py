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
 const fn=fore.map(x=>x/Math.hypot(...fore)),projection=width.reduce((v,x,i)=>v+x*fn[i],0),w=width.map((x,i)=>x-projection*fn[i]),u=[0,1,0].map((x,i)=>x-fn[1]*fn[i]);
 const palmRollAlignment=w.reduce((v,x,i)=>v+x*u[i],0)/Math.hypot(...w)/Math.hypot(...u);
 return {palmRollAlignment,fingerAlignment,thumbSideUp:width[1]/Math.hypot(...width),side,shoulder:a,elbow:b,hand:c,upperDown:v[1]/Math.hypot(...v),upperForward:(v[0]*f[0]+v[2]*f[2])/Math.hypot(...v),legForward:(leg[0]*f[0]+leg[2]*f[2])/Math.hypot(...leg)};
 });""")
def checkArms(pose):
 assert all(a['fingerAlignment']>.95 and a['palmRollAlignment']>.98 and a['upperDown']<-.45 and a['hand'][1]<a['shoulder'][1]-.03 for a in pose),pose


r={'url':base}
try:
 d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
 d.execute_cdp_cmd('Emulation.setTouchEmulationEnabled',{'enabled':True})
 d.execute_cdp_cmd('Emulation.setUserAgentOverride',{'userAgent':'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1','platform':'iPhone'})
 d.get(base);WebDriverWait(d,60).until(lambda _:js('return window.__spellMovement?.ready'))
 js("document.querySelector('#elementFire').click()")
 enemy=js('return window.__mission1.enemies.find(e=>e.active&&e.name==="West Wing Stalker").position')
 js('window.__mission1.setPlayerPosition('+str(enemy[0]+2.7)+','+str(enemy[2])+')')
 WebDriverWait(d,90).until(lambda _:js('return window.__spellCombat.hits>=3 && window.__spellCombat.attack==="dualwave"'))
 r['renderStats']=js('return window.__mission1.renderStats');assert not r['renderStats']['shadows'],r['renderStats']
 r['fireAttack']=js('return {hits:window.__spellCombat.hits,attack:window.__spellCombat.attack}')
 js('window.__mission1.setPlayerPosition(-5,16)');start();time.sleep(2);r['fireRun']=state();r['fireArms']=arms();checkArms(r['fireArms']);shot('fire-run-fixed.png')
 assert r['fireRun']['motion']=='Run' and r['fireRun']['speed']==4.25,r['fireRun']
 # Rotate through left, forward, backward; keep a clear starting position.
 r['directions']=[]
 for x,y in [(85,410),(180,315),(180,505)]:
  stop();js('window.__mission1.setPlayerPosition(-5,16)');event('touchStart',180,410);event('touchMove',x,y);time.sleep(.65)
  a=arms();checkArms(a);r['directions'].append({'state':state(),'arms':a})
 stop();time.sleep(.5);r['idle']=state();assert r['idle']['motion']=='Idle' and not r['idle']['moving'],r['idle']
 js("document.querySelector('#elementLightning').click()")
 enemy=js('return window.__mission1.enemies.find(e=>e.active&&e.name==="East Wing Stalker").position')
 js('window.__mission1.setPlayerPosition('+str(enemy[0]-2.7)+','+str(enemy[2])+')')
 WebDriverWait(d,15).until(lambda _:js('return window.__spellCombat.channelActive'));r['lightningChannel']=state()
 js('window.__mission1.setPlayerPosition(-5,16)');start();time.sleep(1.5);r['lightningRun']=state();r['lightningArms']=arms();checkArms(r['lightningArms']);shot('lightning-run-fixed.png')
 capture=js('return window.__spellMotionCapture.snapshot()');r['captureSamples']=len(capture['samples']);assert 1<=len(capture['samples'])<=160
 assert capture['samples'][-1]['at']-capture['samples'][0]['at']<=10.01
 runs=[s for s in capture['samples'] if s['state']['owner']=='run-clip' and len(s['actions'])==1]
 assert len(runs)>=8,len(runs)
 assert all(all(w['layer']=='mixer' for w in s['writers']) for s in runs),[(s['state'],s['writers']) for s in runs]
 assert all(s['actions'][0]['clip']=='Run' for s in runs)
 assert all(len(s['rig']['bones'])>=60 for s in capture['samples'])
 (out/'capture-replay-fixture.json').write_text(json.dumps(capture))
 # Export must use a local Blob and must not initiate fetch/XHR.
 js("window.__captureNetwork=[];const original=window.fetch;window.fetch=(...args)=>{window.__captureNetwork.push(String(args[0]));return original(...args)};window.__exportName=null;const click=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){window.__exportName=this.download;window.__exportProtocol=new URL(this.href).protocol;click.call(this)};document.querySelector('#captureMotion').click()")
 r['export']=js('return {name:window.__exportName,protocol:window.__exportProtocol,network:window.__captureNetwork}')
 assert r['export']['name'].endswith('.json') and r['export']['protocol']=='blob:' and not r['export']['network'],r['export']
 stop()
 d.get(base.split('?')[0]+'motion-review.html');WebDriverWait(d,60).until(lambda _:js('return window.__motionReview?.ready'))
 d.find_element('id','capture').send_keys(str(out/'capture-replay-fixture.json'));time.sleep(.5)
 r['reviewStatus']=d.find_element('id','status').text;assert 'owner:' in r['reviewStatus'],r['reviewStatus']
 js('window.__motionReview.setTime(0)')
 actual={b['name']:b for b in js('return window.__motionReview.bones')}
 error=max(abs(x-y) for b in capture['samples'][0]['rig']['bones'] for key,actualKey in [('q','q'),('p','localP')] for x,y in zip(b[key],actual[b['name']][actualKey]))
 r['replayMaxJointError']=error;assert error<1e-7,error
 shot('capture-replayed.png')
 r['errors']=[m['message'] for m in d.get_log('browser') if m['level']=='SEVERE'];assert not r['errors'],r['errors']
 r['complete']=True;print('FIRE_LIGHTNING_TURNS_EXPORT_REPLAY_PASS',flush=True)
except Exception as e:
 r['failure']=repr(e);r['debug']=js('return window.__spellMotionCapture?.snapshot()');r['errors']=d.get_log('browser');raise
finally:
 (out/'verification.json').write_text(json.dumps(r,indent=2));d.quit()
