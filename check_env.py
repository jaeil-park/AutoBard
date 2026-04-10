import os
import sys
import subprocess
from dotenv import load_dotenv

def check_python_version():
    print(f"Python Version: {sys.version}")
    if sys.version_info >= (3, 10):
        print("✅ Python 3.10+ detected.")
    else:
        print("❌ Python 3.10+ required.")

def check_env_file():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ .env loaded. API Key found: {api_key[:5]}...{api_key[-4:]}")
    else:
        print("❌ OPENAI_API_KEY not found in .env")

def check_ffmpeg():
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is accessible via system path.")
        else:
            print("❌ FFmpeg command failed.")
    except FileNotFoundError:
        print("❌ FFmpeg not found in system path.")

def check_moviepy():
    try:
        from moviepy import VideoClip
        print("✅ MoviePy is installed and can be imported.")
    except ImportError as e:
        print(f"❌ MoviePy import failed: {e}")

if __name__ == "__main__":
    print("--- AutoBard Environment Check ---")
    check_python_version()
    check_env_file()
    check_ffmpeg()
    check_moviepy()
    print("----------------------------------")
