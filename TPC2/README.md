# TPC 2

Queries em SPARQL para um ficheiro sobre a história de Portugal

### 1 - Quantos triplos existem na topologia?

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT (COUNT(*) AS ?triplos) WHERE { 
    ?s ?p ?o .
}
```

### 2 - Que classes estão definidas?

```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT (COUNT(?classe) AS ?classCount)
WHERE { 
  ?classe a owl:Class .
}
```

### 3 - Que propriedades tem a classe "Rei"?

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT DISTINCT ?propriedade WHERE {
    ?s a :Rei .
    ?s ?propriedade ?o .
}
```

### 4 - Quantos reis aparecem na ontologia?

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT (COUNT(?s) AS ?numReis) WHERE{
    ?s a :Rei .
}
```

### 5 - Calcula uma tabela com o seu nome, data de nascimento e cognome.

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?nome ?nascimento ?cognomes WHERE {
    ?s a :Rei .
    ?s :nome ?nome .
    ?s :nascimento ?nascimento .
    ?s :cognomes ?cognomes .
}
```

### 6 - Acrescenta à tabela anterior a dinastia em que cada rei reinou.

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?nome ?nascimento ?cognomes ?dinastia WHERE {
    ?s a :Rei .
    ?s :nome ?nome .
    ?s :nascimento ?nascimento .
    ?s :cognomes ?cognomes .
    ?s :temReinado ?reinado .
    ?reinado :dinastia ?dinastia .
}
```

### 7 - Qual a distribuição de reis pelas 4 dinastias?

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?dinastia (COUNT(?s) AS ?numReis)
WHERE {
    ?s a :Rei .
    ?s :temReinado ?reinado .
    ?reinado :dinastia ?dinastia .
}
GROUP BY ?dinastia
ORDER BY DESC(?numReis)
```

### 8 - Lista de descobrimentos(sua descrição) por ordem cronológica.

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT DISTINCT ?descricao ?data WHERE{
    ?s a :Descobrimento .
    ?s :data ?data .
    ?s :notas ?descricao .
}ORDER BY (?data)
```

### 9 - Lista as várias conquista, nome e data, com o nome do rei que reinava no momento.

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?nome ?data ?rei WHERE{
    ?s a :Conquista .
    ?s :nome ?nome .
    ?s :data ?data .
    ?s :temReinado ?dinastia .
    ?dinastia :temMonarca ?numRei .
    ?numRei :nome ?rei .
}ORDER BY (?data)
```

### 10 - Calcula uma tabela com o nome, data de nascimento e número de mandatos de todos os presidentes portugueses.

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?nome ?dataNascimento ?mandato WHERE{
    ?s a :Presidente .
    ?s :nome ?nome . 
    ?s :nascimento ?dataNascimento .
    ?s :mandato ?mandato .
}
```

### 11 - Quantos mandatos teve o presidente Sidónio Pais? Em que datas começaram e terminaram esses mandatos?

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?mandato ?inicio ?fim WHERE {
    ?presidente :nome "Sidónio Bernardino Cardoso da Silva Pais" .
    ?presidente :mandato ?mandato .
    ?mandato :comeco ?inicio .
    ?mandato :fim ?fim .
}
```

### 12 - Quais os nomes dos partidos políticos na ontologia?

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?nome WHERE {
    ?s a :Partido .
    ?s :nome ?nome .
}
```

### 13 - Qual a distribuição dos militantes por cada partido político?

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?nomePartido (COUNT(?militante) AS ?numMilitantes) WHERE {
    ?partido a :Partido .
    ?partido :nome ?nomePartido .
    ?partido :temMilitante ?militante .
}GROUP BY (?nomePartido)
```

### 14 - Qual o partido com maior número de presidentes militantes?

```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?nomePartido (COUNT(?militante) AS ?numMilitantes) WHERE {
    ?partido a :Partido .
    ?partido :nome ?nomePartido .
    ?partido :temMilitante ?militante .
}GROUP BY (?nome)
ORDER BY DESC (?numMilitantes)
LIMIT 1 
```

