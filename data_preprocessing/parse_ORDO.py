import re
import json
import xml.etree.ElementTree as ET



# Load the XML file
tree = ET.parse('data/ORDO_en_4.3.owl')
root = tree.getroot()

# Define the target class URI
target_class_uri = "http://www.orpha.net/ORDO/Orphanet_"

namespaces = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'efo': 'http://www.ebi.ac.uk/efo/',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    '': 'http://www.w3.org/XML/1998/namespace'  # Default namespace for unprefixed elements
}


rare_disease_ontology = []


# Iterate over all elements in the XML
for element in root.iter():

    # print(element.tag, element.attrib)
    # Check if the element is a Class with the target URI
    if element.tag.endswith('Class') and element.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', '').startswith(target_class_uri):
        # Extract information from the Class element

        # for e in element.iter():
            # print(e)
        about_attribute = element.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', '')

        match = re.search(r'Orphanet_(\d+)', about_attribute)
        if match == None:
            continue
        orphanet_number = match.group(1)
        id = f"ORPHA:{orphanet_number}"
        if element.find('efo:definition', namespaces) != None:
            definition = element.find('efo:definition', namespaces).text
        else:
            definition = ''
        label = element.find('rdfs:label', namespaces).text
        # notation = element.find('skos:notation', namespaces).text
        if label.startswith('OBSOLETE:'):
            continue

        # Print or process the extracted information as needed
        # print(f"Definition: {definition}")
        # print(f"Label: {label}")
        # print(f"Notation: {id}")
        # print("\n")
        rare_disease_ontology.append({
            'id': id,
            'name': label,
            'definition': definition
        })


with open('data/rare_disease_ontology.jsonl', 'w') as f:
    for D in rare_disease_ontology:
        f.write(json.dumps(D) + '\n')