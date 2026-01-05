from threading import Thread, Semaphore

# semaphores initial values: a=1, b=0, c=0
a = Semaphore(1)
b = Semaphore(0)
c = Semaphore(0)

def process1():
    a.acquire()
    print('H', end='', flush=True)
    print('E', end='', flush=True)
    b.release()

def process2():
    b.acquire()
    print('L', end='', flush=True)
    print('L', end='', flush=True)
    c.release()

def process3():
    c.acquire()
    print('O', flush=True)

if __name__ == '__main__':
    t1 = Thread(target=process1)
    t2 = Thread(target=process2)
    t3 = Thread(target=process3)

    # start all processes
    t1.start()
    t2.start()
    t3.start()

    # wait for them to finish
    t1.join()
    t2.join()
    t3.join()

    print('Simulation complete.')
