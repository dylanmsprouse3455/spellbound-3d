import * as THREE from 'https://esm.sh/three@0.170.0';
const bindings={hips:'Hips',spine:'Spine',chest:'Spine2',head:'Head','upperarm.l':'LeftArm','lowerarm.l':'LeftForeArm','wrist.l':'LeftHand','upperarm.r':'RightArm','lowerarm.r':'RightForeArm','wrist.r':'RightHand','upperleg.l':'LeftUpLeg','lowerleg.l':'LeftLeg','foot.l':'LeftFoot','toes.l':'LeftToeBase','upperleg.r':'RightUpLeg','lowerleg.r':'RightLeg','foot.r':'RightFoot','toes.r':'RightToeBase'};
export function boundBones(model){return [...new Set((()=>{const meshes=[];model.traverse(o=>{if(o.isSkinnedMesh)meshes.push(o)});return meshes.flatMap(m=>m.skeleton.bones)})())]}
export function retargetClip(source,target,clip){
 source.updateMatrixWorld(true);target.updateMatrixWorld(true);
 const sb=boundBones(source),tb=boundBones(target),sm=new Map(sb.map(b=>[b.name.replace(/[.:]/g,''),b])),sourceBone=n=>sm.get(n.replace(/[.:]/g,'')),pairs=Object.entries(bindings).map(([s,t])=>({s:sourceBone(s),t:tb.find(b=>b.name.toLowerCase().endsWith(t.toLowerCase()))}));
 if(pairs.some(p=>!p.s||!p.t))throw Error('Incomplete bound skeleton mapping');
 const targetRest=new Map(tb.map(b=>[b,{p:b.position.clone(),q:b.quaternion.clone(),s:b.scale.clone()}]));
 for(const p of pairs){p.sourceRest=p.s.getWorldQuaternion(new THREE.Quaternion()).invert();p.targetRest=p.t.getWorldQuaternion(new THREE.Quaternion());p.values=[];}
 const sourceHips=sourceBone('hips'),targetHips=pairs[0].t,sourceOrigin=sourceHips.getWorldPosition(new THREE.Vector3()),targetOrigin=targetHips.getWorldPosition(new THREE.Vector3());
 const length=(map,names)=>{const p=names.map(n=>map(n).getWorldPosition(new THREE.Vector3()));return p[0].distanceTo(p[1])+p[1].distanceTo(p[2])};
 const scale=length(n=>tb.find(b=>b.name.endsWith(n)),['LeftUpLeg','LeftLeg','LeftFoot'])/length(n=>sourceBone(n),['upperleg.l','lowerleg.l','foot.l']);
 const mixer=new THREE.AnimationMixer(source),action=mixer.clipAction(clip);action.setLoop(THREE.LoopOnce,1);action.clampWhenFinished=true;action.play();
 const count=Math.ceil(clip.duration*30),times=[],positions=[],trajectory=[],rotation=new THREE.Quaternion(),parent=new THREE.Quaternion(),position=new THREE.Vector3();
 let frameError=0;
 for(let i=0;i<=count;i++){
  const time=Math.min(i*clip.duration/count,clip.duration-1e-6);mixer.setTime(time);source.updateMatrixWorld(true);
  for(const [bone,r] of targetRest){bone.position.copy(r.p);bone.quaternion.copy(r.q);bone.scale.copy(r.s)}target.updateMatrixWorld(true);
  for(const p of pairs){
   p.s.getWorldQuaternion(rotation);rotation.multiply(p.sourceRest).multiply(p.targetRest);
   p.t.parent.getWorldQuaternion(parent);p.t.quaternion.copy(parent.invert().multiply(rotation));p.t.updateWorldMatrix(true,true);
   if(i>0){const v=p.values,q=p.t.quaternion;if(q.x*v.at(-4)+q.y*v.at(-3)+q.z*v.at(-2)+q.w*v.at(-1)<0)q.set(-q.x,-q.y,-q.z,-q.w)}
   p.values.push(...p.t.quaternion.toArray());
  }
  sourceHips.getWorldPosition(position);position.sub(sourceOrigin).multiplyScalar(scale);trajectory.push(position.toArray());position.add(targetOrigin);targetHips.parent.worldToLocal(position);targetHips.position.copy(position);positions.push(...position.toArray());times.push(i*clip.duration/count);
 }
 const tracks=pairs.map(p=>new THREE.QuaternionKeyframeTrack(p.t.name+'.quaternion',times,p.values));tracks.push(new THREE.VectorKeyframeTrack(targetHips.name+'.position',times,positions));
 mixer.stopAllAction();for(const [bone,r] of targetRest){bone.position.copy(r.p);bone.quaternion.copy(r.q);bone.scale.copy(r.s)}target.updateMatrixWorld(true);
 return {clip:new THREE.AnimationClip('KayKit_'+clip.name,clip.duration,tracks),audit:{sourceClip:clip.name,duration:clip.duration,samples:count+1,legScale:scale,mapping:pairs.map(p=>({source:p.s.name,target:p.t.name,sourceUuid:p.s.uuid,targetUuid:p.t.uuid})),sourceOrigin:sourceOrigin.toArray(),targetOrigin:targetOrigin.toArray(),trajectory,method:'World rotation deltas relative to each bind pose; target local rotations solved in parent order. Leg-length-scaled hip translation.'}};
}
