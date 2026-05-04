import sys
import os

try:
    with open("Gemini3/repro_log.txt", "w", encoding="utf-8") as f:
        f.write("Starting script...\n")
except Exception as e:
    print(f"Failed to open log file: {e}")

def log(msg):
    print(msg)
    try:
        with open("Gemini3/repro_log.txt", "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")
    except:
        pass

sys.path.append(os.getcwd())
log(f"CWD: {os.getcwd()}")
log(f"Python: {sys.version}")

try:
    from google.genai import Client, types
    from dotenv import load_dotenv
    log("Imports successful.")
except Exception as e:
    log(f"Import failed: {e}")
    sys.exit(1)

# Load env
load_dotenv()

# API Key Logic
if not os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

# Setup tool
def generate_concept_image(prompt: str, filename: str) -> str:
    """
    Generates an image based on the prompt.
    """
    log(f"DEBUG: Tool called with prompt='{prompt}', filename='{filename}'")
    return "assets/generated/test_image.png"

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        log("GOOGLE_API_KEY not found.")
        return

    log(f"API Key present: {bool(api_key)}")

    try:
        client = Client(api_key=api_key)
        
        # Test message
        input_text = "Create a visual storyboard for a concept about black holes. I want an image of a black hole."
        
        # Define tool config
        # We will pass the function directly to let SDK handle schema generation
        tools = [generate_concept_image]
        
        config = {
            "tools": tools,
            "automatic_function_calling": {'disable': False, 'maximum_remote_calls': 2},
        }
        
        log("Starting chat session with automatic_function_calling...")
        
        chat = client.chats.create(
            model="gemini-3-pro-preview",
            config=config
        )
        
        response = chat.send_message(input_text)
        log("Response received!")
        log(f"Text: {response.text}")
        
    except Exception as e:
        log(f"CRASHED: {e}")
        import traceback
        with open("Gemini3/repro_log.txt", "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)

if __name__ == "__main__":
    main()
