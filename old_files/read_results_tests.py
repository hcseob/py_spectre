from read_results import *

print read_results('./psf/test3/')
for result in read_results('./psf/test3'):
    print result
    print read_results('./psf/test3/' + result)

print read_results('./psf/test4/dcOp.dc', 'VO2')
print read_results('./psf/test4/dcOp.dc')
print read_results('./psf/test4/dcOp.dc', all_results=True)
print read_results('./psf/test4/dcOp.dc', 'VO2', all_results=True)
print read_results('./psf/test4/dcOp.dc', 'VO2', True)
print read_results('./psf/test4/dcOp.dc', 'VO2', all_results=False)
print read_results('./psf/test4/dcOp.dc', 'VO2', False)

print read_results('./psf/test5/dc.dc', 'M0:cgg')

