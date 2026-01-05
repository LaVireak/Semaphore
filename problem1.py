
from threading import Thread, Semaphore, Lock
import threading
import time
import random

BUFFER_PARTICLES = 100
PAIR_SLOTS = BUFFER_PARTICLES // 2

class ParticleBuffer:
    def __init__(self):
        self.buffer = [None] * BUFFER_PARTICLES
        self.in_idx = 0
        self.out_idx = 0
        self.free_pairs = Semaphore(PAIR_SLOTS)
        self.produced_pairs = Semaphore(0)
        self.lock = Lock()
        self.print_lock = Lock()

    def place_pair(self, producer_id, pair_id, p1, p2):
        self.free_pairs.acquire()
        with self.lock:
            i = self.in_idx
            j = (i + 1) % BUFFER_PARTICLES
            self.buffer[i] = (producer_id, pair_id, p1)
            self.buffer[j] = (producer_id, pair_id, p2)
            self.in_idx = (self.in_idx + 2) % BUFFER_PARTICLES
            with self.print_lock:
                print(f"Producer {producer_id}: placed pair {pair_id} -> slots {i},{j}")
        self.produced_pairs.release()

    def fetch_pair(self, consumer_id):
        self.produced_pairs.acquire()
        with self.lock:
            i = self.out_idx
            j = (i + 1) % BUFFER_PARTICLES
            item1 = self.buffer[i]
            item2 = self.buffer[j]
            assert item1 is not None and item2 is not None, "Consumer read empty slot!"
            assert item1[0] == item2[0] and item1[1] == item2[1], "Mismatched pair fetched!"
            self.buffer[i] = None
            self.buffer[j] = None
            self.out_idx = (self.out_idx + 2) % BUFFER_PARTICLES
            with self.print_lock:
                print(f"Consumer {consumer_id}: fetched pair {item1[1]} from slots {i},{j} (from Producer {item1[0]})")
        self.free_pairs.release()
        return item1, item2


def producer_thread(buffer: ParticleBuffer, producer_id: int, pairs_to_produce: int, delay_range=(0.01, 0.2)):
    for pair_id in range(1, pairs_to_produce + 1):
        time.sleep(random.uniform(*delay_range))
        p1 = f"P{pair_id}_a"
        p2 = f"P{pair_id}_b"
        buffer.place_pair(producer_id, pair_id, p1, p2)
    print(f"Producer {producer_id}: finished producing {pairs_to_produce} pairs")


def consumer_thread(buffer: ParticleBuffer, consumer_id: int, total_pairs_to_consume: int):
    consumed = 0
    while consumed < total_pairs_to_consume:
        time.sleep(random.uniform(0.01, 0.15))
        item1, item2 = buffer.fetch_pair(consumer_id)
        with buffer.print_lock:
            print(f"Consumer {consumer_id}: packaging pair {item1[1]} from Producer {item1[0]}")
        consumed += 1
    print(f"Consumer {consumer_id}: finished consuming {consumed} pairs")


if __name__ == '__main__':
    random.seed(1)
    buffer = ParticleBuffer()

    NUM_PRODUCERS = 3
    PAIRS_PER_PRODUCER = 20
    TOTAL_PAIRS = NUM_PRODUCERS * PAIRS_PER_PRODUCER

    producers = []
    for pid in range(1, NUM_PRODUCERS + 1):
        t = Thread(target=producer_thread, args=(buffer, pid, PAIRS_PER_PRODUCER))
        t.start()
        producers.append(t)

    consumer = Thread(target=consumer_thread, args=(buffer, 1, TOTAL_PAIRS))
    consumer.start()

    for t in producers:
        t.join()
    consumer.join()

    print("Simulation complete.")
