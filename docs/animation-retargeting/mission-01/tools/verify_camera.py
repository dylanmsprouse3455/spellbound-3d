import json,time,sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8790/docs/animation-retargeting/mission-01/'
root=Path(__file__).resolve().parents[1]/'evidence'
o=webdriver.ChromeOptions();o.binary_location='/usr/bin/chromium'
for a in ['--headless=new','--no-sandbox','--disable-dev-shm-usage']:o.add_argument(a)
o.set_capability('goog:loggingPrefs',{'browser':'ALL'})
d=webdriver.Chrome(service=Service('/usr/bin/chromedriver'),options=o)
def js(s):return d.execute_script(s)
def vp(w,h):d.execute_cdp_cmd('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':3,'mobile':True})
def shot(n):d.save_screenshot(str(root/n))
data={'url':base,'views':[]}
try:
 vp(390,844)
 d.execute_cdp_cmd('Emulation.setUserAgentOverride',{'userAgent':'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1','platform':'iPhone'})
 d.get(base);WebDriverWait(d,60).until(lambda _:js('return window.__spellMovement?.ready'))
 shot('after-portrait.png')
 for x,z,n in [(30,2,'enemy-hit.png'),(28,0,'corridor.png'),(28,4.2,'corridor-near-wall.png'),(0,13,'atrium-wide.png')]:
  js('window.__mission1.setPlayerPosition('+str(x)+','+str(z)+')');time.sleep(1.7)
  if n=='enemy-hit.png':js('window.__mission1.damageNearest(15)');time.sleep(.1)
  shot(n);state=js('return {player:window.__spellMovement.position,camera:window.__spellMovement.camera.position,stats:window.__mission1.renderStats}')
  data['views'].append({'image':n,**state});print(n,json.dumps(state),flush=True)
  if n=='enemy-hit.png':
   js('window.__mission1.damageNearest(200)');time.sleep(4.5);shot('enemy-death.png')
 js('window.__mission1.setPlayerPosition(0,0)');time.sleep(1);vp(844,390);time.sleep(.6);shot('after-landscape.png')
 data['errors']=[m['message'] for m in d.get_log('browser') if m['level']=='SEVERE'];assert not data['errors'],data['errors']
 data['complete']=True
finally:
 (root/'camera-qa.json').write_text(json.dumps(data,indent=2));d.quit()
