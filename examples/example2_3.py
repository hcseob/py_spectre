from py_spectre import *
pss = PySpectreScript('example.scs')
# find all capacitors > 100fF
constraint = lambda C: C > 100e-15
print pss.search(p_name='c', p_val=constraint)
