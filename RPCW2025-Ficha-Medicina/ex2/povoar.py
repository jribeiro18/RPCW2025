import csv
import json

# Define the output TTL structure
output = """@prefix : <http://example.org/disease/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.org/disease> rdf:type owl:Ontology .

"""

diseases = {}
symptoms_dict = {}
treatments_dict = {}  # Maps treatment names to their IDs
disease_treatments = {}  # Maps disease names to their treatment IDs
descriptions = {}
patients = {}
treatment_counter = 0

# Read disease descriptions
description_file = "Disease_Description.csv"
with open(description_file, newline='', encoding='utf-8') as desc_file:
    desc_reader = csv.DictReader(desc_file)
    for row in desc_reader:
        descriptions[row["Disease"]] = row["Description"].replace('"', '\\"')

# Read disease treatments (precautions)
precaution_file = "Disease_Treatment.csv"
with open(precaution_file, newline='', encoding='utf-8') as treat_file:
    treat_reader = csv.DictReader(treat_file)
    for row in treat_reader:
        disease_name = row["Disease"]
        precautions = [precaution for key, precaution in row.items() 
                      if key.startswith("Precaution_") and precaution]
        
        # Store treatments for this disease
        disease_treatments[disease_name] = []
        for p in precautions:
            if p not in treatments_dict:
                treatments_dict[p] = treatment_counter
                treatment_counter += 1
            disease_treatments[disease_name].append(treatments_dict[p])

# Read disease symptoms
disease_file = "Disease_Syntoms.csv"
with open(disease_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        disease_name = row["Disease"]
        symptoms = [symptom for key, symptom in row.items() 
                   if key.startswith("Symptom_") and symptom]
        description = descriptions.get(disease_name, "No description available.")
        
        if disease_name not in diseases:
            diseases[disease_name] = f"D{len(diseases)}"
            
            # Build symptoms part
            symptoms_part = ""
            if symptoms:
                symptoms_part = "".join(
                    f"    :hasSymptom :S{symptoms_dict.setdefault(s, len(symptoms_dict))} ;\n"
                    for s in symptoms
                )
            
            # Build treatments part - NOW USING disease_treatments
            treatments_part = ""
            if disease_name in disease_treatments:
                treatments_part = "".join(
                    f"    :hasTreatment :T{treatment_id} ;\n"
                    for treatment_id in disease_treatments[disease_name]
                )
            
            output += f"""
### http://example.org/disease#{diseases[disease_name]}
:{diseases[disease_name]} rdf:type owl:NamedIndividual , :Disease ;
    :name "{disease_name}" ;
    :description "{description}" ;
{symptoms_part}{treatments_part}    .
"""

# Read patient data
patients_file = "doentes.json"
with open(patients_file, encoding='utf-8') as jsonfile:
    patients_data = json.load(jsonfile)
    for patient in patients_data:
        patient_id = f"P{len(patients)}"
        patients[patient["nome"]] = patient_id
        patient_symptoms = patient.get("sintomas", [])  # Assuming field is "sintomas" in Portuguese
        
        symptoms_part = ""
        if patient_symptoms:
            symptoms_part = "".join(
                f"    :hasSymptom :S{symptoms_dict.setdefault(s, len(symptoms_dict))} ;\n"
                for s in patient_symptoms if s
            )
        
        output += f"""
### http://example.org/disease#{patient_id}
:{patient_id} rdf:type owl:NamedIndividual , :Patient ;
    :name "{patient['nome']}" ;
{symptoms_part}    .
"""

# Write symptoms instances
for symptom, index in symptoms_dict.items():
    output += f"""
### http://example.org/disease#S{index}
:S{index} rdf:type owl:NamedIndividual , :Symptom ;
    :name "{symptom}" .
"""

# Write treatments instances
for treatment, index in treatments_dict.items():
    output += f"""
### http://example.org/disease#T{index}
:T{index} rdf:type owl:NamedIndividual , :Treatment ;
    :name "{treatment}" .
"""

# Save the output to a file
with open("med_doentes.ttl", "w", encoding='utf-8') as ttl_file:
    ttl_file.write(output)

print("TTL file generated successfully.")