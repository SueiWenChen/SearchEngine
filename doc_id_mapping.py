import os
import json

i=1
doc_name_to_id = dict()
doc_id_to_name = dict()
for f in os.listdir('./documents'):
    name = f[:-4] # remove extension
    doc_name_to_id[name] = str(i)
    doc_id_to_name[str(i)] = name
    i+=1
with open('doc_name_to_id.json', 'w') as f:
    f.write(json.dumps(doc_name_to_id))
with open('doc_id_to_name.json', 'w') as f:
    f.write(json.dumps(doc_id_to_name))