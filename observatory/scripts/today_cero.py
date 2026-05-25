import time
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "grokking_time.txt")

departure_time = time.time() 

with open(file_path, "w") as f:
    f.write(str(departure_time))
    
print(f"Departure time logged at: {departure_time}")