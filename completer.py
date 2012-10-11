import json


DATA = json.load(file("shareable_medication.json"))

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
            s = val.lower()
            for i in xrange(len(s)):
                prefix = s[:i + 1]
                if not BY_PREFIX.has_key(prefix):
                    BY_PREFIX[prefix] = []
                BY_PREFIX[prefix].append(record)
