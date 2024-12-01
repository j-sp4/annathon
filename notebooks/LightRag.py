#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete, gpt_4o_complete


# In[ ]:


import textwrap
from openai import OpenAI
import openai
import requests
import os

import json



#Authentication




# In[ ]:


import nest_asyncio
nest_asyncio.apply()


# In[ ]:


WORKING_DIR = "./dickens"


if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)
    


# In[ ]:





# In[ ]:


WORKING_DIR = "./husband_new"


if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=gpt_4o_mini_complete  # Use gpt_4o_mini_complete LLM model
    # llm_model_func=gpt_4o_complete  # Optionally, use a stronger model
)   


print(rag.query("What are the top themes in this story?", param=QueryParam(mode="naive")))


# In[ ]:





# In[ ]:


WORKING_DIR = "./husband"


if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)
    

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=gpt_4o_mini_complete  # Use gpt_4o_mini_complete LLM model
    # llm_model_func=gpt_4o_complete  # Optionally, use a stronger model
)   
    
    
file_name = "truth_about_husband.txt"
with open(f"./{file_name}") as f:
    rag.insert(f.read())


# In[ ]:


print(rag.query("What are the top themes in this story?", param=QueryParam(mode="naive")))



import textract

file_path = 'CancerSig.pdf'
text_content = textract.process(file_path)

rag.insert(text_content.decode('utf-8'))


# In[ ]:


question = "What are the ways to use machine learning to identify which microRNAs cause cancer?"

print(rag.query(question, param=QueryParam(mode="local")))


# In[ ]:


question = "What are some recent scientific papers that explore machine learning for finding MicroRNA cancer signatures? What are the methods used? Provide the link to the methods"

print(rag.query(question, param=QueryParam(mode="hybrid")))


# In[ ]:


import os
import json
from lightrag.utils import xml_to_json
from neo4j import GraphDatabase

BATCH_SIZE_NODES = 500
BATCH_SIZE_EDGES = 100

# Neo4j connection credentials


NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"


os.environ["NEO4J_URI"] = NEO4J_URI
os.environ["NEO4J_USERNAME"] = NEO4J_USERNAME
#os.environ["NEO4J_PASSWORD"] = NEO4J_PASSWORD

def convert_xml_to_json(xml_path, output_path):
    """Converts XML file to JSON and saves the output."""
    if not os.path.exists(xml_path):
        print(f"Error: File not found - {xml_path}")
        return None

    json_data = xml_to_json(xml_path)
    if json_data:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"JSON file created: {output_path}")
        return json_data
    else:
        print("Failed to create JSON data")
        return None

def process_in_batches(tx, query, data, batch_size):
    """Process data in batches and execute the given query."""
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        tx.run(query, {"nodes": batch} if "nodes" in query else {"edges": batch})


# xml_file = os.path.join(WORKING_DIR, 'graph_chunk_entity_relation.graphml')
# json_file = os.path.join(WORKING_DIR, 'graph_data.json')

# # Convert XML to JSON
# json_data = convert_xml_to_json(xml_file, json_file)


# # Load nodes and edges
# nodes = json_data.get('nodes', [])
# edges = json_data.get('edges', [])


# In[ ]:


WORKING_DIR = "./local_husband"


if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=gpt_4o_mini_complete,  # Use gpt_4o_mini_complete LLM model
    graph_storage="Neo4JStorage", #<-----------override KG default
    log_level="DEBUG"  #<-----------override log_level default
)

file_name = "truth_about_husband.txt"
with open(f"./{file_name}") as f:
    rag.insert(f.read())


# In[ ]:


import textract

file_path = 'CancerSig.pdf'
text_content = textract.process(file_path)

rag.insert(text_content.decode('utf-8'))


# In[ ]:


question = "What are some recent scientific papers that explore machine learning for finding MicroRNA cancer signatures? What are the methods used? Provide the link to the methods"

print(rag.query(question, param=QueryParam(mode="hybrid")))


# In[ ]:




