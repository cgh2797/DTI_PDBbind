import pickle
from collections import Counter
import random
from rdkit.Chem.Scaffolds.MurckoScaffold import MurckoScaffoldSmilesFromSmiles
from rdkit import Chem
import numpy as np
import glob
import gc
import time
import sys
random.seed(0)

keys = glob.glob('../../data_pdbbind/data/*')[:]
keys = [k.split('/')[-1] for k in keys]
#print (keys)
with open('../../data_pdbbind/train_pdbs.txt') as f:
    lines = f.readlines()
    lines = [l.strip() for l in lines]
    train_keys = sorted(list( set(keys) & set(lines)))

with open('../../data_pdbbind/test_pdbs.txt') as f:
    lines = f.readlines()
    lines = [l.strip() for l in lines]
    test_keys = sorted(list( set(keys) & set(lines)))

print (f'Number of train data: {len(train_keys)}')
print (f'Number of test data: {len(test_keys)}')
with open('train_keys.pkl', 'wb') as fp:
    pickle.dump(train_keys, fp)
with open('test_keys.pkl', 'wb') as fp:
    pickle.dump(test_keys, fp)