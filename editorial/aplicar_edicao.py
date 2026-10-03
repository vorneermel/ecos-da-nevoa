from pathlib import Path
import re, json, difflib

root = Path(__file__).resolve().parents[1]
ed = root/'edicao-textual'
pages = sorted((ed/'transcricao').glob('*.md'))
assert len(pages)==53
text = ''
for p in pages:
    page=p.read_text(encoding='utf-8').strip()
    boundary='\n\n' if text and re.search(r'[.!?…][”"]?$',text) and re.match(r'[A-ZÁÉÍÓÚÂÊÔÃÕÇ—#]',page) else '\n'
    text+=boundary+page
text=text.strip()
text = re.sub(r'\n(#{1,2} )', r'\n\n\1', text)
text = re.sub(r'(?m)^(#{1,2} [^\n]+)\n(?!\n)',r'\1\n\n',text)
text = re.sub(r'(?<!\n)\n(?!\n|#)', ' ', text)
text = re.sub(r'\n{3,}', '\n\n', text)
text = '# Prólogo — O Passageiro de 1824\n\n'+text
parts = re.split(r'(?m)(?=^# )', text)
parts = [p.strip()+'\n' for p in parts if p.strip()]
assert len(parts)==16
for dirname in ['base','capitulos']:
    (ed/dirname).mkdir(exist_ok=True)
for i,p in enumerate(parts): (ed/'base'/f'{i:02}.md').write_text(p,encoding='utf-8')
changes=[]
def change(old,new,reason,kind='preparação',chapter=None):
    global parts
    found=0
    for i,p in enumerate(parts):
        if chapter is not None and chapter!=i: continue
        n=p.count(old)
        if n:
            parts[i]=p.replace(old,new)
            changes.append({'capitulo':i,'tipo':kind,'motivo':reason,'antes':old,'depois':new,'ocorrencias':n})
            found+=n
    if not found: raise ValueError('Trecho ausente: '+old)

