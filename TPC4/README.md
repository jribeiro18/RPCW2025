# TPC4

### Exportar dados sobre filmes da DBpedia para um ficheiro JSON

Este trabalho de casa consiste em criar um script em Python que exporta dados sobre filmes da DBpedia para um ficheiro JSON.

As seguintes informações são exportadas da DBpedia através de uma query SPARQL:

- id
- título
- país
- data
- realizador
- elenco
- género
- sinopse

Embora não tenha sido possível obter informações de forma consistente sobre a data e género, o script foi implementado para exportar essas informações caso estejam disponíveis.

Adicionalmente, é feita uma lista de atores presentes nos filmes exportados, com as seguintes informações:

- id
- nome
- data de nascimento
- nacionalidade


