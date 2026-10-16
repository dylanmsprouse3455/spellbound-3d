import json,time,sys,math,shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'evidence';EV.mkdir(exist_ok=True)
if Path('/tmp/mission1-public-current.png').exists() and not (EV/'before-portrait.png').exists():shutil.copy('/tmp/mission1-public-current.png',EV/'before-portrait.png')
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8790/docs/animation-retargeting/mission-01/'
result={'url':base,'checks':{}}
def log(k,v):
 result['checks'][k]=v;(EV/'qa-results.json').write_text(json.dumps(result,indent=2));print(k,json.dumps(v),flush=True)
o=webdriver.ChromeOptions();o.binary_location='/usr/bin/chromium'
for a in ['--headless=new','--no-sandbox','--disable-dev-shm-usage']:o.add_argument(a)
o.set_capability('goog:loggingPrefs',{'browser':'ALL'})
d=webdriver.Chrome(service=Service('/usr/bin/chromedriver'),options=o);d.set_script_timeout(45)
def js(code):return d.execute_script(code)
def viewport(w,h):
 d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':3,'mobile':True})
def touch(typ,x=None,y=None):
 points=[] if x is None else [{'x':x,'y':y,'id':1}]
 d.execute_cdp_cmd('Input.dispatchTouchEvent',{'type':typ,'touchPoints':points})
def drag(dx,dy):
 touch('touchStart',180,410);touch('touchMove',180+dx,410+dy)
def release():touch('touchEnd')
def pos():return js('return window.__spellMovement.position')
def shot(name):d.save_screenshot(str(EV/name))
try:
 viewport(390,844);d.execute_cdp_cmd('Emulation.setTouchEmulationEnabled',{'enabled':True})
 d.execute_cdp_cmd('Emulation.setUserAgentOverride',{'userAgent':'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1','platform':'iPhone'})
 d.get(base);WebDriverWait(d,65).until(lambda _:js('return window.__spellMovement?.ready && window.__mission1?.enemies.length===4'))
 time.sleep(.4);shot('after-portrait.png')
 log('initial',js('return {ready:window.__spellMovement.ready,enemies:window.__mission1.enemies,stats:window.__mission1.renderStats,batching:window.__mission1.batching,viewport:[innerWidth,innerHeight]}'))
 # Test all eight actual FBX files with the same browser loader; this does not alter the active character.
 parsed=d.execute_async_script("""
 const done=arguments[arguments.length-1];
 import('https://esm.sh/three@0.170.0/examples/jsm/loaders/FBXLoader.js').then(async({FBXLoader})=>{
 const files=['standing idle.fbx','Standing Walk Forward.fbx','Standing Run Forward.fbx','Standing Jump.fbx','Standing Walk Back.fbx','standing idle 02.fbx','Standing 1H Magic Attack 01.fbx','Standing 2H Magic Area Attack 02.fbx'];
 const loader=new FBXLoader();
 return Promise.all(files.map(async name=>{const obj=await loader.loadAsync(new URL('assets/animations/'+name,location.href).href);return {name,clips:obj.animations.length,tracks:obj.animations[0]?.tracks.length,duration:obj.animations[0]?.duration};}));
 }).then(done).catch(e=>done({error:String(e)}));""")
 assert isinstance(parsed,list) and len(parsed)==8 and all(a['tracks']>0 for a in parsed),parsed
 log('allPlayerAnimations',parsed)
 selections=[]
 for id in ['elementFire','elementLightning']:
  r=js("return (()=>{const r=document.getElementById('"+id+"').getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})()")
  assert r['w']>=44 and r['h']>=44 and r['x']>=0 and r['x']+r['w']<=390 and r['y']+r['h']<=844,r
  touch('touchStart',r['x']+r['w']/2,r['y']+r['h']/2);release();time.sleep(.1)
  selections.append({'button':id,'rect':r,'selected':js('return window.__spellCombat.element')})
 log('touchAbilities',selections);assert selections[0]['selected']=='fire' and selections[1]['selected']=='lightning'
 # Movement and release require real browser touch events.
 start=pos();drag(0,-95);time.sleep(1.2);walk=pos();shot('walk-phase-a.png');time.sleep(.35);shot('walk-phase-b.png');release();time.sleep(.5);stopped=pos();time.sleep(.5);stable=pos()
 log('touchMovement',{'before':start,'during':walk,'afterRelease':stopped,'later':stable,'moving':js('return window.__spellMovement.moving')})
 assert math.dist(start,walk)>.2 and math.dist(stopped,stable)<.03 and not js('return window.__spellMovement.moving')
 # Combat hit and death use an undamaged wing enemy.
 js('window.__mission1.setPlayerPosition(30,2)');time.sleep(1.1)
 js("document.getElementById('elementFire').click()");prior=js('return window.__mission1.enemies')
 js('window.__mission1.damageNearest(15)');time.sleep(.12);hit=js('return window.__mission1.enemies');shot('enemy-hit.png')
 assert any(a['hp']<b['hp'] and a['hp']>0 for a,b in zip(hit,prior))
 js('window.__mission1.damageNearest(200)');time.sleep(1.7);dead=js('return window.__mission1.enemies');shot('enemy-death.png')
 assert any(not a['active'] and a['hp']==0 and a['animation']=='LayToIdle' for a in dead)
 log('enemyCombat',{'before':prior,'hit':hit,'death':dead,'warning':js('return window.__spellCombat.warning')})
 # Exercise a complete escalator ascent with touch input, then return down the same ramp.
 js('window.__mission1.setPlayerPosition(-11.5,-2.1)');time.sleep(.5);drag(0,-95);ascent=[]
 for _ in range(18):
  time.sleep(.7);ascent.append(pos())
  if ascent[-1][2]<-11.65:break
 release();time.sleep(.5);top=pos();shot('escalator-landing.png')
 assert top[1]>4.9 and top[2]<-11.5,ascent
 warningAtTop=js('return window.__spellCombat.warning')
 drag(0,95);descent=[]
 for _ in range(18):
  time.sleep(.7);descent.append(pos())
  if descent[-1][2]>-2.3:break
 release();time.sleep(.7);bottom=pos();assert bottom[1]<.2,bottom
 log('stairs',{'ascent':ascent,'top':top,'groundWarningAtTop':warningAtTop,'descent':descent,'bottom':bottom})
 # Same follow camera, wider atrium view and a corridor view.
 js('window.__mission1.setPlayerPosition(0,13)');time.sleep(1.0);shot('atrium-wide.png')
 js('window.__mission1.setPlayerPosition(28,0)');time.sleep(.8);shot('corridor.png')
 viewport(844,390);time.sleep(.5);shot('after-landscape.png')
 landscape=js('return ["elementFire","elementLightning"].map(id=>{const r=document.getElementById(id).getBoundingClientRect();return {id,x:r.x,y:r.y,w:r.width,h:r.height}})')
 assert all(r['x']>=0 and r['y']>=0 and r['x']+r['w']<=844 and r['y']+r['h']<=390 and r['h']>=44 for r in landscape)
 log('landscapeControls',landscape)
 severe=[m['message'] for m in d.get_log('browser') if m['level']=='SEVERE'];log('browserErrors',severe);assert not severe,severe
 log('complete',True)
except Exception as e:
 log('failure',repr(e));shot('failure.png');raise
finally:d.quit()
