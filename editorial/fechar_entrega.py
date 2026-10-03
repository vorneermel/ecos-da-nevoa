from pathlib import Path
import json,zipfile,hashlib,re
root=Path(__file__).resolve().parents[1]
vpath=root/'editorial/validacao-edicao-v1.json'
v=json.loads(vpath.read_text(encoding='utf-8'))
v['pdf']['inspecao_visual']='50 páginas inspecionadas; correções de sumário e quebra de palavra revalidadas'
v['capa_impressa']={'estado':'proposta','paginas_miolo':50,'papel_proposto':'creme','lombada_mm':3.175,'arte_pixels':[992,1586],'ppi_efetivo_aproximado':165,'template_kdp':'não aplicado','print_previewer':'não executado'}
for name,info in v['arquivos'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==info['sha256']
vpath.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
# Conferir que todo link local dos documentos de entrada aponta para algo real.
for name in ['README.md','editorial/relatorio-editorial-v1.md']:
    p=root/name
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if not target.startswith(('http:','https:')) and not target.endswith('.zip'):assert (p.parent/target).exists(),target
out=root/'output/entrega';out.mkdir(exist_ok=True)
files=[root/'README.md',root/'.gitattributes']
for rel in ['edicao-textual','editorial','output/capa']:
    files += [p for p in (root/rel).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
files += [root/'output/pdf/ecos-da-nevoa-revisado-v1.pdf',root/'output/epub/ecos-da-nevoa-revisado-v1.epub']
zpath=out/'ecos-da-nevoa-edicao-v1.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(set(files)):z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(zpath) as z:assert z.testzip() is None
print(json.dumps({'arquivo':str(zpath),'arquivos':len(set(files)),'bytes':zpath.stat().st_size,'sha256':hashlib.sha256(zpath.read_bytes()).hexdigest()},ensure_ascii=False))
