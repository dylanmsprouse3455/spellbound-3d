// A bounded, device-local recorder. No uploads, persistence, credentials or remote commands.
export function createMotionRecorder(readState,readBones,readActions,readRig){
 const samples=[],events=[];let writers=[],nextSample=0,previous=[],tracing=false;
 const trim=(list,now)=>{while(list.length&&list[0].at<now-10)list.shift()};
 const round=x=>Math.round(x*100000)/100000;
 const pose=()=>readBones().filter(Boolean).map(b=>({name:b.name,q:b.quaternion.toArray().map(round),p:b.getWorldPosition(b.position.clone()).toArray().map(round)}));
 function layer(name,fn){
  if(!tracing){fn();return;}
  const bones=readBones().filter(Boolean);previous=bones.map(b=>b.quaternion.toArray());
  fn();
  const changed=bones.filter((b,i)=>b.quaternion.toArray().some((v,j)=>Math.abs(v-previous[i][j])>.0001)).map(b=>b.name);
  if(changed.length)writers.push({layer:name,bones:changed});
 }
 function snapshot(){return {schema:1,build:'motion-ownership-v6',seconds:10,viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},samples:samples.slice(),events:events.slice()}}
 const api={
  begin(now){writers=[];tracing=now>=nextSample},layer,
  sample(now){if(now<nextSample)return;nextSample=now+1/15;const at=performance.now()/1000;samples.push({at,state:readState(),actions:readActions(),bones:pose(),rig:readRig(),writers:writers.slice()});trim(samples,at);if(samples.length>160)samples.shift();trim(events,at)},
  event(kind,data){const at=performance.now()/1000;events.push({at,kind,data});trim(events,at);if(events.length>100)events.shift()},
  snapshot,
  download(){const blob=new Blob([JSON.stringify(snapshot())],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='spellbound-motion-'+new Date().toISOString().replace(/[:.]/g,'-')+'.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);return samples.length}
 };return api;
}