change('Oliver Glauiel','Oliver Glauier','Grafia predominante do sobrenome.')
change('Luna','Luana','Grafia predominante; mesma parceira de Maia.')
change('Natã','Natan','Grafia predominante do personagem.')
change('Rio dos Sinos','rio dos Sinos','Nome do rio; substantivo geográfico em minúscula.')
change('casarão estilo castelo histórico do século XIX','casarão histórico do século XIX, em estilo de castelo','Clareza da descrição arquitetônica.')
change('Seus olhos sempre fixos na linha do horizonte nublado carregavam o cansaço de quem carregava um segredo pesado demais para as forças humanas.','Seus olhos, sempre fixos na linha do horizonte nublado, revelavam o cansaço de quem carregava um segredo pesado demais para as forças humanas.','Pontuação e repetição de carregavam/carregava.')
change('A lógica, porém, havia abandonado aquele casarão em 1824.','A lógica, porém, havia abandonado aquele lugar com a chegada de Johann, em 1824.','O casarão só foi construído anos depois.','continuidade')
change('Dispostas em um semicírculo perfeito no chão do salão e ali estavam as estátuas.','Ali estavam as estátuas, dispostas em um semicírculo no chão do salão.','Reparação da sintaxe.')
change('No centro daquele semicírculo de pedra e gesso','No centro daquele semicírculo de barro e gesso','Materiais das estátuas.','continuidade')
change('seu poder combinado', 'seu poder combinado','Sem alteração') if False else None
change('afinal, as contas','afinal, as contas','Sem alteração') if False else None
change('como se tudo estivesse normal, afinal, as contas','como se tudo estivesse normal. Afinal, as contas','Separação de períodos.')
change('No momento em que fez,','No momento em que fez isso,','Complemento do verbo.')
change('O poder combinado de Emanuel e a barreira mística de Mateus foram suficientes','O poder de Emanuel e a barreira mística de Mateus foram suficientes','Paralelismo sintático.')
change('Não por escolha mística do passado, mas porque o presente os estava forçando','O chamado do passado os reunira, e o presente os estava forçando','A seleção mística é explícita no capítulo anterior.','continuidade')
change('havia mais sete pessoas.','havia mais seis pessoas.','Seis no campus e seis no portão: doze pessoas.','continuidade')
change('Era Oliver Glauier, acompanhado por Andressa.','Era Oliver Glauier, acompanhado pela esposa, Flora Rosana.','Identidade e casamento confirmados pelo autor.','decisão autoral')
change('Ao lado deles, Gustavo Henrique e Ágata acenaram com a cabeça.','Ao lado deles, Gustavo Henrique e Ágata Maressa acenaram com a cabeça.','Apresentação do nome completo.')
change('No canto, Gabriela e Flora carregavam bolsas com ervas e frascos místicos, preparadas para o pior, enquanto Rosana, uma mulher de olhar profundo e mãos sujas da poeira branca, observava as paredes do casarão como se pudesse ler sua alma.','No canto, Gabriela e Andressa carregavam bolsas com ervas e frascos místicos, preparadas para o pior. Flora Rosana, uma mulher de olhar profundo e mãos sujas de poeira branca, observava as paredes do casarão como se pudesse ler sua alma.','Unificar Flora Rosana e preservar Gabriela e Andressa, sem criar vínculo amoroso entre elas.','decisão autoral')
change('as quatorze pessoas','as doze pessoas','Contagem das pessoas nomeadas.','continuidade')
change('Rosana caminhou até elas','Flora Rosana caminhou até elas','Identidade confirmada.','decisão autoral')
change('cada um dos doze guerreiros ali presentes','cada um dos dez companheiros ali presentes','Doze integrantes, dos quais dois líderes.','continuidade')
change('Oliver e Andressa, vocês','Oliver e Flora, vocês','Missão investigativa do casal confirmado.','decisão autoral')
change('Gabriela e Flora cuidam dos feridos. E Rosana... você','Gabriela e Andressa cuidam dos feridos. E Flora... você','Distribuir as tarefas sem duplicar Flora Rosana.','decisão autoral')
change('Os doze defensores olharam','Os dez defensores olharam','Seguidores além dos dois líderes.','continuidade')
change('o quarto casal trabalhava incansavelmente','Oliver e Flora Rosana trabalhavam incansavelmente','Evitar ordinal incompatível com a composição do grupo.','continuidade')
change('Ela não olhou para o portal de argila batida e segurou a mão direita dele, entrelaçando seus dedos.','Ela se aproximou de Emanuel sobre o chão de argila batida e segurou a mão direita dele, entrelaçando os dedos.','Reparação de frase e posição do chão; ligação local.','complementação local')
change('O Conselho dos Quatro Casais','O Conselho da Sociedade','Há cinco casais e duas integrantes de apoio.','continuidade')
change('O salão infinito o salão infinito','O salão infinito','Duplicação acidental.')
change('É por isso que a sociedade é feita de casais. A cumplicidade e o amor entre vocês são as nossas maiores armas','É por isso que tantos de nós fomos chamados em pares. A cumplicidade e o amor entre nós são as nossas maiores armas','Preservar os casais e incluir as duas integrantes sem par declarado.','continuidade')
change('Eles finalmente entenderam por que a natureza os havia escolhido em pares.','Eles finalmente entenderam a força dos laços que os reuniam.','Evitar atribuir um par não documentado a Gabriela e Andressa.','continuidade')
change('ele dividiu a essência da chave em um artefato místico. Ele escondeu a primeira parte desse artefato no lugar de onde fugiu:','ele dividiu a essência da chave entre três relíquias místicas. Escondeu a primeira no lugar de onde fugiu:','Três peças confirmadas nos capítulos posteriores.','continuidade')
change('Para conseguir contê-la temporariamente enquanto construía o casarão,','Para conseguir contê-la temporariamente durante a travessia e a construção do casarão,','Divisão da chave deve anteceder a partida.','continuidade')
change('selar a primeira das três conexões globais. Para sempre.','enfraquecer a primeira das três conexões globais. As três relíquias reunidas nos permitirão selar as rotas da sombra.','O retorno é sabotado antes da reunião das três peças.','continuidade')
change('depois para seus doze guerreiros','depois para seus dez companheiros','Número de seguidores.','continuidade')
change('Ele então olhou para o quarto casal e depois para sua esposa.','Ele então olhou para Oliver e Flora e depois para sua esposa.','Ordinal removido.','continuidade')
change('Mateus, Natan, Luana, Maia, Gustavo Henrique e Ágata Maressa... vocês ficam.','Mateus, Natan, Luana, Maia, Gustavo Henrique, Ágata Maressa, Gabriela e Andressa... vocês ficam.','Oito ficam; quatro viajam.','continuidade')
change('Gabriela e Flora haviam preparado','Gabriela e Andressa haviam preparado','Coerência da equipe de apoio.','continuidade')
dup='— As paredes... elas não são de pedra comum — observou Oliver, tocando o relevo escuro do corredor subterrâneo. — Isso é argila misturada com minério de ferro antigo. É o mesmo material do nosso casarão no Vale dos Sinos. Mas corrompido pelo tempo.\n\n'
change(dup,'','Remover repetição integral imediatamente seguida por versão equivalente.')
change('No centro do salão, livre de seus protetores,','No centro do salão, sem seus guardiões,','Clareza do referente.')
change('o primeiro round na Europa','o primeiro confronto na Europa','Registro narrativo em português.')
change('e transformando-se em um turbilhão violeta caótico.','transformando-se em um turbilhão violeta caótico.','Construção sintática.')
change('olhando para os outros três casais','olhando para os outros defensores','Mateus integra um dos três casais que ficaram; há duas auxiliares.','continuidade')
change('projetar ondas de choque sísmicas','projetar ondas de choque sísmicas','Sem alteração') if False else None
change('gerou uma faísca direto na pólvora centenária.','gerou uma faísca que atingiu os explosivos centenários.','Dinamite não é chamada de pólvora.')
change('disparando sua lanterna em direção','apontando sua lanterna em direção','Precisão lexical.')
change('a segunda relíquia de gesso e ferro','a segunda relíquia','Nevada tem gesso e ouro.','continuidade')
change('aproximando as lentes de seus óculos de uma parede de metal.','aproximando-se de uma parede de metal para examinar os símbolos.','Ação fisicamente clara.')
change('desenhou em seu diário em 1824','registrou em seu diário','A cidade americana pode ser posterior; diário não limitado a 1824.','continuidade')
change('A lógica, porém','A lógica, porém','Sem alteração') if False else None
change('Rezando para que o destino final os levasse de volta para os braços da sociedade secreta no Rio Grande do Sul.','Ela torcia para que o destino final os levasse de volta aos companheiros da sociedade secreta no Rio Grande do Sul.','Reparação do fragmento; sujeito explícito.')
change('ela arrancou a coroa','ela arrancou a coroa','Sem alteração') if False else None
change('Jade, Oliver e Flora ergueram-se sob uma nevasca','Os quatro ergueram-se sob uma nevasca','Emanuel também chegou à Sibéria.','continuidade')
change('No mesmo milésimo de segundo em que o casal pisou','No mesmo instante em que o grupo pisou','Quatro viajantes.','continuidade')
change('o formato que desafiava a biologia','o formato de uma coroa que parecia desafiar as leis da matéria','A peça seguinte é uma coroa.','continuidade')
change('toda a sua força de seu casamento e de seu poder','toda a força de seu poder e do laço que o unia a Jade','Sintaxe e redução da repetição.')
change('Os quatro casais defensores gritaram','Os oito defensores gritaram','Três casais e duas auxiliares ficaram no Brasil.','continuidade')
change('os sete casais reunidos','os companheiros reunidos','Cinco casais e duas auxiliares.','continuidade')
change('— Casais, preparem-se!','— Defensores, preparem-se!','Comando abrange todos os integrantes.','continuidade')
change('desabou o casarão','desabou sobre o casarão','Preposição ausente.')
change('fazendo colidirem uns contra os outros','fazendo-os colidir uns contra os outros','Regência e pronome.')
change('As estátuas de pedra empunharam','As estátuas de gesso e barro empunharam','Materiais estabelecidos.','continuidade')
change('focando toda energia purificadora','concentrando toda a energia purificadora','Artigo e precisão lexical.')
change('“Pela terra, pelo sul e pelo nosso amanhã!”, suas vozes ecoaram em uníssono.','— Pela terra, pelo sul e pelo nosso amanhã! — Suas vozes ecoaram em uníssono.','Padronização da fala em travessão.')
change('Os oito casais se reuniram ao redor da mesa de argila central.','Os cinco casais, Gabriela e Andressa se reuniram ao redor da mesa de argila central.','Doze pessoas preservadas no desfecho.','continuidade')
change('a maior lenda que o mundo jamais esqueceria.','uma lenda que os guardiões jamais esqueceriam.','A população desconhece os acontecimentos; manter a vitória secreta.','continuidade')
change('se expandiu, tocando','se expandiu, tocando','Sem alteração') if False else None
# Complementações pontuais para rastrear o apoio durante a ausência dos viajantes.
change('— Nós não podemos desistir — declarou Mateus,','Gabriela e Andressa recolhiam os feridos para junto da mesa, mantendo os frascos de seiva ao alcance dos defensores.\n\n— Nós não podemos desistir — declarou Mateus,','Dar continuidade à função de apoio já atribuída.','complementação local',10)
change('Eles compraram o imóvel naquela mesma semana.','Eles compraram o imóvel naquela mesma semana. O preço baixo tornou possível o que, até então, parecera fora de alcance.','Ligação mínima com a situação financeira já apresentada.','complementação local',1)
change('uma aliança de casamento', 'uma aliança de casamento','Sem alteração') if False else None
change('Para dois estudantes universitários que tentavam equilibrar as contas','Para Emanuel e Jade, um casal de estudantes universitários que tentava equilibrar as contas','Apresentar o casal já estabelecido nas alianças posteriores.','continuidade',1)
change('Oliver e Flora Rosana trabalhavam incansavelmente. Oliver Glauier e Flora Rosana estavam cercados','Oliver Glauier e Flora Rosana trabalhavam incansavelmente, cercados','Reduzir repetição dos nomes.',chapter=5)
change('Se eles conseguirem, a Terra','Se a sombra conseguir, a Terra','Referente da ameaça é a névoa.',chapter=6)
change('## Parte 1\n','## Parte 1 — Os Preparativos\n','Título da parte coerente com a cena.',chapter=7)
change('Jade Hadassa aproximou-se. Ela se aproximou de Emanuel sobre o chão de argila batida e segurou','Jade Hadassa caminhou até Emanuel sobre o chão de argila batida e segurou','Evitar repetição criada ao reparar a frase.',chapter=5)
change('simultaneamente.\n\nSe a névoa','simultaneamente. Se a névoa','Reunir continuação da fala de Oliver na virada da folha.',chapter=5)
change('Eles não pareciam se reconhecer, mas todos','Alguns pareciam desconhecidos entre si, mas todos','Os casais já se conhecem.','continuidade',4)
change('Três dias haviam passado desde a descoberta','Dois dias haviam passado desde a descoberta','Descoberta/chamado na terça-feira; ataque na quinta-feira.','continuidade',3)

