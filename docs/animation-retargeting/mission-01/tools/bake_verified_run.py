from pathlib import Path
root=Path(__file__).resolve().parents[1]
import subprocess
s=subprocess.check_output(['git','show','3e87598:docs/animation-retargeting/mission-01/index.html'],cwd=root,text=True)
s=s.replace('const swing=THREE.MathUtils.clamp(-thighForward*.65,-.42,.42);','const swing=arm.side*bakeDrive*.675-.325;')
api='''
let bakeDrive=0;
window.__bakeRun=()=>{
 mixer.stopAllAction();motionRoot.rotation.y=0;moving=true;combatMovementActive=false;selectedMotion='Run';casting=null;castPending=false;poseEnabled=false;throwActive=false;runArmWeight=1;
 const source=testCache.Run,action=mixer.clipAction(source);action.reset().setLoop(THREE.LoopRepeat,Infinity).setEffectiveWeight(1).setEffectiveTimeScale(1).play();
 const armBones=[...new Set(window.__spellRig.skinned.flatMap(m=>m.skeleton.bones))].filter(b=>/((Left|Right)(Shoulder|Arm|ForeArm|Hand))$/.test(b.name));
 const steps=Math.ceil(source.duration*60),times=[],values=armBones.map(()=>[]),last=armBones.map(()=>null);
 const driveAt=time=>{mixer.setTime(time);character.updateMatrixWorld(true);const v=(a,b)=>{const p=b.getWorldPosition(new THREE.Vector3()).sub(a.getWorldPosition(new THREE.Vector3()));return p.z/p.length()};return (v(leftHip,leftKnee)-v(rightHip,rightKnee))*.5};
 const drives=Array.from({length:steps},(_,i)=>driveAt(i*source.duration/steps)),minimum=Math.min(...drives),maximum=Math.max(...drives),mid=(minimum+maximum)*.5,extent=(maximum-minimum)*.5;
 for(let i=0;i<=steps;i++){
  const time=i===steps?0:i*source.duration/steps;bakeDrive=(drives[i%steps]-mid)/Math.max(.001,extent);mixer.setTime(time);
  for(const b of armBones)if(/Shoulder$/.test(b.name))b.quaternion.copy(b.userData.runRest);
  character.updateMatrixWorld(true);applyRunningArms(1);character.updateMatrixWorld(true);
  times.push(i*source.duration/steps);
  armBones.forEach((b,j)=>{const q=b.quaternion.clone();if(last[j]&&q.dot(last[j])<0)q.set(-q.x,-q.y,-q.z,-q.w);values[j].push(...q.toArray());last[j]=q});
 }
 const names=new Set(armBones.map(b=>b.name+'.quaternion'));
 const tracks=source.tracks.filter(tr=>!names.has(tr.name)).map(tr=>tr.clone());
 armBones.forEach((b,i)=>tracks.push(new THREE.QuaternionKeyframeTrack(b.name+'.quaternion',times,values[i])));
 return {clip:THREE.AnimationClip.toJSON(new THREE.AnimationClip('Ch08_Run_Verified_v1',source.duration,tracks)),evidence:{duration:source.duration,samples:steps+1,bones:armBones.map(b=>b.name),sourceTracks:source.tracks.length,outputTracks:tracks.length,driveRange:[minimum,maximum],swingRadians:[-1,.35]}};
};
'''
s=s.replace('const clock=new THREE.Clock();',api+'const clock=new THREE.Clock();')
(root/'motion-bake-lab.html').write_text(s)

import json,sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
options=webdriver.ChromeOptions();options.binary_location='/usr/bin/chromium'
for arg in ['--headless=new','--no-sandbox','--disable-dev-shm-usage']:options.add_argument(arg)
driver=webdriver.Chrome(service=Service('/usr/bin/chromedriver'),options=options)
try:
 base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8790/docs/animation-retargeting/mission-01/'
 driver.get(base+'motion-bake-lab.html')
 WebDriverWait(driver,60).until(lambda _:driver.execute_script('return window.__spellMovement?.ready'))
 result=driver.execute_script('return window.__bakeRun()')
 (root/'assets/animations/Ch08_Run_Verified_v1.json').write_text(json.dumps(result['clip'],separators=(',',':')))
 (root/'evidence/motion-ownership/bake.json').write_text(json.dumps(result['evidence'],indent=2))
 print(result['evidence'])
finally:
 driver.quit();(root/'motion-bake-lab.html').unlink(missing_ok=True)
