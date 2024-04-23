# http://stackoverflow.com/a/2544313/457201
class classproperty(property):
    def __get__(self, obj, type_):
        return self.fget.__get__(None, type_)()
    def __set__(self, obj, value):
        cls = type(obj) 
        return self.fset.__get__(None, cls)(value)

