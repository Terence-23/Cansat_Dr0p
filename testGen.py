import os
import random as r

def genDataPoint(max_a = 2, maxtilt = 10):
    wyn = [((r.random() * max_a) - max_a/2)*2, 
            ((r.random() * max_a) - max_a/2)*2, 
            ((r.random() * max_a) - max_a/2)*2,
            
            ((r.random() * maxtilt) - maxtilt/2)*2,
            ((r.random() * maxtilt) - maxtilt/2)*2,
            (r.random() * 360)
            ]
    if wyn[-1] > 180:
        wyn[-1] -= 360
    
    return wyn


if __name__ == "__main__":
    n = 1000
    data = ""
    for _ in range(n):
        text = ""
        for i in genDataPoint():
            text += str(i) + ";"
        data += text[:-1] + "\n"
    
    with open(os.getcwd() +"/data/test.data",'w') as f:
        f.write(data[:-1])
    f.close()