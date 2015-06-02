import numpy as np
from py_spectre import *
pss = PySpectreScript('./spectre_scripts/gmid_sweep.scs')
pss.add('save M0:all M1:all')

gmid_path = './spectre_scripts/gmid_sweep_results/'
nmos = {}
pmos = {}
tech_array = ['130nm', '90nm', '65nm', '45nm', '32nm']
L_min_array = [130e-9, 90e-9, 65e-9, 45e-9, 32e-9]
VDS_array = np.arange(0,1.1,0.1)
old_tech = tech_array[0]
first_sim = True
for i, tech in enumerate(tech_array):
    pss.search('include').replace(old_tech, tech)
    L_array = np.arange(L_min_array[i],500e-9, 100e-9)
    for j, L in enumerate(L_array):
        pss.search('parameters').change('LN', L)
        pss.search('parameters').change('LP', L)
        for k, VDS in enumerate(VDS_array):
            pss.search('parameters').change('VDS', VDS)
            pss.write('./spectre_scripts/gmid_sweep.ws.scs')
            pss.run()
            if first_sim:
                first_sim = False
                nmos_results = [v for v in pss.results('dc.dc') if 'M0' in v]
                pmos_results = [v for v in pss.results('dc.dc') if 'M1' in v]
            for m, result in enumerate(nmos_results):
                vgs, data = pss.results('dc.dc', result) 
                if tech not in nmos:
                    nmos[tech] = np.empty((len(nmos_results) + 1, len(L_array), len(VDS_array), len(data))) 
                nmos[tech][m, j, k, :] = data 
            nmos[tech][-1, j, k, :] = [L] * len(data)
            for m, result in enumerate(pmos_results):
                vgs, data = pss.results('dc.dc', result) 
                if tech not in pmos:
                    pmos[tech] = np.empty((len(pmos_results) + 1, len(L_array), len(VDS_array), len(data))) 
                pmos[tech][m, j, k, :] = data
            pmos[tech][-1, j, k, :] = [L] * len(data)
    old_tech = tech
    np.array(list(nmos_results)).tofile(gmid_path + 'nmos' + tech + '_lookup')
    np.array(list(pmos_results)).tofile(gmid_path + 'pmos' + tech + '_lookup')

