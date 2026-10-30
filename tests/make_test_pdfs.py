"""Realistic test PDFs: journal paper (A), phone scan (B), PNG screenshots incl. palette image (C), text-only (D).

Usage: python3 tests/make_test_pdfs.py tests/pdfs
Needs numpy, pillow, img2pdf, reportlab (and matplotlib for make_test_pdfs.py).
"""
import os, sys
os.makedirs(sys.argv[1] if len(sys.argv) > 1 else "tests/pdfs", exist_ok=True)
os.chdir(sys.argv[1] if len(sys.argv) > 1 else "tests/pdfs")
import numpy as np, io, img2pdf
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFilter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'))
rng=np.random.default_rng(1)
def photo(w,h,seed,noise=10):
    r=np.random.default_rng(seed)
    x=np.linspace(0,1,w)[None,:]*np.ones((h,1));y=np.linspace(0,1,h)[:,None]*np.ones((1,w))
    base=np.stack([180*x+40*y+20*np.sin(20*x*y),140*y+60+30*np.cos(9*x),120+80*np.sin(6*x+3*y)],-1)
    return Image.fromarray(np.clip(base+r.normal(0,noise,(h,w,3)),0,255).astype('uint8'))
# A) journal paper: 300dpi PNG figures shown small + a dermoscopy photo, embedded TTF font
c=canvas.Canvas('A_paper.pdf',pagesize=(595,842))
for p in range(8):
    c.setFont('DV',9)
    for l in range(60): c.drawString(50,800-l*12.5,"Skin lesion classification with foundation models across ISIC and Derm7pt benchmarks, line %d."%l)
    if p%2==0:
        fig,ax=plt.subplots(figsize=(6,4),dpi=300); 
        for k in range(5): ax.plot(np.cumsum(rng.normal(size=200)),lw=1)
        ax.imshow(rng.random((40,60)),extent=(0,200,-15,15),alpha=.3,aspect='auto')
        b=io.BytesIO(); fig.savefig(b,format='png'); plt.close(fig); b.seek(0)
        c.drawImage(ImageReader(Image.open(b)),60,420,width=230,height=153)
        ph=photo(3000,2250,p).filter(ImageFilter.GaussianBlur(1.5)); bb=io.BytesIO(); ph.save(bb,'JPEG',quality=92); bb.seek(0)
        c.drawImage(ImageReader(bb),310,420,width=230,height=172)
    c.showPage()
c.save()
# B) phone scan: 12MP JPEG q88, via img2pdf onto A4
pages=[]
for i in range(3):
    im=photo(3024,4032,10+i,noise=6); d=ImageDraw.Draw(im)
    for l in range(60): d.text((200,200+l*60),"Consent form scanned with phone camera, line %d"%l,fill=(15,15,15))
    b=io.BytesIO(); im.save(b,'JPEG',quality=88); pages.append(b.getvalue())
open('B_phonescan.pdf','wb').write(img2pdf.convert(pages,layout_fun=img2pdf.get_layout_fun((img2pdf.mm_to_pt(210),img2pdf.mm_to_pt(297)))))
# C) PNG screenshots via img2pdf (Flate + PNG predictor), incl palette image
ims=[]
s=photo(2560,1600,30,noise=3); b=io.BytesIO(); s.save(b,'PNG'); ims.append(b.getvalue())
pal=photo(2000,1400,31,noise=0).quantize(64); b=io.BytesIO(); pal.save(b,'PNG'); ims.append(b.getvalue())
open('C_screenshots.pdf','wb').write(img2pdf.convert(ims))
# D) text-only report (nothing to compress)
c=canvas.Canvas('D_textonly.pdf',pagesize=(595,842))
for p in range(10):
    c.setFont('DV',10)
    for l in range(60): c.drawString(50,800-l*12.5,"Plain text page %d line %d with an embedded TrueType font."%(p,l))
    c.showPage()
c.save()
