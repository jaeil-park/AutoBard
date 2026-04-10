from moviepy import AudioFileClip
import os

def check_durations():
    temp_files = [f for f in os.listdir("temp") if f.endswith(".mp3") and not f.endswith("_raw.mp3")]
    print("--- Audio Duration Check ---")
    for f in temp_files:
        path = os.path.join("temp", f)
        audio = AudioFileClip(path)
        print(f"File: {f} | Duration: {audio.duration:.2f}s")
        audio.close()

if __name__ == "__main__":
    check_durations()
