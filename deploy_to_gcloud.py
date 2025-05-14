#!/usr/bin/env python
"""
Deploy Math-To-Manim to Google Cloud Run

This script automates the deployment of the Math-To-Manim application to Google Cloud Run.
It handles:
1. Building and pushing the Docker image to Google Container Registry
2. Deploying the image to Google Cloud Run
3. Setting up a Google Cloud Storage bucket for storing generated animations

Requirements:
- Google Cloud SDK installed and configured
- Docker installed
- .env file with Google Cloud configuration
"""

import os
import subprocess
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Google Cloud configuration from environment variables
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
REGION = os.getenv("GOOGLE_REGION", "us-central1")
SERVICE_NAME = os.getenv("GOOGLE_CLOUD_RUN_SERVICE", "math-to-manim")
STORAGE_BUCKET = os.getenv("GOOGLE_STORAGE_BUCKET")

def check_requirements():
    """Check if all required tools and configurations are available."""
    if not PROJECT_ID:
        raise ValueError("GOOGLE_PROJECT_ID environment variable is not set. Please check your .env file.")
    
    # Check if gcloud is installed
    try:
        subprocess.run(["gcloud", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError("Google Cloud SDK (gcloud) is not installed or not in PATH.")
    
    # Check if docker is installed
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError("Docker is not installed or not in PATH.")
    
    # Check if user is logged in to gcloud
    try:
        subprocess.run(["gcloud", "auth", "print-identity-token"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        raise RuntimeError("Not logged in to Google Cloud. Run 'gcloud auth login' first.")

def create_dockerfile():
    """Create a Dockerfile for the application if it doesn't exist."""
    if os.path.exists("Dockerfile"):
        print("Dockerfile already exists, skipping creation.")
        return
    
    dockerfile_content = """FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    texlive-full \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for the web interface
EXPOSE 8080

# Start the application
CMD ["python", "app.py"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    print("Created Dockerfile.")

def setup_storage_bucket():
    """Create a Google Cloud Storage bucket if it doesn't exist."""
    if not STORAGE_BUCKET:
        print("GOOGLE_STORAGE_BUCKET not set, skipping storage bucket setup.")
        return
    
    # Check if bucket exists
    result = subprocess.run(
        ["gsutil", "ls", "-b", f"gs://{STORAGE_BUCKET}"],
        capture_output=True
    )
    
    if result.returncode != 0:
        print(f"Creating storage bucket: gs://{STORAGE_BUCKET}")
        subprocess.run(
            ["gsutil", "mb", "-l", REGION, f"gs://{STORAGE_BUCKET}"],
            check=True
        )
        
        # Set public access if requested
        subprocess.run(
            ["gsutil", "iam", "ch", "allUsers:objectViewer", f"gs://{STORAGE_BUCKET}"],
            check=True
        )
    else:
        print(f"Storage bucket gs://{STORAGE_BUCKET} already exists.")

def build_and_push_image():
    """Build and push the Docker image to Google Container Registry."""
    image_name = f"gcr.io/{PROJECT_ID}/{SERVICE_NAME}"
    
    print(f"Building Docker image: {image_name}")
    subprocess.run(
        ["docker", "build", "-t", image_name, "."],
        check=True
    )
    
    print(f"Pushing Docker image to Google Container Registry")
    subprocess.run(
        ["docker", "push", image_name],
        check=True
    )
    
    return image_name

def deploy_to_cloud_run(image_name):
    """Deploy the application to Google Cloud Run."""
    print(f"Deploying to Google Cloud Run: {SERVICE_NAME}")
    
    # Prepare environment variables for Cloud Run
    env_vars = []
    if os.getenv("DEEPSEEK_API_KEY"):
        env_vars.append(f"DEEPSEEK_API_KEY={os.getenv('DEEPSEEK_API_KEY')}")
    if os.getenv("GOOGLE_API_KEY"):
        env_vars.append(f"GOOGLE_API_KEY={os.getenv('GOOGLE_API_KEY')}")
    if STORAGE_BUCKET:
        env_vars.append(f"GOOGLE_STORAGE_BUCKET={STORAGE_BUCKET}")
    
    env_flags = []
    for var in env_vars:
        env_flags.extend(["--set-env-vars", var])
    
    # Deploy to Cloud Run
    deploy_cmd = [
        "gcloud", "run", "deploy", SERVICE_NAME,
        "--image", image_name,
        "--platform", "managed",
        "--region", REGION,
        "--allow-unauthenticated"  # Public access
    ]
    
    if env_flags:
        deploy_cmd.extend(env_flags)
    
    subprocess.run(deploy_cmd, check=True)
    
    # Get the deployed URL
    url_cmd = [
        "gcloud", "run", "services", "describe", SERVICE_NAME,
        "--platform", "managed",
        "--region", REGION,
        "--format", "value(status.url)"
    ]
    
    result = subprocess.run(url_cmd, check=True, capture_output=True, text=True)
    url = result.stdout.strip()
    
    print(f"\nDeployment successful!")
    print(f"Your Math-To-Manim application is now available at: {url}")

def main():
    parser = argparse.ArgumentParser(description="Deploy Math-To-Manim to Google Cloud Run")
    parser.add_argument("--skip-storage", action="store_true", help="Skip setting up a storage bucket")
    args = parser.parse_args()
    
    try:
        check_requirements()
        create_dockerfile()
        
        if not args.skip_storage:
            setup_storage_bucket()
        
        image_name = build_and_push_image()
        deploy_to_cloud_run(image_name)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

