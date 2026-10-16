from pathlib import Path
import json,struct,io,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def read(p):
 b=p.read_bytes(); n=struct.unpack_from('<I',b,12)[0]
 return json.loads(b[20:20+n]),b[28+n:]
def pack(g,blob,p):
 g['buffers']=[{'byteLength':len(blob)}]
 j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
 blob+=b'\0'*((-len(blob))%4)
 p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
def optimize(src,dst,keep=None):
 g,blob=read(src); original=json.loads(json.dumps(g)); imageData={}; images=[]
 for im in g.get('images',[]):
  v=g['bufferViews'][im['bufferView']];data=blob[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
  pic=Image.open(io.BytesIO(data)); before=pic.size
  pic.thumbnail((1024,1024),Image.Resampling.LANCZOS);out=io.BytesIO()
  if im['mimeType']=='image/jpeg':pic.convert('RGB').save(out,format='JPEG',quality=82,optimize=True)
  else:pic.save(out,format='PNG',optimize=True)
  imageData[im['bufferView']]=out.getvalue()
  images.append({'before':before,'after':pic.size,'bytesBefore':len(data),'bytesAfter':len(out.getvalue())})
 if keep:
  g['animations']=[a for a in g.get('animations',[]) if a.get('name') in keep]
  assert {a['name'] for a in g['animations']}==set(keep)
 used=set()
 for m in g.get('meshes',[]):
  for p in m['primitives']:
   used.update(p['attributes'].values())
   if 'indices' in p:used.add(p['indices'])
   for target in p.get('targets',[]):used.update(target.values())
 for s in g.get('skins',[]):
  if 'inverseBindMatrices' in s:used.add(s['inverseBindMatrices'])
 for a in g.get('animations',[]):
  for s in a['samplers']:used.update([s['input'],s['output']])
 used=sorted(used); amap={old:i for i,old in enumerate(used)}
 for m in g.get('meshes',[]):
  for p in m['primitives']:
   p['attributes']={k:amap[v] for k,v in p['attributes'].items()}
   if 'indices' in p:p['indices']=amap[p['indices']]
   for target in p.get('targets',[]):
    for k,v in list(target.items()):target[k]=amap[v]
 for s in g.get('skins',[]):
  if 'inverseBindMatrices' in s:s['inverseBindMatrices']=amap[s['inverseBindMatrices']]
 for a in g.get('animations',[]):
  for s in a['samplers']:
   s['input']=amap[s['input']];s['output']=amap[s['output']]
 g['accessors']=[g['accessors'][i] for i in used]
 views={im['bufferView'] for im in g.get('images',[]) if 'bufferView' in im}
 for a in g['accessors']:
  if 'bufferView' in a:views.add(a['bufferView'])
  if 'sparse' in a:
   views.add(a['sparse']['indices']['bufferView']);views.add(a['sparse']['values']['bufferView'])
 vmap={old:i for i,old in enumerate(sorted(views))};newBlob=bytearray();newViews=[]
 for i in sorted(views):
  v=dict(g['bufferViews'][i]);start=v.get('byteOffset',0);data=imageData.get(i,blob[start:start+v['byteLength']])
  newBlob.extend(b'\0'*((-len(newBlob))%4));v['byteOffset']=len(newBlob);v['byteLength']=len(data);newBlob.extend(data);newViews.append(v)
 for a in g['accessors']:
  if 'bufferView' in a:a['bufferView']=vmap[a['bufferView']]
  if 'sparse' in a:
   for k in ['indices','values']:a['sparse'][k]['bufferView']=vmap[a['sparse'][k]['bufferView']]
 for im in g.get('images',[]):
  if 'bufferView' in im:im['bufferView']=vmap[im['bufferView']]
 g['bufferViews']=newViews;pack(g,bytes(newBlob),dst)
 ng,nb=read(dst)
 assert ng['nodes']==original['nodes']
 assert all(s.get('joints')==o.get('joints') and s.get('skeleton')==o.get('skeleton') for s,o in zip(ng['skins'],original['skins']))
 # Every retained non-image buffer view is copied byte for byte.
 for old,new in vmap.items():
  if old in imageData:continue
  a=original['bufferViews'][old];b=ng['bufferViews'][new]
  assert blob[a.get('byteOffset',0):a.get('byteOffset',0)+a['byteLength']]==nb[b['byteOffset']:b['byteOffset']+b['byteLength']]
 return {'source':src.name,'output':dst.name,'bytesBefore':src.stat().st_size,'bytesAfter':dst.stat().st_size,'images':images,'clipsBefore':len(original.get('animations',[])),'clipsAfter':[a['name'] for a in ng.get('animations',[])],'rigAndRetainedBuffersVerified':True}
reports=[]
reports.append(optimize(ROOT/'assets/player/character-mobile.glb',ROOT/'assets/player/character-mobile-optimized.glb'))
reports.append(optimize(ROOT/'assets/enemies/UAL2_Standard.glb',ROOT/'assets/enemies/UAL2_Mission1.glb',{'Zombie_Idle_Loop','Zombie_Walk_Fwd_Loop','Zombie_Scratch','Hit_Knockback','LayToIdle'}))
(ROOT/'asset-optimization.json').write_text(json.dumps(reports,indent=2)+'\n')
for r in reports:print(r['source'],r['bytesBefore'],'->',r['bytesAfter'],'rig/buffers verified',r['rigAndRetainedBuffersVerified'])
