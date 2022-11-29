from time import sleep

from numpy import random


def sleep_for_a_random_time(low=5, high=20):
    sleep_time = random.uniform(low, high)
    sleep(sleep_time)
