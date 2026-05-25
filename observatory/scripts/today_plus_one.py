import time
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "grokking_time.txt")

# Aquí usamos "r" porque solo vamos a LEER
with open(file_path, "r") as f:
    start_time = float(f.read())

elapsed = time.time() - start_time
print(f"You have been away for {elapsed / 86400:.2f} days.")