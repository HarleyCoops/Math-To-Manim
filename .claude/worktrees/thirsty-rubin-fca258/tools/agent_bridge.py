#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Jules Bridge: Simplified entry point for Gemini3 Pipeline")
    parser.add_argument("--prompt", type=str, required=True, help="Path to the prompt text file or the prompt text itself")
    parser.add_argument("--output", type=str, default="Gemini3/output_scene.py", help="Destination file for the generated code")

    args = parser.parse_args()

    # Determine the root directory of the repo
    # Assuming this script is in tools/ and the repo root is one level up
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)

    pipeline_script = os.path.join(repo_root, "Gemini3", "run_pipeline.py")

    if not os.path.exists(pipeline_script):
        print(f"Error: Could not find pipeline script at {pipeline_script}")
        sys.exit(1)

    cmd = [sys.executable, pipeline_script, "--prompt", args.prompt, "--output", args.output]

    print(f"Bridge executing: {' '.join(cmd)}")

    try:
        # Check environment variables
        env = os.environ.copy()

        # Run the pipeline script
        result = subprocess.run(cmd, env=env, check=True)

        if result.returncode == 0:
            print(f"Pipeline finished successfully. Output should be at {args.output}")
        else:
            print("Pipeline finished with errors.")

    except subprocess.CalledProcessError as e:
        print(f"Error running pipeline: {e}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
