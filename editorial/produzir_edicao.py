from pathlib import Path
import re, html, json, uuid, zipfile
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER,TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pypdf import PdfReader,PdfWriter
import subprocess, shutil

root=Path(__file__).resolve().parents[1]
title='Ecos da Névoa'; subtitle='O Segredo de 1824'; author='Vorne Ermel'
for d in ['pdf','epub','capa']: (root/'output'/d).mkdir(exist_ok=True)
tmp=root/'tmp';tmp.mkdir(exist_ok=True)
for name,f in [('Georgia','georgia.ttf'),('GeorgiaB','georgiab.ttf'),('GeorgiaI','georgiai.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+f))
pdfmetrics.registerFontFamily('Georgia',normal='Georgia',bold='GeorgiaB',italic='GeorgiaI',boldItalic='GeorgiaB')
styles={
 'body':ParagraphStyle('body',fontName='Georgia',fontSize=11,leading=15,alignment=TA_JUSTIFY,firstLineIndent=14,spaceAfter=3,allowWidows=0,allowOrphans=0,splitLongWords=False),
 'first':ParagraphStyle('first',fontName='Georgia',fontSize=11,leading=15,alignment=TA_JUSTIFY,spaceAfter=3,allowWidows=0,allowOrphans=0,splitLongWords=False),
 'head':ParagraphStyle('head',fontName='GeorgiaB',fontSize=21,leading=26,alignment=TA_CENTER,spaceAfter=25,keepWithNext=True),
 'sub':ParagraphStyle('sub',fontName='GeorgiaB',fontSize=12,leading=16,spaceBefore=16,spaceAfter=12,keepWithNext=True),
 'label':ParagraphStyle('label',fontName='Georgia',fontSize=10,leading=14,alignment=TA_CENTER,spaceAfter=12,keepWithNext=True),
 'title':ParagraphStyle('title',fontName='GeorgiaB',fontSize=32,leading=40,alignment=TA_CENTER,spaceAfter=22),
 'subtitle':ParagraphStyle('subtitle',fontName='Georgia',fontSize=17,leading=24,alignment=TA_CENTER,spaceAfter=60),
 'author':ParagraphStyle('author',fontName='Georgia',fontSize=14,leading=20,alignment=TA_CENTER),
}
chapters=[]
for p in sorted((root/'edicao-textual'/'capitulos').glob('*.md')):
    h,b=p.read_text(encoding='utf-8').strip().split('\n\n',1)
    chapters.append((h[2:],b.split('\n\n')))
assert len(chapters)==16
W,H=432,648
def running(c,d):
    c.saveState()
    if d.page>3:
        c.setFont('Georgia',8);c.setFillGray(.35)
        c.drawCentredString(W/2,H-29,title.upper() if d.page%2 else author.upper())
        c.setFillGray(0);c.drawCentredString(W/2,27,str(d.page))
    c.restoreState()
class Book(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(str(path),pagesize=(W,H),title=title+' — '+subtitle,author=author)
        frames=[Frame(x,51,W-99,H-105,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0,id=id) for x,id in [(54,'odd'),(45,'even')]]
        self.addPageTemplates([PageTemplate('Odd',[frames[0]],onPage=running,autoNextPageTemplate='Even'),PageTemplate('Even',[frames[1]],onPage=running,autoNextPageTemplate='Odd')])
    def beforeDocument(self): self.starts=[]
    def afterFlowable(self,f):
        if hasattr(f,'chapter_title'):
            self.notify('TOCEntry',(0,f.chapter_title,self.page))
            self.starts.append({'titulo':f.chapter_title,'pagina':self.page})
story=[Spacer(1,125),Paragraph(title,styles['title']),Paragraph(subtitle,styles['subtitle']),Paragraph(author,styles['author']),PageBreak(),Spacer(1,145)]
for p in ['Ecos da Névoa — O Segredo de 1824','Vorne Ermel','Edição revisada v1 · 2026','Obra de ficção. Personagens, acontecimentos sobrenaturais e organizações pertencem ao universo narrativo.']:
    story+=[Paragraph(html.escape(p),ParagraphStyle('notice',fontName='Georgia',fontSize=9,leading=14,alignment=TA_CENTER,spaceAfter=14))]
story+=[PageBreak(),Paragraph('Sumário',styles['head'])]
toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',fontName='Georgia',fontSize=9.5,leading=12,spaceBefore=3,rightIndent=24)]
story += [toc,PageBreak()]
for n,(heading,paras) in enumerate(chapters):
    label,ct=heading.split(' — ',1)
    story += [Spacer(1,20),Paragraph(label.upper(),styles['label'])]
    ph=Paragraph(html.escape(ct),styles['head']);ph.chapter_title=heading;story.append(ph)
    first=True
    for p in paras:
        if p.startswith('## '):
            story.append(Paragraph(html.escape(p[3:]),styles['sub']));first=True
        else:
            story.append(Paragraph(html.escape(p),styles['first'] if first else styles['body']));first=False
    if n<15:story.append(PageBreak())
pdf=root/'output/pdf/ecos-da-nevoa-revisado-v1.pdf'
doc=Book(pdf);doc.multiBuild(story)
r=PdfReader(pdf)
if len(r.pages)%2:
    w=PdfWriter();w.clone_document_from_reader(r);w.add_blank_page(W,H)
    with pdf.open('wb') as f:w.write(f)
pages=len(PdfReader(pdf).pages)
(root/'editorial/paginacao.json').write_text(json.dumps(doc.starts,ensure_ascii=False,indent=2),encoding='utf-8')

# Capa frontal: tipografia vetorial editável no fonte SVG e no PDF.
cover=root/'output/capa';art=cover/'arte-capa-v1.png'
front=tmp/'capa-frontal.pdf'
c=canvas.Canvas(str(front),pagesize=(W,H));c.drawImage(str(art),0,0,W,H)
c.setFillColor(HexColor('#f1e8d4'));c.setFont('GeorgiaB',40)
c.drawCentredString(W/2,H-80,'ECOS DA');c.drawCentredString(W/2,H-128,'NÉVOA')
c.setFont('Georgia',16);c.drawCentredString(W/2,H-166,subtitle)
c.setStrokeColor(HexColor('#b6a16b'));c.setLineWidth(.6);c.line(160,H-190,272,H-190)
c.setFont('GeorgiaB',16);c.drawCentredString(W/2,38,author.upper());c.save()
subprocess.run([shutil.which('pdftoppm'),'-singlefile','-scale-to-x','1600','-scale-to-y','2560','-jpeg',str(front),str(cover/'capa-digital-v1')],check=True)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="2560" viewBox="0 0 432 648"><image href="arte-capa-v1.png" width="432" height="648" preserveAspectRatio="none"/><g fill="#f1e8d4" text-anchor="middle" font-family="Georgia"><text x="216" y="80" font-size="40" font-weight="bold">ECOS DA</text><text x="216" y="128" font-size="40" font-weight="bold">NÉVOA</text><text x="216" y="166" font-size="16">{subtitle}</text><path d="M160 190H272" stroke="#b6a16b"/><text x="216" y="610" font-size="16" font-weight="bold">{author.upper()}</text></g></svg>'''
(cover/'capa-editavel-v1.svg').write_text(svg,encoding='utf-8')
back='Um casarão barato demais. Um corredor que não termina. Um segredo trazido pelo mar em 1824.\n\nAo comprar uma antiga propriedade no Vale dos Sinos, Emanuel e Jade esperam construir uma vida juntos. Mas a casa muda de tamanho, o barro obedece às mãos de Emanuel e Jade começa a enxergar lembranças que não são suas.\n\nQuando uma névoa sombria invade a região, outros defensores chegam ao casarão. Para proteger o vale, o grupo terá de descobrir por que o porão se liga a cidades abandonadas em três continentes.\n\nEntre argila, raízes e alianças, a confiança que os une pode ser sua única defesa contra uma força que se alimenta do medo.'
(cover/'contracapa.md').write_text(back+'\n',encoding='utf-8')
# Proposta de capa aberta; geometria para papel creme, sem texto em lombada curta.
spine=pages*.0025*72;bleed=9;CW=2*W+spine+2*bleed;CH=H+2*bleed
c=canvas.Canvas(str(cover/'proposta-capa-impressa-v1.pdf'),pagesize=(CW,CH));c.setFillColor(HexColor('#101c21'));c.rect(0,0,CW,CH,fill=1,stroke=0)
fx=bleed+W+spine;c.drawImage(str(art),fx,0,W+bleed,CH)
c.setFillColor(HexColor('#f1e8d4'));c.setFont('GeorgiaB',40)
c.drawCentredString(fx+W/2,bleed+H-80,'ECOS DA');c.drawCentredString(fx+W/2,bleed+H-128,'NÉVOA')
c.setFont('Georgia',16);c.drawCentredString(fx+W/2,bleed+H-166,subtitle)
c.setFont('GeorgiaB',16);c.drawCentredString(fx+W/2,bleed+38,author.upper())
y=CH-85
bs=ParagraphStyle('back',fontName='Georgia',fontSize=12,leading=18,textColor=HexColor('#f1e8d4'),spaceAfter=18)
for p in back.split('\n\n'):
    pp=Paragraph(html.escape(p),bs);pw,ph=pp.wrap(W-100,CH);pp.drawOn(c,bleed+48,y-ph);y-=ph+20
# Área clara reservada ao código de barras do KDP; sem ISBN ou código fictício.
c.setFillColor(HexColor('#f1e8d4'));c.rect(bleed+W-180,bleed+24,144,86.4,fill=1,stroke=0)
c.save()

def xhtml(h,body):
    return f'<?xml version="1.0" encoding="UTF-8"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="pt-BR" xml:lang="pt-BR"><head><title>{html.escape(h)}</title><meta charset="utf-8"/><link rel="stylesheet" type="text/css" href="style.css"/></head><body>{body}</body></html>'
contents={'style.css':'body{font-family:serif;line-height:1.45;margin:5%}h1{text-align:center;font-size:1.55em;line-height:1.2;margin:2em 0 1.5em}h2{font-size:1.1em;page-break-after:avoid;margin-top:1.6em}p{text-indent:1.25em;margin:0 0 .4em;orphans:2;widows:2}.first,.author{text-indent:0}.author{text-align:center}nav li{margin:.6em 0}a{color:inherit}.cover{text-align:center;margin:0}.cover img{max-width:100%;max-height:95vh}',
'title.xhtml':xhtml(title,f'<section epub:type="titlepage"><h1>{title}</h1><p class="author">{subtitle}</p><p class="author">{author}</p></section>'),
'cover.xhtml':xhtml('Capa','<section epub:type="cover" class="cover"><img src="cover.jpg" alt="Capa de Ecos da Névoa — O Segredo de 1824, de Vorne Ermel"/></section>')}
for n,(h,paras) in enumerate(chapters):
    typ='prologue' if n==0 else 'epilogue' if n==15 else 'chapter'
    body=f'<section epub:type="{typ}" id="ch{n:02}"><h1>{html.escape(h)}</h1>'
    first=True
    for p in paras:
        if p.startswith('## '):body+=f'<h2>{html.escape(p[3:])}</h2>';first=True
        else:body+=f'<p class="{"first" if first else "body"}">{html.escape(p)}</p>';first=False
    contents[f'ch{n:02}.xhtml']=xhtml(h,body+'</section>')
nav='<nav epub:type="toc" id="toc"><h1>Sumário</h1><ol>'+''.join(f'<li><a href="ch{n:02}.xhtml#ch{n:02}">{html.escape(h)}</a></li>' for n,(h,p) in enumerate(chapters))+'</ol></nav><nav epub:type="landmarks" hidden="hidden"><h2>Navegação</h2><ol><li><a epub:type="cover" href="cover.xhtml">Capa</a></li><li><a epub:type="bodymatter" href="ch00.xhtml#ch00">Início</a></li></ol></nav>'
contents['nav.xhtml']=xhtml('Sumário',nav)
uid='urn:uuid:'+str(uuid.uuid5(uuid.NAMESPACE_URL,'ecos-da-nevoa-vorne-ermel-2026-10-03-v1'))
manifest='<item id="style" href="style.css" media-type="text/css"/><item id="cover-image" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>'
for name in contents:
    if name.endswith('.xhtml'):manifest+=f'<item id="{name[:-6]}" href="{name}" media-type="application/xhtml+xml"'+(' properties="nav"' if name=='nav.xhtml' else '')+'/>'
spine='<itemref idref="cover" linear="no"/><itemref idref="title"/><itemref idref="nav"/>'+''.join(f'<itemref idref="ch{n:02}"/>' for n in range(16))
opf=f'<?xml version="1.0" encoding="UTF-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="pt-BR"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">{uid}</dc:identifier><dc:title>{title} — {subtitle}</dc:title><dc:creator>{author}</dc:creator><dc:language>pt-BR</dc:language><meta property="dcterms:modified">2026-10-03T18:00:00Z</meta></metadata><manifest>{manifest}</manifest><spine>{spine}</spine></package>'
epub=root/'output/epub/ecos-da-nevoa-revisado-v1.epub'
with zipfile.ZipFile(epub,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
    z.writestr('META-INF/container.xml','<?xml version="1.0"?><container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
    z.writestr('OEBPS/content.opf',opf);z.write(cover/'capa-digital-v1.jpg','OEBPS/cover.jpg')
    for name,content in contents.items():z.writestr('OEBPS/'+name,content)
print(json.dumps({'pdf':str(pdf),'paginas':pages,'epub':str(epub),'secoes':16,'lombada_mm':pages*.0635},ensure_ascii=False))
