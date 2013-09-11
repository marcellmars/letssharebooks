class A_B:
    def __init__(self):
        self.counter = 0
        self.seqs = []

    def a_b(self, a, b):
        print(a)
        print(b)
        print(zip(a,b))
        self.rez = [i for i,j in zip(a,b) if i == j]
        self.seqs.append(self.rez)
        #self.counter = self.counter + len(self.rez)
        print("rez: {}; counter: {}".format(self.rez, self.counter))
        if self.counter >= len(a) or self.counter >= len(b):
            return
        else:
            self.a_b(a[len(self.rez)+1:], b[len(self.rez):])


ab = A_B()
ab.a_b(a,c)
print(ab.seqs)
    
    


