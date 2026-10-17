import numpy as np, json
from PIL import Image
from scipy import ndimage
OUT='game/assets/'
def load(n): return Image.open(f'cut/{n}_rgba.png').convert('RGBA')
def clean(im):
    # keep the largest blob + anything near it; drop faint specks
    a=np.array(im)[:,:,3]; m=a>40
    lab,k=ndimage.label(ndimage.binary_dilation(m,iterations=4))
    if k>1:
        sizes=ndimage.sum(m,lab,range(1,k+1)); keep=np.argmax(sizes)+1
        arr=np.array(im); arr[:,:,3]=np.where(lab==keep,arr[:,:,3],0); im=Image.fromarray(arr)
    return im.crop(im.getbbox())
def crop(sheet,b): return clean(sheet.crop(b))
def ref_x(im):
    a=np.array(im)[:,:,3].astype(float); h=a.shape[0]; top=a[:int(h*.35)]
    cols=top.sum(0); return float((cols*np.arange(len(cols))).sum()/cols.sum())
def strip(name,frames,chest_frac,pad=6):
    # frames: list of RGBA crops. align bottoms and head x
    rx=[ref_x(f) for f in frames]
    left=max(rx); right=max(f.width-r for f,r in zip(frames,rx))
    fw=int(left+right)+pad*2; fh=max(f.height for f in frames)+pad*2
    sheet=Image.new('RGBA',(fw*len(frames),fh)); chest=[]
    for i,(f,r) in enumerate(zip(frames,rx)):
        x=int(i*fw+pad+left-r); y=fh-pad-f.height; sheet.paste(f,(x,y),f)
        # chest anchor: band at chest_frac of figure height
        a=np.array(f)[:,:,3]; yy=int(f.height*chest_frac); band=a[max(0,yy-4):yy+4].sum(0).astype(float)
        cx=r if band.sum()==0 else float((band*np.arange(len(band))).sum()/band.sum())
        cx=0.5*cx+0.5*r  # lean toward the head line
        chest.append([round(x-i*fw+cx,1), round(y+yy,1)])
    sheet.save(OUT+name+'.webp','WEBP',quality=88,method=6)
    return {'src':name+'.webp','fw':fw,'fh':fh,'n':len(frames),'chest':chest,'foot':fh-pad}
meta={}
K=load('kalkidan_sheet')
kb=[(42,60,247,354),(254,60,446,355),(453,60,655,356),(672,60,871,355),(891,61,1086,355),(1101,60,1319,355),(37,409,226,705),(224,408,435,702),(447,410,609,707),(638,410,784,705)]
meta['kalkidan']={'run':strip('kalkidan_run',[crop(K,b) for b in kb],.36),'jump':strip('kalkidan_jump',[crop(K,(814,391,1043,688))],.38),'slide':strip('kalkidan_slide',[crop(K,(1003,492,1336,704))],.5)}
C=load('cousins1')
meta['nahome']={'run':strip('nahome_run',[crop(C,b) for b in [(41,21,228,289),(233,24,421,291),(444,27,587,294),(606,24,776,289)]],.52),
 'jump':strip('nahome_jump',[crop(C,b) for b in [(869,20,995,288),(1042,17,1144,258),(1193,28,1300,270)]],.5)}
meta['kiru']={'run':strip('kiru_run',[crop(C,b) for b in [(41,298,222,527),(227,300,414,527),(408,294,569,526),(591,297,760,526)]],.32),
 'jump':strip('kiru_jump',[crop(C,b) for b in [(896,308,995,531),(1015,277,1145,462),(1199,288,1305,500)]],.33)}
meta['bethani']={'run':strip('bethani_run',[crop(C,b) for b in [(46,549,209,750),(211,549,371,750),(394,544,495,752),(505,543,622,751),(635,538,761,751)]],.38),
 'jump':strip('bethani_jump',[crop(C,b) for b in [(870,538,1007,750),(1013,517,1170,750),(1171,515,1341,732)]],.36)}
