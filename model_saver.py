"""
2017/06/27 Gregory Grant
"""

import numpy as np
import json
import copy
import base64

global multi_types
global singlet_types
global other_types

# JSON will only handle dictionaries, lists, strings, numbers, booleans, and None/null.
multi_types = [type({}), type([])]
singlet_types = [type(""), type(1), type(True), type(None)]
# Other types that we have written conversions for go here.
other_types = [type(np.array([0])), type(np.float32(0.)), type(np.float64(0.)), type(range(0,1))]

def json_save(x, savedir="save.json", toplevel=True):
    x = copy.deepcopy(x)

    def item(x, i):
        s = type(x[i])
        if s in multi_types:
            x[i] = json_save(x[i], toplevel=False)
        elif s in singlet_types:
            pass
        elif s in other_types:
            if s == type(np.array([0])):
                if not x[i].flags['C_CONTIGUOUS']:
                    x[i] = np.ascontiguousarray(x[i])
                x[i] = ["ndarray", str(base64.b64encode(x[i])), str(x[i].shape), str(x[i].dtype)]
            elif (s == type(np.float32(0.)) or s == type(np.float64(0.))):
                x[i] = np.asscalar(x[i])
            elif (s == type(range(0,1))):
                x[i] = ["range", x[i].start, x[i].stop, x[i].step]
        return x[i]

    if type(x) == multi_types[0]:
        for i in x:
            x[i] = item(x, i)
    elif type(x) == multi_types[1]:
        for i in range(len(x)):
            x[i] = item(x, i)

    if toplevel == True:
        with open(savedir, 'w') as f:
            json.dump(x, f)
    else:
        return x


def json_load(savedir="save.json", toplevel=True, a=None):

    if toplevel == True:
        with open(savedir, 'r') as f:
            x = json.load(f)
            print("Loading JSON file...")
    else:
        x = copy.deepcopy(a)

    for i in x:
        s = type(x[i])
        if s == multi_types[0]:
            x[i] = json_load(toplevel=False, a=x[i])
        if s == multi_types[1]:
            if x[i][0] == "ndarray":
                x[i] = np.reshape(np.fromstring(base64.b64decode(x[i][1][1:]), dtype=x[i][3]), x[i][2])
            elif x[i][0] == "range":
                x[i] = range(*x[i][1:3])
            else:
                x[i] = json_load(toplevel=False, a=x[i])
        if s in singlet_types:
            pass

    return x