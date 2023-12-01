import networkx as nx
import matplotlib.pyplot as plt
from neo4j import GraphDatabase

from utils import *



triples = load_data('cache_data/step6_res.jsonl')


uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"


driver = GraphDatabase.driver(uri, auth=(username, password))

def add_triple(tx, subj, pred, obj):
    tx.run("MERGE (a:Entity {name: $subj}) "
           "MERGE (b:Entity {name: $obj}) "
           "MERGE (a)-[r:RELATIONSHIP {type: $pred}]->(b)",
           subj=subj, pred=pred, obj=obj)



with driver.session() as session:
    for subj, pred, obj in triples:
        session.write_transaction(add_triple, subj, pred, obj)

driver.close()