for i,p in enumerate(parts):
    (ed/'capitulos'/f'{i:02}.md').write_text(p,encoding='utf-8')
    target=root/'editorial'/'comparacao'; target.mkdir(exist_ok=True)
    base=(ed/'base'/f'{i:02}.md').read_text(encoding='utf-8')
    (target/f'{i:02}.diff').write_text(''.join(difflib.unified_diff(base.splitlines(True),p.splitlines(True),fromfile=f'base/{i:02}.md',tofile=f'capitulos/{i:02}.md')),encoding='utf-8')
full='# Ecos da Névoa\n\n## O Segredo de 1824\n\nVorne Ermel\n\n'+'\n'.join(parts)
(ed/'livro-revisado.md').write_text(full,encoding='utf-8')
(root/'editorial'/'alteracoes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
rows=['# Alterações — edição v1','', '03/10/2026. Originais e transcrições preservados. Cada registro localiza capítulo (0 = prólogo; 15 = epílogo), tipo e decisão.','']
for n,c in enumerate(changes,1):
    rows += [f"## {n:03} — Seção {c['capitulo']:02}: {c['tipo']}",'',c['motivo'],'',f"Antes: {c['antes']}",'',f"Depois: {c['depois'] or '[repetição removida]'}",'']
(root/'editorial'/'alteracoes.md').write_text('\n'.join(rows),encoding='utf-8')
counts={'folhas_transcritas':53,'secoes':16,'registros':len(changes),'ocorrencias':sum(c['ocorrencias'] for c in changes),'palavras_base':sum(len(re.findall(r'\S+',p.read_text(encoding='utf-8'))) for p in (ed/'base').glob('*.md')),'palavras_revisadas':sum(len(re.findall(r'\S+',p)) for p in parts)}
(root/'editorial'/'contagens.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(counts,ensure_ascii=False))
