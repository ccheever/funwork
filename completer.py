import json
import re
import marshal

DATA = json.load(file("shareable_medication.json"))

BY_ID = {}
for row in DATA:
    BY_ID[row["id"]] = row

def match(s):
    s_ = s.lower()
    matches = []
    for row in DATA:
        for (field, val) in row.iteritems():
            if type(val) is unicode:
                if val.lower().startswith(s_):
                    matches.append(row)
                    break
    return matches

BY_PREFIX = {}

for record in DATA:
    for (field, val) in record.iteritems():
        if field == "id":
            continue
        if val is not None:
            tokens = re.split("[^0-9a-z]", val.lower())
            for s in tokens:
                if not s:
                    continue
                for i in xrange(len(s)):
                    prefix = s[:i + 1]
                    if not BY_PREFIX.has_key(prefix):
                        BY_PREFIX[prefix] = set()
                    BY_PREFIX[prefix].add(record["id"])

def match2(s):
    ids = BY_PREFIX.get(s.lower(), set())
    x = []
    for i in ids:
        x.append(BY_ID[i])
    return x

def write_by_prefix():
    marshal.dump(BY_PREFIX, open("shareable_medication_prefixes.pm", "w"))

