import json
from query import query_dbpedia

'''desportos = []
with open('desportos.json', 'r') as f:
    desportos = json.load(f)

endpoint = 'http://dbpedia.org/sparql'

dataset = []

for d in desportos:
    query_desporto = f"""
select distinct ?name ?designacao where {{
<{d}> rdfs:label ?name ;
     dbo:abstract ?designacao .
FILTER(lang(?designacao)="en") .
FILTER(lang(?name)="en") .
}} LIMIT 100
    """

    result = query_dbpedia(endpoint, query_desporto)

    query_atleta = f"""
    select distinct ?atleta ?name ?birthDate ?birthPlace where {{
?atleta a schema:Person.
?atleta dbp:sport <{d}> .
?atleta dbp:name ?name .
?atleta dbo:birthDate ?birthDate .
?atleta dbo:birthPlace ?birthPlace .
}}
    """

    result2 = query_dbpedia(endpoint, query_atleta)
    atletas = []
    for atleta in result2['results']['bindings']:
        atletas.append(
            {
                "id": atleta['atleta']['value'],
                "nome": atleta['name']['value'],
                "birthPlace": atleta['birthPlace']['value'], 
                "birthDate": atleta['birthDate']['value']
            }
        )
    dataset.append(
        {
        "id" : d,
        "nome" : result['results']['bindings'][0]['name']['value'],
        "designacao": result['results']['bindings'][0]['designacao']['value'],
        "atletas": atletas
    }
    )


with open('dataset.json', 'w') as fout:
    json.dump(dataset, fout, ensure_ascii=False)
    '''


endpoint = 'http://dbpedia.org/sparql'


query_movies = f"""
select distinct ?id ?titulo ?pais ?director ?designacao where {{
?id rdf:type schema:Movie .
?id dbp:name ?titulo
FILTER(lang(?titulo)="en") .
?id dbp:country ?pais.
FILTER(lang(?pais)="en").
?id dbp:director ?director.
?id dbo:abstract ?designacao .
}} ORDER BY RAND() LIMIT 10
"""

movies = query_dbpedia(endpoint, query_movies)

dataset = {
    "movies": {} ,
    "actors": {}
}

for movie in movies['results']['bindings']:
    movie_id = movie['id']['value']
    movie_title = movie['titulo']['value']
    movie_country = movie['pais']['value']
    # movie_date = movie['data']['value']
    movie_director = movie['director']['value']

    # query for list of actors, there is a set to avoid duplicates
    query_actors = f"""
    select distinct ?name ?birthDate ?birthPlace where {{
<{movie_id}> dbo:starring ?actor.
?actor dbp:name ?name.
?actor dbo:birthDate ?birthDate.
?actor dbo:birthPlace ?birthPlace.
    }}
    """
    actors = query_dbpedia(endpoint, query_actors)
    unique_actors = set()
    for actor in actors['results']['bindings']:
        if actor['name']['value'] not in dataset['actors']:
            dataset['actors'][actor['name']['value']] = {
                "birthDate": actor['birthDate']['value'],
                "birthPlace": actor['birthPlace']['value']
            }
        unique_actors.add(actor['name']['value'])

    # query for list of genres
    query_genre = f"""
    select distinct ?genre where {{
<{movie_id}> dbp:genre ?genre.
    }}
    """
    genres = query_dbpedia(endpoint, query_genre)
    unique_genres = set()
    for genre in genres['results']['bindings']:
        unique_genres.add(genre['genre']['value'])  

    movie_designacao = movie['designacao']['value']
    dataset['movies'][movie_id] = {
        "title": movie_title,
        "country": movie_country,
        "director": movie_director,
        "actors": list(unique_actors),
        "genres": list(unique_genres),
        "designacao": movie_designacao
    }

with open('dataset.json', 'w') as fout:
    json.dump(dataset, fout, ensure_ascii=False)
