class a(object):
    def __init__(self):
        print self.test(2)
    @staticmethod
    def test(x):
        return x**2

b = a()
