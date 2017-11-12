import queue
import threading


def worker(queue, func):
    while True:
        items = queue.get()
        if items is None:
            break
        func(items)
        queue.task_done()


class Uploader(object):

    def __init__(self, func, num_of_threads=2):
        self.num_of_threads = num_of_threads
        self.func = func
        self.queue = queue.Queue()
        self.threads = None

    def start(self):
        if self.threads:
            return

        self.threads = [
            threading.Thread(target=worker, args=(self.queue, self.func))
            for i in range(self.num_of_threads)
        ]
        for thread in self.threads:
            thread.start()

    def wait(self):
        self.queue.join()

    def finish(self):
        for i in range(self.num_of_threads):
            self.queue.put(None)
        while self.threads:
            self.threads.pop().join()
