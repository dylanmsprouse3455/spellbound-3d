import json,time,sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8790/docs/animation-retargeting/mission-01/'
out=Path(__file__).resolve().parents[1]/'evidence/movement';out.mkdir(exist_ok=True)
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
r={'url':base}
try:
 d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':3,'mobile':True})
 d.execute_cdp_cmd('Emulation.setTouchEmulationEnabled',{'enabled':True})
 d.execute_cdp_cmd('Emulation.setUserAgentOverride',{'userAgent':'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1','platform':'iPhone'})
 d.get(base);WebDriverWait(d,60).until(lambda _:js('return window.__spellMovement?.ready'))
 js('window.__mission1.setPlayerPosition(-5,16)');time.sleep(.5);start();time.sleep(.9);r['running']=state();shot('run-a.png');time.sleep(.45);shot('run-b.png');stop();time.sleep(.5)
 a=r['running'];assert a['mode']=='Exploration' and a['motion']=='Run' and a['speed']==4.25 and not a['hands'] and not a['warning'],a
 print('RUN',json.dumps(a),flush=True)
 enemy=js('return window.__mission1.enemies.find(e=>e.active).position')
 js('window.__mission1.setPlayerPosition('+str(enemy[0]+2.7)+','+str(enemy[2])+')');time.sleep(.4);start();time.sleep(.6);r['combatMoving']=state();shot('combat-move.png');stop();time.sleep(.7);r['combatReady']=state();shot('combat-ready.png')
 b=r['combatMoving'];assert b['mode']=='Combat' and b['motion'] in ['Walk','Back'] and b['speed']==2.5 and b['hands'] and b['warning'],b
 assert r['combatReady']['channel'] and r['combatReady']['hands'],r['combatReady']
 print('COMBAT',json.dumps(b),flush=True)
 js('window.__mission1.setPlayerPosition(-5,16)');time.sleep(.5);start();time.sleep(.6);r['runningAgain']=state();stop();time.sleep(.5);r['stopped']=state()
 c=r['runningAgain'];assert c['mode']=='Exploration' and c['motion']=='Run' and c['speed']==4.25 and not c['hands'],c
 assert not r['stopped']['moving'] and r['stopped']['motion']=='Idle' and r['stopped']['speed']==0,r['stopped']
 r['errors']=[m['message'] for m in d.get_log('browser') if m['level']=='SEVERE'];assert not r['errors'],r['errors']
 r['complete']=True;print('TRANSITIONS_AND_RELEASE_PASS',flush=True)
except Exception as e:r['failure']=repr(e);raise
finally:
 (out/'results.json').write_text(json.dumps(r,indent=2));d.quit()
