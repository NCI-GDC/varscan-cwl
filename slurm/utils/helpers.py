import json

def load_json_from_file(fil):
    dic = {}
    with open(fil, 'rt') as fh:
        dic = json.load(fh)
    return dic
