from pathlib import Path
import re,json,zipfile,unicodedata,hashlib,subprocess,shutil,xml.etree.ElementTree as ET
from pypdf import PdfReader
import pdfplumber
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
tmp=root/'tmp';proof=tmp/'prova-v1';proof.mkdir(exist_ok=True)
pdf=root/'output/pdf/ecos-da-nevoa-revisado-v1.pdf';reader=PdfReader(pdf)
starts=json.loads((root/'editorial/paginacao.json').read_text(encoding='utf-8'))
def norm(s):return ''.join(ch for ch in unicodedata.normalize('NFKC',s).lower() if ch.isalnum())
pdftext=[]
for page in reader.pages:
    lines=page.extract_text().splitlines()
    lines=[s for s in lines if s.strip() not in ['ECOS DA NÉVOA','VORNE ERMEL'] and not s.strip().isdigit()]
    pdftext.append('\n'.join(lines))
miss=[];checks=[]
ns={'x':'http://www.w3.org/1999/xhtml','o':'http://www.idpf.org/2007/opf'}
epub=root/'output/epub/ecos-da-nevoa-revisado-v1.epub'
with zipfile.ZipFile(epub) as z:
    assert z.namelist()[0]=='mimetype' and z.getinfo('mimetype').compress_type==0
    assert z.read('mimetype')==b'application/epub+zip'
    for name in z.namelist():
        if name.endswith(('.xml','.opf','.xhtml')):ET.fromstring(z.read(name))
    opf=ET.fromstring(z.read('OEBPS/content.opf'))
    manifest={e.attrib['id']:e.attrib['href'] for e in opf.find('o:manifest',ns)}
    for href in manifest.values(): assert 'OEBPS/'+href in z.namelist()
    for item in opf.find('o:spine',ns): assert item.attrib['idref'] in manifest
    for i,p in enumerate(sorted((root/'edicao-textual/capitulos').glob('*.md'))):
        heading,body=p.read_text(encoding='utf-8').strip().split('\n\n',1)
        elem=ET.fromstring(z.read(f'OEBPS/ch{i:02}.xhtml'))
        out=[''.join(e.itertext()) for e in elem.findall('.//x:p',ns)]
        expected=[t for t in body.split('\n\n') if not t.startswith('## ')]
        assert out==expected,(i,'EPUB divergence')
        assert ''.join(elem.find('.//x:h1',ns).itertext())==heading[2:]
        sub=[''.join(e.itertext()) for e in elem.findall('.//x:h2',ns)]
        assert sub==[t[3:] for t in body.split('\n\n') if t.startswith('## ')]
        start=starts[i]['pagina']-1;end=starts[i+1]['pagina']-1 if i<15 else len(reader.pages)
        text=norm('\n'.join(pdftext[start:end]))
        for t in body.split('\n\n'):
            if norm(t.removeprefix('## ')) not in text:miss.append({'capitulo':i,'inicio':t[:80]})
        checks.append({'secao':i,'paragrafos':len(expected),'pagina_inicial':start+1,'epub_identico':True})
    for name in z.namelist():
        if name.endswith('.xhtml'):
            e=ET.fromstring(z.read(name))
            for a in e.iter():
                link=a.get('href') or a.get('src')
                if link:
                    f,_,anchor=link.partition('#');target='OEBPS/'+f if f else name
                    assert target in z.namelist(),(name,link)
                    if anchor:assert any(n.get('id')==anchor for n in ET.fromstring(z.read(target)).iter())
assert not miss,miss
assert all(abs(float(p.mediabox.width)-432)<.01 and abs(float(p.mediabox.height)-648)<.01 for p in reader.pages)
fonts={}
for p in reader.pages:
    for name,ref in p['/Resources'].get('/Font',{}).items():
        f=ref.get_object();desc=f.get('/FontDescriptor')
        if desc:
            desc=desc.get_object();fonts[str(f['/BaseFont'])]=any(k in desc for k in ['/FontFile','/FontFile2','/FontFile3'])
assert all(fonts.values())
overflow=[]
with pdfplumber.open(pdf) as doc:
    for i,page in enumerate(doc.pages,1):
        for ch in page.chars:
            if ch['x0']<25 or ch['x1']>407 or ch['top']<15 or ch['bottom']>635:overflow.append(i);break
assert not overflow,overflow
subprocess.run([shutil.which('pdftoppm'),'-r','100','-png',str(pdf),str(proof/'pagina')],check=True)
images=sorted(proof.glob('pagina-*.png'))
for first in range(0,len(images),4):
    sheet=Image.new('RGB',(1200,1880),'#d2d7d7');draw=ImageDraw.Draw(sheet)
    for j,p in enumerate(images[first:first+4]):
        im=Image.open(p);im.thumbnail((570,900));x=(j%2)*600+15;y=(j//2)*940+30
        sheet.paste(im,(x,y));draw.text((x,y-20),f'Página {first+j+1}',fill='black')
    sheet.save(proof/f'prancha-{first//4+1:02}.jpg',quality=90)
subprocess.run([shutil.which('pdftoppm'),'-singlefile','-scale-to','1800','-png',str(root/'output/capa/proposta-capa-impressa-v1.pdf'),str(proof/'capa-aberta')],check=True)
im=Image.open(root/'output/capa/capa-digital-v1.jpg');assert im.size==(1600,2560) and im.mode=='RGB'
v={'data':'2026-10-03','pdf':{'paginas':len(reader.pages),'dimensoes_pt':[432,648],'texto_integral':True,'secoes':checks,'fontes_incorporadas':fonts,'caracteres_fora_area_segura':overflow,'prova_renderizada':len(images),'inspecao_visual':'aguardando leitura das pranchas'},'epub':{'xml_valido':True,'links_validos':True,'paragrafos_identicos':True,'epubcheck':'não executado','kindle_previewer':'não executado'},'capa_digital':{'pixels':im.size,'modo':im.mode},'arquivos':{}}
for p in [pdf,epub,root/'output/capa/capa-digital-v1.jpg',root/'output/capa/proposta-capa-impressa-v1.pdf',root/'edicao-textual/livro-revisado.md']:
    v['arquivos'][str(p.relative_to(root))]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(root/'editorial/validacao-edicao-v1.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'paginas':len(reader.pages),'texto_pdf':'integral','epub':'parágrafos idênticos','pranchas':len(list(proof.glob('prancha-*.jpg')))},ensure_ascii=False))
