import json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, OWL
from urllib.parse import urlparse
import re

OUTPUT_FILE = "games"

# Função utilitária para obter apenas o nome local da URI
def uri_to_local(uri):
    local = uri.split("/")[-1]
    local = local.replace(" ", "_").replace("'", "").replace("\"", "")
    return re.sub(r"[^\w]", "_", local)

# Carregar dados
with open('dataset_final.json', 'r') as f:
    jogos = json.load(f)

# Namespaces
EX = Namespace("http://example.org/jogos#")
g = Graph()
g.bind("", EX)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)
g.bind("owl", OWL)

### 1. DEFINIÇÃO DA ONTOLOGIA ###

# Classes
g.add((EX.Jogo, RDF.type, OWL.Class))
g.add((EX.Plataforma, RDF.type, OWL.Class))
g.add((EX.Genero, RDF.type, OWL.Class))
g.add((EX.Desenvolvedora, RDF.type, OWL.Class))
g.add((EX.Publicador, RDF.type, OWL.Class))


# Object Properties para desenvolvedor
g.add((EX.foiDesenvolvidoPor, RDF.type, OWL.ObjectProperty))
g.add((EX.foiDesenvolvidoPor, RDFS.domain, EX.Jogo))
g.add((EX.foiDesenvolvidoPor, RDFS.range, EX.Desenvolvedora))

g.add((EX.desenvolveu, RDF.type, OWL.ObjectProperty))
g.add((EX.desenvolveu, RDFS.domain, EX.Desenvolvedora))
g.add((EX.desenvolveu, RDFS.range, EX.Jogo))

# Object Properties para genero
g.add((EX.pertenceAoGenero, RDF.type, OWL.ObjectProperty))
g.add((EX.pertenceAoGenero, RDFS.domain, EX.Jogo))
g.add((EX.pertenceAoGenero, RDFS.range, EX.Genero))

g.add((EX.temJogo, RDF.type, OWL.ObjectProperty))
g.add((EX.temJogo, RDFS.domain, EX.Genero))
g.add((EX.temJogo, RDFS.range, EX.Jogo))

# Object Properties para plataforma
g.add((EX.disponivelEm, RDF.type, OWL.ObjectProperty))
g.add((EX.disponivelEm, RDFS.domain, EX.Jogo))
g.add((EX.disponivelEm, RDFS.range, EX.Plataforma))

g.add((EX.suporta, RDF.type, OWL.ObjectProperty))
g.add((EX.suporta, RDFS.domain, EX.Plataforma))
g.add((EX.suporta, RDFS.range, EX.Jogo))

# Object Properties para publicador
g.add((EX.foiPublicadoPor, RDF.type, OWL.ObjectProperty))
g.add((EX.foiPublicadoPor, RDFS.domain, EX.Jogo))
g.add((EX.foiPublicadoPor, RDFS.range, EX.Publicador))

g.add((EX.publicou, RDF.type, OWL.ObjectProperty))
g.add((EX.publicou, RDFS.domain, EX.Publicador))
g.add((EX.publicou, RDFS.range, EX.Jogo))


# Datatype Properties
g.add((EX.temTitulo, RDF.type, OWL.DatatypeProperty))
g.add((EX.temTitulo, RDFS.domain, EX.Jogo))
g.add((EX.temTitulo, RDFS.range, XSD.string))

g.add((EX.anoDeLancamento, RDF.type, OWL.DatatypeProperty))
g.add((EX.anoDeLancamento, RDFS.domain, EX.Jogo))
g.add((EX.anoDeLancamento, RDFS.range, XSD.date))

g.add((EX.temDescricao, RDF.type, OWL.DatatypeProperty))
g.add((EX.temDescricao, RDFS.domain, EX.Jogo))
g.add((EX.temDescricao, RDFS.range, XSD.string))

### 2. INSTÂNCIAS ###

jogos_adicionados = set()
generos_adicionados = set()
plataformas_adicionadas = set()
desenvolvedores_adicionados = set()
publicadores_adicionados = set()


for jogo in jogos:
    jogo_id = uri_to_local(jogo["id"])
    jogo_uri = EX[jogo_id]

    if jogo_id not in jogos_adicionados and jogo_id:
        g.add((jogo_uri, RDF.type, EX.Jogo))
        if "titulo" in jogo and jogo["titulo"]:
            g.add((jogo_uri, EX.temTitulo, Literal(jogo["titulo"], lang="en")))
        if "data" in jogo and jogo["data"]:
            g.add((jogo_uri, EX.anoDeLancamento, Literal(jogo["data"], datatype=XSD.date)))
        if "descricao" in jogo and jogo["descricao"]:
            g.add((jogo_uri, EX.temDescricao, Literal(jogo["descricao"], lang="en")))

        jogos_adicionados.add(jogo_id)

    # Generos (múltiplos)
    for genero_uri_full in jogo.get("generos", []):
        genero_id = uri_to_local(genero_uri_full)
        if genero_id:
            genero_uri = EX[genero_id]
            if genero_id not in generos_adicionados:
                g.add((genero_uri, RDF.type, EX.Genero))
                generos_adicionados.add(genero_id)
            g.add((jogo_uri, EX.pertenceAoGenero, genero_uri))
            g.add((genero_uri, EX.temJogo, jogo_uri))  # relação inversa

    # Plataformas (múltiplas)
    for plataforma_uri_full in jogo.get("plataformas", []):
        plataforma_id = uri_to_local(plataforma_uri_full)
        if plataforma_id:
            plataforma_uri = EX[plataforma_id]
            if plataforma_id not in plataformas_adicionadas:
                g.add((plataforma_uri, RDF.type, EX.Plataforma))
                plataformas_adicionadas.add(plataforma_id)
            g.add((jogo_uri, EX.disponivelEm, plataforma_uri))
            g.add((plataforma_uri, EX.suporta, jogo_uri))  # relação inversa

    # Desenvolvedores (múltiplos)
    for dev_uri_full in jogo.get("desenvolvedores", []):
        dev_id = uri_to_local(dev_uri_full)
        if dev_id:
            dev_uri = EX[dev_id]
            if dev_id not in desenvolvedores_adicionados:
                g.add((dev_uri, RDF.type, EX.Desenvolvedora))
                desenvolvedores_adicionados.add(dev_id)
            g.add((jogo_uri, EX.foiDesenvolvidoPor, dev_uri))
            g.add((dev_uri, EX.desenvolveu, jogo_uri))  # relação inversa

    # Publicadores (múltiplos)
    for pub_uri_full in jogo.get("publicadores", []):
        pub_id = uri_to_local(pub_uri_full)
        if pub_id:
            pub_uri = EX[pub_id]
            if pub_id not in publicadores_adicionados:
                g.add((pub_uri, RDF.type, EX.Publicador))
                publicadores_adicionados.add(pub_id)
            g.add((jogo_uri, EX.foiPublicadoPor, pub_uri))
            g.add((pub_uri, EX.publicou, jogo_uri))  # relação inversa


### 3. GUARDAR COMO TTL ###
g.serialize(f"{OUTPUT_FILE}.ttl", format="turtle")
print(f"✅ TTL criado com sucesso: {OUTPUT_FILE}.ttl")
