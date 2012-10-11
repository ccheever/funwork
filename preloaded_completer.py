import marshal
import os
import json

def relative_path(p):
    return os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), p)


BY_PREFIX = marshal.load(file(relative_path("shareable_medication_prefixes.pm")))

DATA = json.load(file(relative_path("shareable_medication.json")))

BY_ID = {}
for record in DATA:
    BY_ID[record["id"]] = record

def match(q):
    return [BY_ID[x] for x in  BY_PREFIX.get(q, [])]

