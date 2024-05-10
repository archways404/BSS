import pyaudio
from cryptography.fernet import Fernet
import threading
import queue

# Initialize encryption
key = Fernet.generate_key()
cipher = Fernet(key)

# Audio setup
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()

# Queues for audio data
encrypted_queue = queue.Queue()
decrypted_queue = queue.Queue()

# Function to handle audio capture, encrypt, and queue
def capture_and_encrypt():
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    try:
        while True:
            data = stream.read(CHUNK)
            encrypted_data = cipher.encrypt(data)
            encrypted_queue.put(encrypted_data)  # For encrypted playback
            decrypted_queue.put(encrypted_data)  # For decrypted playback
    finally:
        stream.stop_stream()
        stream.close()

# Function to play encrypted audio
def play_encrypted():
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    try:
        while True:
            encrypted_data = encrypted_queue.get()
            stream.write(encrypted_data)  # Play as-is, will sound like noise
    finally:
        stream.stop_stream()
        stream.close()

# Function to decrypt and play back audio
def decrypt_and_play():
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    try:
        while True:
            encrypted_data = decrypted_queue.get()
            decrypted_data = cipher.decrypt(encrypted_data)
            stream.write(decrypted_data)  # Play decrypted, should sound normal
    finally:
        stream.stop_stream()
        stream.close()

# Start threads
t1 = threading.Thread(target=capture_and_encrypt)
t2 = threading.Thread(target=play_encrypted)
#t3 = threading.Thread(target=decrypt_and_play)
t1.start()
t2.start()
#t3.start()

t1.join()
t2.join()
#t3.join()

p.terminate()
