import os
import subprocess
import time
import multiprocessing
from multiprocessing import Pool
import glob
import sys

from rdkit import Chem
from rdkit.Chem import SDMolSupplier
from rdkit.Chem import SDWriter
from rdkit.Chem.rdmolfiles import PDBWriter
from rdkit.Chem import AllChem


def docking(k):
    # mol_id = k.split("/")[-1]
    mol_id = k
    protein = os.path.join(pdbbind_dir, mol_id, f"{mol_id}_protein.pdb")
    protein_pdbqt = os.path.join(pdbbind_dir, mol_id,
                                 f"{mol_id}_protein.pdbqt")
    ligand = os.path.join(pdbbind_dir, mol_id, f"{mol_id}_ligand.sdf")
    ligand_mol2 = os.path.join(pdbbind_dir, mol_id, f"{mol_id}_ligand.mol2")
    log_name = os.path.join(log_dir, f'{mol_id}.log')
    out_name = os.path.join(out_pdbqt_dir, f'{mol_id}_out.pdbqt')
    pdb_name = os.path.join(pdb_dir, f'{mol_id}.pdb')
    pdbqt_name = os.path.join(pdbqt_dir, f'{mol_id}.pdbqt')
    ligand_rcsb = os.path.join(rcsb_dir, mol_id, f"{mol_id}.sdf")

    if os.path.exists(out_name):
        return

    # Generate 3D structure of ligand
    # m = Chem.MolFromSmiles(smiles)
    m = SDMolSupplier(ligand)[0]
    if m is None and os.path.exists(ligand_rcsb):
        m = SDMolSupplier(ligand_rcsb)[0]

    if m is None:
        m = Chem.MolFromMol2File(ligand_mol2)

    if m is None:
        return

    Chem.SanitizeMol(m)

    # Adding hydrogen atoms to molecule
    m = Chem.AddHs(m)
    cids = AllChem.EmbedMultipleConfs(
        m,
        numConfs=20,
    )
    cenergy = []
    for conf in cids:
        converged = not AllChem.UFFOptimizeMolecule(m, confId=conf)
        cenergy.append(
            AllChem.UFFGetMoleculeForceField(m, confId=conf).CalcEnergy())
    min_idx = cenergy.index(min(cenergy))

    m = Chem.RemoveHs(m)
    w = PDBWriter(pdb_name)
    w.write(m, min_idx)
    w.close()

    # pdb to pdbqt (both of ligand and protein)
    if not os.path.exists(pdbqt_name):
        os.system(f'obabel {pdb_name} -O {pdbqt_name}')
    if not os.path.exists(protein_pdbqt):
        os.system(f'obabel {protein} -O {protein_pdbqt}')

    command = f"smina \
            -r {protein_pdbqt} \
            -l {pdbqt_name} \
            --autobox_ligand {ligand} \
            --autobox_add 8 \
            --exhaustiveness 8 \
            --log {log_name} \
            -o {out_name} \
            --cpu 1 \
            --num_modes 100 \
            --seed 0"

    os.system(command)


def run(k):
    try:
        docking(k)
        print(f"{k.split('/')[-1]} done!")
    except:
        print(f"{k.split('/')[-1]} failed!")
        return None


if __name__ == "__main__":
    pdbbind_dir = '../refined_set'
    rcsb_dir = '../rcsb_pdb/refined_data'
    pdbqt_dir = "./pdbqt"
    pdb_dir = "./pdb"
    log_dir = "./result_log"
    out_pdbqt_dir = "./result_pdbqt"
    out_pdb_dir = "./result_pdb"

    for direc in [pdbqt_dir, pdb_dir, log_dir, out_pdbqt_dir, out_pdb_dir]:
        if not os.path.exists(direc):
            os.mkdir(direc)

    with open("./total.txt", "r") as f:
        lines = f.readlines()
        lines = [l.split("_")[0] for l in lines]
        lines = list(set(lines))

    for line in lines:
        run(line)