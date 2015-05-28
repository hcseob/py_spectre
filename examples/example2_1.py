from py_spectre import *
pss = PySpectreScript('example.scs')
pss.search('R*').scale('r', 1.1)
pss.search('C*').scale('c', 1.1)
print pss.search('R*')
print pss.search('C*')


