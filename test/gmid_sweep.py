import numpy as np
import os
import sys
sys.path.append('/home/rboesch/Python/py_spectre')

from py_spectre.py_spectre import *
from py_spectre.post.read_results import read_results

pss = PySpectreScript()
pss.read_script('./spectre_scripts/gmid_sweep.scs')

pss.add_ns('save M0:all M1:all')

gmid_path = './spectre_scripts/gmid_sweep_results/'
nmos = {}
pmos = {}
tech_array = ['130nm', '90nm', '65nm', '45nm', '32nm']
L_min_array = [130e-9, 90e-9, 65e-9, 45e-9, 32e-9]
VDS_array = np.arange(0,1.01,0.01)
old_tech = tech_array[0]
first_sim = True
for i, tech in enumerate(tech_array):
    pss.search('include').replace(old_tech, tech)
    L_array = np.arange(L_min_array[i],500e-9, 10e-9)
    for j, L in enumerate(L_array):
        pss.search('parameters').change('LN', L)
        pss.search('parameters').change('LP', L)
        for k, VDS in enumerate(VDS_array):
            pss.search('parameters').change('VDS', VDS)
            pss.write_script('./spectre_scripts/gmid_sweep.ws.scs')
            pss.run_script()
            psf = read_results(pss.path_to_results, 'dc.dc')
            if first_sim:
                first_sim = False
                nmos_results = [v for v in psf.getValueNames() if 'M0' in v]
                pmos_results = [v for v in psf.getValueNames() if 'M1' in v]
            for m, result in enumerate(nmos_results):
                data = psf.getValuesByName(result) 
                if tech not in nmos:
                    nmos[tech] = np.empty((len(nmos_results) + 1, len(L_array), len(VDS_array), len(data))) 
                nmos[tech][m, j, k, :] = data
            nmos[tech][-1, j, k, :] = [L] * len(data)
            for m, result in enumerate(pmos_results):
                data = psf.getValuesByName(result) 
                if tech not in pmos:
                    pmos[tech] = np.empty((len(pmos_results) + 1, len(L_array), len(VDS_array), len(data))) 
                pmos[tech][m, j, k, :] = data
            pmos[tech][-1, j, k, :] = [L] * len(data)
    old_tech = tech
    # nmos[tech].tofile(gmid_path + 'nmos' + tech)
    np.array(list(nmos_results)).tofile(gmid_path + 'nmos' + tech + '_lookup')
    # pmos[tech].tofile(gmid_path + 'pmos' + tech)
    np.array(list(pmos_results)).tofile(gmid_path + 'pmos' + tech + '_lookup')

