import os
from password import password
from tqdm import tqdm
import time


min_length = 8
max_length = 11
algo = password()


__debug__ and print("\nTesting...")


with tqdm(total=range(2, 10).__len__(), desc="Processing") as pbar:
    for step in range(2, 10):
        __debug__ and print(f"\nStep")
        time.sleep(0.1)  # Replace with actual work
        pbar.update(1)  # Increment progress bar by 1 step





# Wrap any iterable with tqdm()
# for i in tqdm(range(100), desc="Processing"):
#     time.sleep(0.1)  # Simulating work

# for value in algo.generate_numbers(min_length, max_length, limit=10):
#     print(value)