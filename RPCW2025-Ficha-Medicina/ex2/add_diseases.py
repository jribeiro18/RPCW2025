from rdflib import Graph, Namespace, Literal, RDF, OWL

g = Graph().parse("med_doentes.ttl", format="turtle")

q = """
CONSTRUCT {
  ?doente :hasDisease ?doenca .
  }
WHERE { 
    ?doente a :Patient .
    ?doenca a :Disease .
    ?doente :hasSymptom ?sintoma1 .
    ?doente :hasSymptom ?sintoma2 .
    ?doente :hasSymptom ?sintoma3 .
    ?doenca :hasSymptom ?sintoma1 .
    ?doenca :hasSymptom ?sintoma2 .
    ?doenca :hasSymptom ?sintoma3 .
    FILTER(?sintoma1 != ?sintoma2)
    FILTER(?sintoma1 != ?sintoma3)
    FILTER(?sintoma2 != ?sintoma3)
    }
  
"""

n = Namespace("http://example.org/disease/")
g.add((n.hasDisease, RDF.type, OWL.ObjectProperty))

for r in g.query(q):
    g.add(r)
print(g.serialize())