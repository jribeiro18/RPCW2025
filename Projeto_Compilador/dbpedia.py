import json
from SPARQLWrapper import SPARQLWrapper, JSON
from time import sleep

def query_dbpedia(endpoint, query):
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

endpoint = "https://dbpedia.org/sparql"

def get_all_games(endpoint, step=1000, max_pages=20):
    all_results = []
    for offset in range(0, step * max_pages, step):
        print(f"Fetching games {offset} to {offset + step}...")
        query = f"""
        SELECT DISTINCT ?jogo ?titulo WHERE {{
          ?jogo rdf:type dbo:VideoGame ;
                foaf:name ?titulo ;
                dbo:releaseDate ?data .
          FILTER (lang(?titulo) = 'en')
        }} LIMIT {step} OFFSET {offset}
        """
        res = query_dbpedia(endpoint, query)
        bindings = res["results"]["bindings"]
        if not bindings:
            break
        all_results.extend(bindings)
    return all_results

# Exemplo de uso:
jogos_resultados = get_all_games(endpoint, step=1000, max_pages=20)

dataset = []

# Passo 2: para cada jogo, buscar detalhes
for i, jogo in enumerate(jogos_resultados):
    uri_jogo = jogo["jogo"]["value"]
    print(f"{i} {uri_jogo}")
    # print(f"Processando: {uri_jogo}")

    query_detalhes = f"""
SELECT ?titulo ?data ?desc
       (GROUP_CONCAT(DISTINCT ?genero; separator="|") AS ?generos)
       (GROUP_CONCAT(DISTINCT ?plataforma; separator="|") AS ?plataformas)
       (GROUP_CONCAT(DISTINCT ?dev; separator="|") AS ?desenvolvedores)
       (GROUP_CONCAT(DISTINCT ?pub; separator="|") AS ?publicadores)
WHERE {{
  <{uri_jogo}> foaf:name ?titulo .
  OPTIONAL {{ <{uri_jogo}> dbo:releaseDate ?data. }}
  OPTIONAL {{ <{uri_jogo}> dbo:abstract ?desc . FILTER (lang(?desc) = 'en') }}
  OPTIONAL {{ <{uri_jogo}> dbo:genre ?genero. }}
  OPTIONAL {{
  {{ <{uri_jogo}> dbo:computingPlatform ?plataforma. }}
  UNION
  {{ <{uri_jogo}> dbp:platforms ?plataforma. }}
}}
  OPTIONAL {{
  {{ <{uri_jogo}> dbo:developer ?dev. }}
  UNION
  {{ <{uri_jogo}> dbp:developer ?dev. }}
}}
  OPTIONAL {{
  {{ <{uri_jogo}> dbo:publisher ?pub. }}
  UNION
  {{ <{uri_jogo}> dbp:publisher ?pub. }}
}}

  FILTER (lang(?titulo) = 'en')
}}
GROUP BY ?titulo ?data ?desc
"""

    detalhes = query_dbpedia(endpoint, query_detalhes)

    if not detalhes["results"]["bindings"]:
        continue

    d = detalhes["results"]["bindings"][0]

    jogo_info = {
        "id": uri_jogo,
        "titulo": d.get("titulo", {}).get("value", ""),
        "data": d.get("data", {}).get("value", ""),
        "descricao": d.get("desc", {}).get("value", ""),
        "generos": d.get("generos", {}).get("value", "").split("|") if "generos" in d else [],
        "plataformas": d.get("plataformas", {}).get("value", "").split("|") if "plataformas" in d else [],
        "desenvolvedores": d.get("desenvolvedores", {}).get("value", "").split("|") if "desenvolvedores" in d else [],
        "publicadores": d.get("publicadores", {}).get("value", "").split("|") if "publicadores" in d else []

    }

    dataset.append(jogo_info)

    #sleep(0.5)  # Evita overload no endpoint da DBpedia

# Guardar no ficheiro
with open("dataset_final.json", "w", encoding="utf-8") as fout:
    json.dump(dataset, fout, ensure_ascii=False, indent=4)

print(f"Dataset criado com {len(dataset)} jogos.")
