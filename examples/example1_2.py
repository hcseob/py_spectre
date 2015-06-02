from py_spectre import *
pss = PySpectreScript('example.scs')
pss.run()

print pss.results()
print pss.results('dcOp.dc')
print pss.results('dcOp.dc', 'VO')
