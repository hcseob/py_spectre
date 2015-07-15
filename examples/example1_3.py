from py_spectre import *
pss = PySpectreScript('example.scs')
print pss.search('parameters')
pss.search('parameters').change('VSWEEP', 2)
print pss.search('parameters')
pss.run()
