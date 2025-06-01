from flask import Flask, render_template, request, session, redirect, url_for
from rdflib import Graph, Namespace
import random
import requests
import random

app = Flask(__name__)
app.secret_key = "chave_secreta_para_sessao"  # deve ser segura em produção


# Namespaces e grafo
EX = Namespace("http://example.org/jogos#")
g = Graph()
g.parse("games.ttl", format="turtle")

def get_top_labels(property_uri, direction="inverse"):
    """
    Retorna 5 amostras aleatórias dos top 20 recursos mais associados a jogos.
    """
    if direction == "inverse":
        query = f'''
        SELECT ?ent (COUNT(?jogo) AS ?total) WHERE {{
            ?jogo <{property_uri}> ?ent .
        }} GROUP BY ?ent ORDER BY DESC(?total) LIMIT 20
        '''
    else:
        query = f'''
        SELECT ?ent (COUNT(?jogo) AS ?total) WHERE {{
            ?ent <{property_uri}> ?jogo .
        }} GROUP BY ?ent ORDER BY DESC(?total) LIMIT 20
        '''
    top_results = list(g.query(query))
    sample = random.sample(top_results, min(5, len(top_results)))
    return [{"nome": str(row.ent).split("#")[-1], "id": str(row.ent).split("#")[-1]} for row in sample]

