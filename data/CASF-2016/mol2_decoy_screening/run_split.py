import glob
import os
import sys
import multiprocessing
from multiprocessing import Pool
import time


def python_run(fn):
    key = fn.split("/")[-1].split("_")[0]
    with open(fn, "r") as f:
        lines = f.readlines()
    dic = dict()
    for line in lines:
        if "#\tName" in line:
            ligand, _, idx = line.split()[-1].split("_")
            curr = "_".join([key, ligand, idx]) + ".mol2"
            dic[curr] = [line]
        else:
            dic[curr].append(line)
    for k, v in dic.items():
        with open(k, "w") as w:
            for l in v:
                w.write(l)
    return

total = glob.glob("../decoys_screening/*/*.mol2")
total = sorted(total,
               key=lambda x: (x.split("/")[-1].split(".")[0].split("_")[0],
                              x.split("/")[-1].split(".")[0].split("_")[1]))

start, end = int(sys.argv[1]), int(sys.argv[2])
end = None if end == -1 else end
pool = Pool(4)
r = pool.map_async(python_run, total[start:end])
r.wait()
pool.close()
pool.join()
