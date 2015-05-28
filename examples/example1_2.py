from py_spectre import *
pss = PySpectreScript('example.scs')
pss.run()

print pss.results()
print pss.results('dc.dc')
print pss.results('dc.dc', 'VO')
