# :p1 a :Pessoa;
#     nome "Emily Terrel";
#     idade 28;
#     genero "F";
#     email "emily.terrel@gdgoma.org";
#     morada "..." .


# :e1 a :Exame;
#     dataEMD "2020-07-27";
#     resultado true;
#     :éRealizadoPor : p1;


# :c1 a :Clube;
#     nome "GDGoma";
#     :temAtleta : p1;


# :m1 a :Modalidade;
#     nome "Futebol";
#    :éPraticadaEm : c1;
#    :temExame : e1;
#    :éPraticadaPor : p1.

import json

file = open("emd.json", "r")
emds = json.load(file)

output = """
@prefix : <http://rpcw.di.uminho.pt/2025/EMD/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://rpcw.di.uminho.pt/2025/EMD/> .

<http://rpcw.di.uminho.pt/2025/EMD> rdf:type owl:Ontology .

#################################################################
#    Object Properties
#################################################################

###  http://rpcw.di.uminho.pt/2025/EMD#pratica
:pratica rdf:type owl:ObjectProperty ;
         owl:inverseOf :éPraticadaPor ;
         rdfs:domain :Pessoa ;
         rdfs:range :Modalidade .


###  http://rpcw.di.uminho.pt/2025/EMD#realiza
:realiza rdf:type owl:ObjectProperty ;
         owl:inverseOf :éRealizadoPor ;
         rdfs:domain :Pessoa ;
         rdfs:range :Exame .


###  http://rpcw.di.uminho.pt/2025/EMD#relativoA
:relativoA rdf:type owl:ObjectProperty ;
           owl:inverseOf :temExame ;
           rdfs:domain :Exame ;
           rdfs:range :Modalidade .


###  http://rpcw.di.uminho.pt/2025/EMD#temAtleta
:temAtleta rdf:type owl:ObjectProperty ;
           owl:inverseOf :éAtletaDe .


###  http://rpcw.di.uminho.pt/2025/EMD#temExame
:temExame rdf:type owl:ObjectProperty .


###  http://rpcw.di.uminho.pt/2025/EMD#temModalidade
:temModalidade rdf:type owl:ObjectProperty ;
               owl:inverseOf :éPraticadaEm ;
               rdfs:domain :Clube ;
               rdfs:range :Modalidade .


###  http://rpcw.di.uminho.pt/2025/EMD#éAtletaDe
:éAtletaDe rdf:type owl:ObjectProperty ;
           rdfs:domain :Pessoa ;
           rdfs:range :Clube .


###  http://rpcw.di.uminho.pt/2025/EMD#éPraticadaEm
:éPraticadaEm rdf:type owl:ObjectProperty .


###  http://rpcw.di.uminho.pt/2025/EMD#éPraticadaPor
:éPraticadaPor rdf:type owl:ObjectProperty .


###  http://rpcw.di.uminho.pt/2025/EMD#éRealizadoPor
:éRealizadoPor rdf:type owl:ObjectProperty .


#################################################################
#    Data properties
#################################################################

###  http://rpcw.di.uminho.pt/2025/EMD#dataEMD
:dataEMD rdf:type owl:DatatypeProperty .


###  http://rpcw.di.uminho.pt/2025/EMD#email
:email rdf:type owl:DatatypeProperty .


###  http://rpcw.di.uminho.pt/2025/EMD#gênero
:gênero rdf:type owl:DatatypeProperty .


###  http://rpcw.di.uminho.pt/2025/EMD#idade
:idade rdf:type owl:DatatypeProperty .


###  http://rpcw.di.uminho.pt/2025/EMD#morada
:morada rdf:type owl:DatatypeProperty .


###  http://rpcw.di.uminho.pt/2025/EMD#nome
:nome rdf:type owl:DatatypeProperty .


###  http://rpcw.di.uminho.pt/2025/EMD#resultado
:resultado rdf:type owl:DatatypeProperty .


#################################################################
#    Classes
#################################################################

###  http://rpcw.di.uminho.pt/2025/EMD#Clube
:Clube rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2025/EMD#Exame
:Exame rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2025/EMD#Modalidade
:Modalidade rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/2025/EMD#Pessoa
:Pessoa rdf:type owl:Class .


#################################################################
#    Individuals
#################################################################


"""
modalidades = {}
clubes = {}
pessoas = {}

for iterator,exame in enumerate(emds):

    if exame['email'] not in pessoas:
        pessoas[exame['email']] = "P" + str(len(pessoas))
        output += f"""
###  http://rpcw.di.uminho.pt/2025/EMD#{pessoas[exame['email']]}
:{pessoas[exame['email']]} rdf:type owl:NamedIndividual ,
             :Pessoa ;
    :email "{exame['email']}" ;
    :género "{exame['género']}" ;
    :idade {exame['idade']} ;
    :morada "{exame['morada']}" ;
    :nome "{exame['nome']['primeiro']} {exame['nome']['último']}" .
    """
        
    idPessoa = pessoas[exame['email']]

    if exame['clube'] not in clubes:
        clubes[exame['clube']] = "C" + str(len(clubes))
        output += f"""
###  http://rpcw.di.uminho.pt/2025/EMD#{clubes[exame['clube']]}
:{clubes[exame['clube']]} rdf:type owl:NamedIndividual ,
             :Clube ;
    :temAtleta :{idPessoa} ;
    :nome "{exame['clube']}" .
        """
    idClube = clubes[exame['clube']]


    if exame['modalidade'] not in modalidades:
        modalidades[exame['modalidade']] = "M" + str(len(modalidades))
        output += f"""
###  http://rpcw.di.uminho.pt/2025/EMD#{modalidades[exame['modalidade']]}
:{modalidades[exame['modalidade']]} rdf:type owl:NamedIndividual ,
             :Modalidade ;
    :temExame :E{iterator} ;
    :éPraticadaEm :{idClube} ;
    :éPraticadaPor :{idPessoa} ;
    :nome "{exame['modalidade']}" .
        """
    # idModalidade = modalidades[exame['modalidade']]
    else :
        output += f"""
    :M{modalidades[exame['modalidade']]} :temExame :E{iterator} ;
                                         :éPraticadaEm :{idClube} ;
                                         :éPraticadaPor :{idPessoa} .
    """
    
    output += f"""
###  http://rpcw.di.uminho.pt/2025/EMD#E{iterator}
:E{iterator} rdf:type owl:NamedIndividual ,
             :Exame ;
    :éRealizadoPor :P{idPessoa} ;
    :dataEMD "{exame['dataEMD']}" ;
    :resultado "{str(exame['resultado']).lower()}"^^xsd:boolean .

"""
    
print(output)