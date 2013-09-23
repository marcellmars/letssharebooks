class A_B:
    def __init__(self):
        self.counter = 0
        self.seqs = []

    def a_b(self, a, b):
        if len(a) <= 0 or len(b) <=0:
            return
        self.rez = [i for i,j in zip(a,b) if i == j]
        self.seqs.append(self.rez)
        self.a_b(a[len(self.rez)+1:], b[len(self.rez):])


ab = A_B()
ab.a_b(a,b)
print(ab.seqs)


