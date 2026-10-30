"""Large test PDFs: 4-page 300 dpi scan, figure-heavy paper with a transparent image, CMYK JPEG.

Usage: python3 tests/make_test_pdfs_basic.py tests/pdfs
Needs numpy, pillow, img2pdf, reportlab (and matplotlib for make_test_pdfs.py).
"""
import os, sys
os.makedirs(sys.argv[1] if len(sys.argv) > 1 else "tests/pdfs", exist_ok=True)
os.chdir(sys.argv[1] if len(sys.argv) > 1 else "tests/pdfs")
import numpy as np, img2pdf, io
from PIL import Image, ImageDraw, ImageFilter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
def photo(w,h,seed):
    r=np.random.default_rng(seed)
    x=np.linspace(0,1,w)[None,:]*np.ones((h,1));y=np.linspace(0,1,h)[:,None]*np.ones((1,w))
    base=np.stack([200*x+30*y,150*y+50,120+80*np.sin(6*x+3*y)],-1)
    img=Image.fromarray(np.clip(base+r.normal(0,18,(h,w,3)),0,255).astype('uint8'))
    d=ImageDraw.Draw(img)
    for i in range(min(40,h//90-2)): d.text((100,100+i*90),"Scanned line of text %d lorem ipsum consent form"%i,fill=(20,20,20))
    return img
pages=[]
for i in range(4):
    b=io.BytesIO(); photo(2480,3508,i).save(b,'JPEG',quality=95); pages.append(b.getvalue())
open('scan.pdf','wb').write(img2pdf.convert(pages))
b=io.BytesIO(); photo(1600,2200,9).convert('CMYK').save(b,'JPEG',quality=95)
open('cmyk.pdf','wb').write(img2pdf.convert([b.getvalue()]))
c=canvas.Canvas('paper.pdf',pagesize=(595,842))
for p in range(3):
    c.setFont('Helvetica-Bold',16); c.drawString(56,790,f"Section {p+1}: Results")
    c.setFont('Helvetica',10)
    for l in range(20): c.drawString(56,760-l*14,"Dermatology foundation model evaluation across benchmark splits, line %d."%l)
    fig=photo(1800,1200,20+p).filter(ImageFilter.GaussianBlur(2))
    c.drawImage(ImageReader(fig),56,200,width=480,height=320)
    if p==1:
        rgba=Image.new('RGBA',(800,400),(0,0,0,0)); d=ImageDraw.Draw(rgba); d.ellipse((50,50,750,350),fill=(200,30,30,180))
        c.drawImage(ImageReader(rgba),56,60,width=300,height=150,mask='auto')
    c.showPage()
c.save()
