from statistics import mean
import time

class TimedCounter:
    def __init__(self, name, display_func = None):
        self.name = name
        self.start_time = time.time()
        self.value = 0
        self.display_func = display_func

    def add(self, val):
        self.value += val

        end_time = time.time()

        total_seconds = end_time - self.start_time
        
        if total_seconds >= 1:
            self.start_time = time.time()
            
            if self.display_func is not None:
                self.display_func(self.name, self.value)
            else:
                print(f"{self.name}: {self.value}")

            self.value = 0

class PerfTimer:
    def __init__(self, name):
        self.name = name
        self.items = []
        self.print_timer = time.time()

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        end_time = time.time()
        elapsed = end_time - self.start_time

        self.items.append(elapsed)

        if end_time - self.print_timer > 1:
            print(f"'{self.name}' taken:", mean(self.items), "seconds.")
            self.print_timer = time.time()
            self.items.clear()