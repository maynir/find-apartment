import random
import time


def human_delay(min_time=2, max_time=5):
    time.sleep(random.uniform(min_time, max_time))


def random_num(start, end):
    return random.randint(start, end)


def wait_with_countdown(wait_min):
    print(f"Going to sleep now")
    while wait_min > 0:
        print(f"{wait_min} min left...")
        time.sleep(60)
        wait_min -= 1