D=load('cousins2')
# split the hand-holding chain
ch=D.crop((66,48,556,280)); a=np.array(ch)[:,:,3].sum(0)
c1=150+int(np.argmin(a[150:200])); c2=310+int(np.argmin(a[310:360]))
y1=clean(ch.crop((0,0,c1,ch.height))); g2=clean(ch.crop((c1,0,c2,ch.height))); y3=clean(ch.crop((c2,0,ch.width,ch.height)))
print('chain cuts',c1,c2)
meta['emmu']={'run':strip('emmu_run',[y3,crop(D,(545,68,709,276)),y1],.42)}
meta['eldana']={'run':strip('eldana_run',[g2],.42)}
meta['afomia']={'run':strip('afomia_run',[crop(D,b) for b in [(924,67,1036,276),(1034,60,1163,254),(1173,76,1312,281)]],.42),'wave':strip('afomia_wave',[crop(D,(770,51,911,278))],.42)}
for n,b in [('tukul',(72,293,603,729)),('gashe',(608,391,773,723)),('emaye',(785,408,949,718)),('wave_pair',(948,482,1187,714)),('wave_pink',(1154,515,1285,718))]:
    im=D.crop(b) if n=='tukul' else crop(D,b); im=im.crop(im.getbbox()); im.save(OUT+n+'.webp','WEBP',quality=88,method=6); meta[n]={'src':n+'.webp','w':im.width,'h':im.height}
I=load('item_kit')
for n,b in [('jebena',(148,17,439,363)),('mesob',(554,22,822,272)),('rock',(925,98,1261,277)),('bean',(649,339,786,460)),('pw_speed',(100,476,346,720)),('pw_magnet',(413,477,659,720)),('pw_double',(725,477,971,720)),('pw_dash',(1038,477,1284,720))]:
    im=I.crop(b) if n in('jebena','bean') else crop(I,b)
    im=im.crop(im.getbbox())
    if n.startswith('pw'): im=im.resize((160,160),Image.LANCZOS)
    if n=='bean': im=crop(I,(680,360,760,450)); im=im.resize((round(im.width*.8),round(im.height*.8)),Image.LANCZOS)
    im.save(OUT+n+'.webp','WEBP',quality=90,method=6); meta[n]={'src':n+'.webp','w':im.width,'h':im.height}
# backgrounds: mirror-tiled for seamless scrolling
P=Image.open('src/stitch-parallax.jpg').convert('RGB')
def mirror(im):
    w,h=im.size; o=Image.new(im.mode,(w*2,h)); o.paste(im,(0,0)); o.paste(im.transpose(Image.FLIP_LEFT_RIGHT),(w,0)); return o
mt=P.crop((0,0,1376,254)); mirror(mt).save(OUT+'bg_mountains.webp','WEBP',quality=84,method=6)
hl=np.array(P.crop((0,255,1376,512))).astype(int); r,g,b=hl[...,0],hl[...,1],hl[...,2]
land=(g>b+8)&(g>r-25)|((r+g+b)<330)
alpha=np.zeros(r.shape,np.uint8)
for x in range(hl.shape[1]):
    col=land[:,x]; ys=np.where(np.convolve(col,np.ones(5),'same')>=4)[0]
    top=ys[0] if len(ys) else 0
    alpha[top:,x]=255
alpha=np.array(Image.fromarray(alpha).filter(__import__('PIL.ImageFilter',fromlist=['x']).GaussianBlur(1.2)))
hills=Image.fromarray(np.dstack([hl,alpha]).astype(np.uint8),'RGBA'); mirror(hills).save(OUT+'bg_hills.webp','WEBP',quality=84,method=6)
mirror(P.crop((0,513,1376,717))).save(OUT+'bg_ground.webp','WEBP',quality=84,method=6)
P.crop((0,717,688,765)).save(OUT+'tibeb.webp','WEBP',quality=88,method=6)
meta['bg']={'mountains':[2752,254],'hills':[2752,257],'ground':[2752,204],'tibeb':[688,48]}
# app icon
Image.open('src/stitch-icon.jpg').convert('RGB').resize((512,512),Image.LANCZOS).save(OUT+'icon.webp','WEBP',quality=90)
json.dump(meta,open(OUT+'meta.json','w'),indent=0)
print('done')