def get_google_image_url(entity_name):
    params = {
        "q": entity_name,
        "tbm": "isch",
        "ijn": "0",
        "api_key": "581026fbc122969ca890ba25d60c0e78048d3f818ef4a5234fe4e55fc9490578"
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    try:
        return data["images_results"][0]["original"]
    except (KeyError, IndexError):
        return None


def gerar_pergunta():
    tipos = [
        "jogo_por_publicador",
        "jogo_por_desenvolvedor",
        "jogo_por_genero",
        "jogo_por_data",
        "publicador_por_jogo",
        "desenvolvedor_por_jogo",
        "genero_por_jogo",
        "data_por_jogo"
    ]
    
    tipo = random.choice(tipos)

    # Amostra de jogos
    jogos = list(g.query(f'''
        SELECT ?jogo ?titulo WHERE {{
            ?jogo a <{EX.Jogo}> ;
                   <{EX.temTitulo}> ?titulo .
        }}
    '''))
    
    if not jogos:
        return {"pergunta": "Sem dados", "resposta_correta": "", "opcoes": []}

    jogo_escolhido = random.choice(jogos)
    jogo_uri = str(jogo_escolhido.jogo)
    jogo_id = jogo_uri.split("#")[-1]
    titulo = str(jogo_escolhido.titulo)

    # Função auxiliar
    def get_labels(predicate, direction="inverse"):
        query = f'''
        SELECT DISTINCT ?ent WHERE {{
            {'?x <' + predicate + '> ?ent .' if direction == "inverse" else '?ent <' + predicate + '> ?x .'}
        }}
        '''
        return [str(row.ent).split("#")[-1] for row in g.query(query)]

    def opcoes_aleatorias(lista, correta):
        lista_unica = list(set(lista) - {correta})
        opcoes = random.sample(lista_unica, min(3, len(lista_unica)))
        opcoes.append(correta)
        return random.sample(opcoes, len(opcoes))

    # Perguntas do tipo "Qual jogo foi X por Y?"
    if tipo == "jogo_por_publicador":
        query = f'''
        SELECT ?pub WHERE {{
            <{EX[jogo_id]}> <{EX.foiPublicadoPor}> ?pub .
        }}
        '''
        pubs = [str(r.pub).split("#")[-1] for r in g.query(query)]
        if not pubs: return gerar_pergunta()
        pub = random.choice(pubs)
        candidatos = [str(j.titulo) for j in jogos if j.titulo != titulo]
        opcoes = opcoes_aleatorias(candidatos, titulo)
        return {
            "pergunta": f"Qual dos seguintes jogos foi publicado por {pub.replace('_', ' ')}?",
            "resposta_correta": titulo,
            "opcoes": opcoes
        }

    if tipo == "jogo_por_desenvolvedor":
        query = f'''
        SELECT ?dev WHERE {{
            <{EX[jogo_id]}> <{EX.foiDesenvolvidoPor}> ?dev .
        }}
        '''
        devs = [str(r.dev).split("#")[-1] for r in g.query(query)]
        if not devs: return gerar_pergunta()
        dev = random.choice(devs)
        candidatos = [str(j.titulo) for j in jogos if j.titulo != titulo]
        opcoes = opcoes_aleatorias(candidatos, titulo)
        return {
            "pergunta": f"Qual dos seguintes jogos foi desenvolvido por {dev.replace('_', ' ')}?",
            "resposta_correta": titulo,
            "opcoes": opcoes
        }

    if tipo == "jogo_por_genero":
        query = f'''
        SELECT ?gen WHERE {{
            <{EX[jogo_id]}> <{EX.pertenceAoGenero}> ?gen .
        }}
        '''
        generos = [str(r.gen).split("#")[-1] for r in g.query(query)]
        if not generos: return gerar_pergunta()
        genero = random.choice(generos)
        candidatos = [str(j.titulo) for j in jogos if j.titulo != titulo]
        opcoes = opcoes_aleatorias(candidatos, titulo)
        return {
            "pergunta": f"Qual dos seguintes jogos pertence ao género {genero.replace('_', ' ')}?",
            "resposta_correta": titulo,
            "opcoes": opcoes
        }

    if tipo == "jogo_por_data":
        query = f'''
        SELECT ?data WHERE {{
            <{EX[jogo_id]}> <{EX.anoDeLancamento}> ?data .
        }}
        '''
        datas = [str(r.data) for r in g.query(query)]
        if not datas: return gerar_pergunta()
        data = datas[0]
        candidatos = [str(j.titulo) for j in jogos if j.titulo != titulo]
        opcoes = opcoes_aleatorias(candidatos, titulo)
        return {
            "pergunta": f"Qual dos seguintes jogos foi lançado em {data}?",
            "resposta_correta": titulo,
            "opcoes": opcoes
        }

    # Perguntas inversas: Qual entidade X está associada ao jogo Y?

    if tipo == "publicador_por_jogo":
        query = f'''
        SELECT ?pub WHERE {{
            <{EX[jogo_id]}> <{EX.foiPublicadoPor}> ?pub .
        }}
        '''
        pubs = [str(r.pub).split("#")[-1] for r in g.query(query)]
        if not pubs: return gerar_pergunta()
        pub = random.choice(pubs)
        candidatos = get_labels(EX.foiPublicadoPor)
        opcoes = opcoes_aleatorias(candidatos, pub)
        return {
            "pergunta": f"Qual das publicadoras publicou o jogo {titulo}?",
            "resposta_correta": pub.replace('_', ' '),
            "opcoes": [o.replace('_', ' ') for o in opcoes]
        }

    if tipo == "desenvolvedor_por_jogo":
        query = f'''
        SELECT ?dev WHERE {{
            <{EX[jogo_id]}> <{EX.foiDesenvolvidoPor}> ?dev .
        }}
        '''
        devs = [str(r.dev).split("#")[-1] for r in g.query(query)]
        if not devs: return gerar_pergunta()
        dev = random.choice(devs)
        candidatos = get_labels(EX.foiDesenvolvidoPor)
        opcoes = opcoes_aleatorias(candidatos, dev)
        return {
            "pergunta": f"Qual dos desenvolvedores criou o jogo {titulo}?",
            "resposta_correta": dev.replace('_', ' '),
            "opcoes": [o.replace('_', ' ') for o in opcoes]
        }

    if tipo == "genero_por_jogo":
        query = f'''
        SELECT ?gen WHERE {{
            <{EX[jogo_id]}> <{EX.pertenceAoGenero}> ?gen .
        }}
        '''
        generos = [str(r.gen).split("#")[-1] for r in g.query(query)]
        if not generos: return gerar_pergunta()
        genero = random.choice(generos)
        candidatos = get_labels(EX.pertenceAoGenero)
        opcoes = opcoes_aleatorias(candidatos, genero)
        return {
            "pergunta": f"Qual o género do jogo {titulo}?",
            "resposta_correta": genero.replace('_', ' '),
            "opcoes": [o.replace('_', ' ') for o in opcoes]
        }

    if tipo == "data_por_jogo":
        query = f'''
        SELECT ?data WHERE {{
            <{EX[jogo_id]}> <{EX.anoDeLancamento}> ?data .
        }}
        '''
        datas = [str(r.data) for r in g.query(query)]
        if not datas: return gerar_pergunta()
        data = datas[0]
        datas_fake = [str(r.data) for r in g.query(f'''
            SELECT DISTINCT ?data WHERE {{
                ?jogo <{EX.anoDeLancamento}> ?data .
                FILTER (?data != "{data}")
            }}
        ''')]
        opcoes = opcoes_aleatorias(datas_fake, data)
        return {
            "pergunta": f"Qual a data de lançamento de {titulo}?",
            "resposta_correta": data,
            "opcoes": opcoes
        }

    return {"pergunta": "Erro ao gerar pergunta.", "resposta_correta": "", "opcoes": []}

# Adiciona nova funcao para obter todas as entidades sem limite

def get_all_labels(property_uri, direction="inverse"):
    if direction == "inverse":
        query = f'''
        SELECT DISTINCT ?ent WHERE {{
            ?jogo <{property_uri}> ?ent .
        }}
        '''
    else:
        query = f'''
        SELECT DISTINCT ?ent WHERE {{
            ?ent <{property_uri}> ?jogo .
        }}
        '''

    resultados = list(g.query(query))
    return [{
        "nome": str(row.ent).split("#")[-1],
        "id": str(row.ent).split("#")[-1]
    } for row in resultados]

# Rota para todas as plataformas
@app.route("/plataformas")
def todas_plataformas():
    plataformas = get_all_labels(EX.disponivelEm)
    return render_template("lista_generica.html", 
                         title="Todas as Plataformas",
                         items=plataformas,
                         entity_type="plataforma")

# Rota para todos os generos
@app.route("/generos")
def todos_generos():
    generos = get_all_labels(EX.pertenceAoGenero)
    return render_template("lista_generica.html",
                         title="Todos os Géneros", 
                         items=generos,
                         entity_type="genero")

# Rota para todas as desenvolvedoras
@app.route("/desenvolvedoras")
def todas_desenvolvedoras():
    desenvolvedoras = get_all_labels(EX.foiDesenvolvidoPor)
    return render_template("lista_generica.html",
                         title="Todas as Desenvolvedoras",
                         items=desenvolvedoras, 
                         entity_type="desenvolvedora")

# Rota para todos os publicadores
@app.route("/publicadores")
def todos_publicadores():
    publicadores = get_all_labels(EX.foiPublicadoPor)
    return render_template("lista_generica.html",
                         title="Todos os Publicadores",
                         items=publicadores,
                         entity_type="publicador")

# Rota para todos os jogos
@app.route("/jogos")
def todos_jogos():
    query = f'''
    SELECT ?jogo ?titulo WHERE {{
        ?jogo a <{EX.Jogo}> ;
              <{EX.temTitulo}> ?titulo .
    }}
    '''
    jogos = [{
        "id": str(row.jogo).split("#")[-1],
        "titulo": str(row.titulo)
    } for row in g.query(query)]

    return render_template("lista_generica.html",
                         title="Todos os Jogos",
                         items=jogos,
                         entity_type="jogo")

@app.route("/")
def index():
    # Jogos com título
    query_jogos = f'''
    SELECT ?jogo ?titulo WHERE {{
        ?jogo a <{EX.Jogo}> ;
              <{EX.temTitulo}> ?titulo .
    }}
    '''
    jogos_raw = list(g.query(query_jogos))
    jogos_sample = random.sample(jogos_raw, min(5, len(jogos_raw)))
    jogos = [{
        "uri": str(j.jogo),
        "id": str(j.jogo).split("#")[-1],
        "titulo": str(j.titulo)
    } for j in jogos_sample]

    plataformas = get_top_labels(EX.disponivelEm)
    generos = get_top_labels(EX.pertenceAoGenero)
    publicadores = get_top_labels(EX.foiPublicadoPor)
    desenvolvedoras = get_top_labels(EX.foiDesenvolvidoPor)



    return render_template("index.html", jogos=jogos, plataformas=plataformas, generos=generos, publicadores=publicadores, desenvolvedoras=desenvolvedoras)

@app.route("/jogo/<jogo_id>")
def jogo_detail(jogo_id):
    jogo_uri = EX[jogo_id]
    
    query = f'''
    SELECT ?titulo ?data ?descricao WHERE {{
        <{jogo_uri}> <{EX.temTitulo}> ?titulo .
        OPTIONAL {{ <{jogo_uri}> <{EX.anoDeLancamento}> ?data }}
        OPTIONAL {{ <{jogo_uri}> <{EX.temDescricao}> ?descricao}}
    }}
    '''
    result = list(g.query(query))
    if not result:
        return "Jogo não encontrado", 404

    titulo = result[0].titulo
    data = result[0].data if hasattr(result[0], 'data') else "?"
    descricao = result[0].descricao if hasattr(result[0], 'descricao') else "N/A"

    # Géneros
    query_generos = f'''
    SELECT ?g WHERE {{
        <{jogo_uri}> <{EX.pertenceAoGenero}> ?g .
    }}
    '''
    generos = [str(row.g).split("#")[-1] for row in g.query(query_generos)]

    # Plataformas
    query_plataformas = f'''
    SELECT ?p WHERE {{
        <{jogo_uri}> <{EX.disponivelEm}> ?p .
    }}
    '''
    plataformas = [str(row.p).split("#")[-1] for row in g.query(query_plataformas)]

    # Publicadores
    query_pubs = f'''
        SELECT ?pub WHERE {{
            <{jogo_uri}> <{EX.foiPublicadoPor}> ?pub .
        }}
    '''
    publicadores = [str(row.pub).split("#")[-1] for row in g.query(query_pubs)]

    # Desenvolvedoras
    query_devs = f'''
    SELECT ?d WHERE {{
        <{jogo_uri}> <{EX.foiDesenvolvidoPor}> ?d .
    }}
    '''
    desenvolvedoras = [str(row.d).split("#")[-1] for row in g.query(query_devs)]

    image_url = get_google_image_url(jogo_id)

    return render_template(
        "jogo.html",
        id=jogo_id,
        titulo=titulo,
        data=data,
        descricao=descricao,
        generos=generos,
        plataformas=plataformas,
        publicadores=publicadores,
        desenvolvedoras=desenvolvedoras,
        image_url=image_url
    )


@app.route("/plataforma/<plataforma_id>")
def plataforma_detail(plataforma_id):
    uri = EX[plataforma_id]
    query = f'''
    SELECT ?jogo ?titulo WHERE {{
        ?jogo <{EX.disponivelEm}> <{uri}> ;
              <{EX.temTitulo}> ?titulo .
    }}
    '''
    jogos = [{
        "id": str(row.jogo).split("#")[-1],
        "titulo": str(row.titulo)
    } for row in g.query(query)]

    image_url = get_google_image_url(plataforma_id)

    return render_template("detalhe_generico.html", 
                         id=plataforma_id, 
                         jogos=jogos, 
                         image_url=image_url,
                         entity_label="Plataforma",
                         entity_label_lower="da plataforma",
                         games_section_title="Jogos disponíveis")

@app.route("/genero/<genero_id>")
def genero_detail(genero_id):
    uri = EX[genero_id]
    query = f'''
    SELECT ?jogo ?titulo WHERE {{
        ?jogo <{EX.pertenceAoGenero}> <{uri}> ;
              <{EX.temTitulo}> ?titulo .
    }}
    '''
    jogos = [{
        "id": str(row.jogo).split("#")[-1],
        "titulo": str(row.titulo)
    } for row in g.query(query)]

    image_url = get_google_image_url(genero_id)

    return render_template("detalhe_generico.html", 
                         id=genero_id, 
                         jogos=jogos, 
                         image_url=image_url,
                         entity_label="Género",
                         entity_label_lower="do género",
                         games_section_title="Jogos do género")


@app.route("/publicador/<publicador_id>")
def publicador_detail(publicador_id):
    uri = EX[publicador_id]
    query = f'''
    SELECT ?jogo ?titulo WHERE {{
        ?jogo <{EX.foiPublicadoPor}> <{uri}> ;
              <{EX.temTitulo}> ?titulo .
    }}
    '''
    jogos = [{
        "id": str(row.jogo).split("#")[-1],
        "titulo": str(row.titulo)
    } for row in g.query(query)]

    image_url = get_google_image_url(publicador_id)

    return render_template("detalhe_generico.html", 
                         id=publicador_id, 
                         jogos=jogos, 
                         image_url=image_url,
                         entity_label="Publicador",
                         entity_label_lower="do publicador",
                         games_section_title="Jogos publicados")

app.route("/desenvolvedora/<desenvolvedora_id>")
def desenvolvedora_detail(desenvolvedora_id):
    uri = EX[desenvolvedora_id]
    query = f'''
    SELECT ?jogo ?titulo WHERE {{
        ?jogo <{EX.foiDesenvolvidoPor}> <{uri}> ;
              <{EX.temTitulo}> ?titulo .
    }}
    '''
    jogos = [{
        "id": str(row.jogo).split("#")[-1],
        "titulo": str(row.titulo)
    } for row in g.query(query)]

    image_url = get_google_image_url(desenvolvedora_id)

    return render_template("detalhe_generico.html", 
                         id=desenvolvedora_id, 
                         jogos=jogos, 
                         image_url=image_url,
                         entity_label="Desenvolvedora",
                         entity_label_lower="da desenvolvedora",
                         games_section_title="Jogos desenvolvidos")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    # Inicializa contadores se não existirem
    if "corretas" not in session:
        session["corretas"] = 0
    if "erradas" not in session:
        session["erradas"] = 0

    if request.method == "POST":
        pergunta = request.form["pergunta"]
        resposta_correta = request.form["resposta_correta"]
        resposta_dada = request.form.get("resposta")

        correta = (resposta_dada == resposta_correta)
        if correta:
            session["corretas"] += 1
        else:
            session["erradas"] += 1

        return render_template(
            "quiz.html",
            pergunta=pergunta,
            opcoes=[],
            resposta_correta=resposta_correta,
            resposta_dada=resposta_dada,
            correta=correta,
            mostrar_resultado=True,
            corretas=session["corretas"],
            erradas=session["erradas"]
        )

    q = gerar_pergunta()
    return render_template(
        "quiz.html",
        pergunta=q["pergunta"],
        opcoes=q["opcoes"],
        resposta_correta=q["resposta_correta"],
        mostrar_resultado=False,
        corretas=session["corretas"],
        erradas=session["erradas"]
    )

@app.route("/quiz/reset")
def quiz_reset():
    session["corretas"] = 0
    session["erradas"] = 0
    return redirect(url_for('quiz'))

@app.route("/pesquisa")
def pesquisar_jogos():
    termo = request.args.get("q", "").lower()

    query = f'''
    SELECT ?jogo ?titulo WHERE {{
        ?jogo a <{EX.Jogo}> ;
              <{EX.temTitulo}> ?titulo .
        FILTER(CONTAINS(lcase(str(?titulo)), "{termo}"))
    }}
    '''
    resultados = [{
        "id": str(row.jogo).split("#")[-1],
        "titulo": str(row.titulo)
    } for row in g.query(query)]

    return render_template("lista_generica.html", 
                         title="Resultados da Pesquisa",
                         items=resultados, 
                         entity_type="jogo",
                         pesquisa=termo)


if __name__ == '__main__':
    app.run(debug=True)
