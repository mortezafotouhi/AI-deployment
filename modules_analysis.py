import json
from modules import ModuleTrack
import numpy as np
import matplotlib.pyplot as plt

with open('data/modules_description.jsonl', 'r') as file:
    MODULES_DESCRIPTION = [json.loads(line) for line in file]

with open('data/pp_demo.json', 'r') as file:
    data_demo = json.load(file)

with open('data/gcp_uk_demo_asthma.json', 'r') as file:
    data_gcp = json.load(file)

DATA = data_demo + data_gcp

Module = ModuleTrack()
List = []
for dep in DATA:
    vec = Module.create_module_array(dep["modules"])
    List.append(vec)

List = np.array(List)
modules_count = np.sum(List, axis=0)

sorted_list = sorted(zip(modules_count, [item["moduleId"] for item in MODULES_DESCRIPTION]), reverse=True)
plt.figure(figsize=(12, 6))
plt.xticks(rotation=45)
plt.bar([item[1] for item in sorted_list], [item[0] for item in sorted_list])
plt.show()
