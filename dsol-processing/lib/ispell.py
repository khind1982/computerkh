import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import popen2

class ispell:
    def __init__(self):
        self._f = popen2.Popen3("ispell -w '-'")
        self._f.fromchild.readline() #skip the credit line
    def __call__(self, words):
        words = words.split(' ')
        output = []
        for word in words:
            self._f.tochild.write(word+'\n')
            self._f.tochild.flush()
            s = self._f.fromchild.readline().strip()
            self._f.fromchild.readline() #skip the blank line
            if s[:8] == "word: ok":
                output.append((word, None))
            elif s[:-1] == "word: not found":
                output.append((word, False))
            else:
                output.append((word, (s[17:-1]).strip().split(', ')))
        return output
