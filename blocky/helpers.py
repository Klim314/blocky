import heapq
from itertools import count
from heapdict import heapdict


class PriorityQueue:
    def __init__(self):
        self.queue = []
        self.counter = count()

    def put(self, item, priority):
        count = next(self.counter)
        heapq.heappush(self.queue, (priority, count, item))

    def pop(self):
        return heapq.heappop(self.queue)
    
    def head(self):
        if not self.queue:
            return None
        return self.queue[0]


if __name__ == "__main__":
    pq = PriorityQueue()

    pq.put("last", 10)
    pq.put("first", 1)
    pq.put("third", 3)
    pq.put("second", 2)
    while pq.head():
        print(pq.pop())

