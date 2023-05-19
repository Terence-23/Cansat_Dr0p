import queue


class MovingAvg:
    ARITHMETIC = 0
    WEIGHTED_LIN = 1
    WEIGHTED_EXP = 2
    MULTI_PASS_EXP = 3

    size = 7

    last_val: float = -1e100

    def arithmetic_first(self, size, first=None):
        self.arth_q = queue.Queue(size + 2)
        self.arth_sum = 0
        self.size = size
        if first is not None:
            self.arithmetic_next(first)

    def arithmetic_next(self, next):
        if self.arth_q.qsize() >= self.size:
            self.arth_sum -= self.arth_q.get_nowait()
        self.arth_sum += next
        self.arth_q.put_nowait(next)

        self.last_val = self.arth_sum / self.arth_q.qsize()

        return self.last_val

    def exp_first(self, size, first):
        self.size = size
        den = (1 << size) - 1
        self.weights = [(1 << i) / den for i in range(0, size)]
        self.list = [first for _ in range(size)]

    def lin_first(self, size, first):
        self.size = size
        den = sum(range(size + 1))
        self.weights = [i / den for i in range(1, size + 1)]
        self.list = [first for _ in range(size)]

    def weighted_next(self, next):
        self.list.pop(0)
        self.list.append(next)
        self.last_val = sum((x * y for x, y in zip(self.list, self.weights)))

        return self.last_val

    def multipass_first(self, size, first, pass_num):
        self.size = size
        self.avg_list = []
        for _ in range(pass_num):
            avg = MovingAvg(first, size, MovingAvg.WEIGHTED_EXP)
            first = avg.next(first)
            self.avg_list.append(avg)
        
    
    def multipass_next(self, next):
        for i in self.avg_list:
            next = i.next(next)
        self.last_val = next
        return next
            

    def next(self, next) -> int:
        return -1

    def __init__(self, first, size=7, avg_type=ARITHMETIC, pass_num = None) -> None:
        if size < 2:
            raise ValueError("not long enough moving average")

        elif avg_type == self.ARITHMETIC:
            self.arithmetic_first(size, first)
            self.next = self.arithmetic_next

        elif avg_type == self.WEIGHTED_LIN:
            self.lin_first(size, first)
            self.next = self.weighted_next

        elif avg_type == self.WEIGHTED_EXP:
            self.exp_first(size, first)
            self.next = self.weighted_next
        elif avg_type == self.MULTI_PASS_EXP:
            self.multipass_first(size, first, pass_num)
            self.next = self.multipass_next


def main():
    import matplotlib.pyplot as plt
    import numpy as np
    
    n=10000
    noise = np.random.normal(0,1,n)
    x = np.linspace(0, 10, n)
    data = np.array([i**2 for i in x]) + noise
    
    fig, ax = plt.subplots(figsize=(16, 9))
    
    ax.plot(x, data, label='Noisy')
    arth = MovingAvg(data[0],100,MovingAvg.ARITHMETIC)
    ax.plot(x, [arth.next(i) for i in data], label='Arithmetic')
    #works good but linear reacts a bit faster
    
    lin = MovingAvg(data[0],100,MovingAvg.WEIGHTED_LIN)
    ax.plot(x, [lin.next(i) for i in data], label='Weighted linear')
    #works great 
    
    mp = MovingAvg(data[0], 100, MovingAvg.MULTI_PASS_EXP, 7)
    ax.plot(x, [mp.next(i) for i in data], label='Weighted exponential')
    fig.legend(loc='upper right')
    #doesnot really work
    
    plt.show()


if __name__ == '__main__':
    main()
