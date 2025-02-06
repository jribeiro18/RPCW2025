import json

# Load JSON file
with open('emd.json', 'r', encoding='utf-8') as f:
    bd = json.load(f)

Objetos = set()
ttl = ""

for emd in bd:
    # Collect unique values
    Objetos.add(emd['género'])
    Objetos.add(emd['modalidade'])
    Objetos.add(emd['clube'])
    Objetos.add(emd['morada'])
    
    # Create RDF representation
    registo = f"""
###  http://rpcw.di.uminho.pt/2024/EMD#{emd['_id']}
<http://rpcw.di.uminho.pt/2024/EMD#{emd['_id']}> rdf:type owl:NamedIndividual ,
                                                    <http://rpcw.di.uminho.pt/2024/TPC1/Atleta> ;
                                            <http://rpcw.di.uminho.pt/2024/TPC1/temNome> "{emd['nome']['primeiro']} {emd['nome']['último']}" ;
                                            <http://rpcw.di.uminho.pt/2024/TPC1/temGénero> <http://rpcw.di.uminho.pt/2024/TPC1/{emd['género']}> ;
                                            <http://rpcw.di.uminho.pt/2024/TPC1/temModalidade> <http://rpcw.di.uminho.pt/2024/TPC1/{emd['modalidade'].replace(" ", "_")}> ;
                                            <http://rpcw.di.uminho.pt/2024/TPC1/temClube> <http://rpcw.di.uminho.pt/2024/TPC1/{emd['clube'].replace(" ", "_")}> ;
                                            <http://rpcw.di.uminho.pt/2024/TPC1/temMorada> "{emd['morada']}" ;
                                            <http://rpcw.di.uminho.pt/2024/TPC1/temIdade> "{emd['idade']}"^^xsd:int ;
                                            <http://rpcw.di.uminho.pt/2024/TPC1/temDataEMD> "{emd['dataEMD']}"^^xsd:dateTime ;
                                            <http://rpcw.di.uminho.pt/2024/TPC1/éFederado> "{str(emd['federado']).lower()}"^^xsd:boolean ;
                                            <http://rpcw.di.uminho.pt/2024/TPC1/temResultado> "{str(emd['resultado']).lower()}"^^xsd:boolean .
    """
    ttl += registo

# Create RDF individuals for unique values
for element in Objetos:
    obj = f"""
###  http://rpcw.di.uminho.pt/2024/EMD#{element.replace(" ", "_")}
:{element.replace(" ", "_")} rdf:type owl:NamedIndividual .
"""
    ttl += obj

# Write to a TTL file
with open('emd.ttl', 'w', encoding='utf-8') as ttl_file:
    ttl_file.write(ttl)

print("TTL file successfully created: emd.ttl")