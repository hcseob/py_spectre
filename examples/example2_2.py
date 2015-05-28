from py_spectre import *
pss = PySpectreScript('example.scs')
pss.remove('R1')
print pss.search('R*')
line_num = 5
ns = 'R1 VO 0 resistor r=3k' 
pss.add(ns, line_num)
print pss.search('R*')
