import os
import random as r

def genDataPoint(max_a = 2, maxtilt = 10, maxTemp = 290, minTemp = 270, minPress = 50_000, maxPress = 110000):
    # temp  in Kelwins, press in pascals
    wyn = [((r.random() * max_a) - max_a/2)*2, 
            ((r.random() * max_a) - max_a/2)*2, 
            ((r.random() * max_a) - max_a/2)*2,
            
            ((r.random() * maxtilt) - maxtilt/2)*2,
            ((r.random() * maxtilt) - maxtilt/2)*2,
            (r.random() * 360),
            # temp
            (r.random() * (maxTemp - minTemp) + minTemp),
            # Pressure
            (r.random()*(maxPress - minPress) + minPress)
            ]
    if wyn[5] > 180:
        wyn[5] -= 360
    
    return wyn


if __name__ == "__main__":
    n = 10
    data = ""
    for _ in range(n):
        text = ""
        for i in genDataPoint():
            text += str(i) + ";"
        data += text[:-1] + "\n"
    
    with open(os.getcwd() +"/data/test.data",'w') as f:
        f.write(data[:-1])
    f.close()