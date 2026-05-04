import subprocess
import os

log_file = r"C:\Users\chris\Math-To-Manim\python_log.txt"
input_file = r"C:\Users\chris\Math-To-Manim\media\videos\lorenz_attractor_symphony\480p15\partial_movie_files\LorenzAttractorSymphony\uncached_00012.mp4"
output_file = r"C:\Users\chris\Math-To-Manim\uncached_00012.gif"

with open(log_file, "w") as f:
    f.write(f"Input exists: {os.path.exists(input_file)}\n")
    
    try:
        # ffmpeg might not be in path for python subprocess if env is weird, but let's try
        # Use shell=True to find ffmpeg in path more easily on windows
        result = subprocess.run(["ffmpeg", "-y", "-i", input_file, output_file], capture_output=True, text=True, shell=True)
        f.write(f"Return code: {result.returncode}\n")
        f.write(f"Stdout: {result.stdout}\n")
        f.write(f"Stderr: {result.stderr}\n")
    except Exception as e:
        f.write(f"Error: {e}\n")

    f.write(f"Output exists: {os.path.exists(output_file)}\n")




