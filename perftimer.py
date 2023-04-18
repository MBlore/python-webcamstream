import time

# PerfTimer is a class that allows us to use instances in a 'with' block thanks
# to the special '__enter__' and '__exit__' functions.
class PerfTimer:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start_time = time.perf_counter()

    def __exit__(self, type, value, traceback):
        end_time = time.perf_counter()
        elapsed = end_time - self.start_time
        print(f"'{self.name}' taken: {elapsed} seconds.")

# Use the class in a 'with' block over the code you want to time.
with PerfTimer("Big For Loop") as p:
    for i in range(100000000):
        x = 0
        x += 1


