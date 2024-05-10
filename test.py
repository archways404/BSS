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

# Queue to hold encrypted audio
encrypted_queue = queue.Queue()

# Function to handle audio capture and encryption
def capture_and_encrypt():
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    try:
        while True:
            data = stream.read(CHUNK)
            encrypted_data = cipher.encrypt(data)
            encrypted_queue.put(encrypted_data)
    finally:
        stream.stop_stream()
        stream.close()

# Function to decrypt and play back audio
def decrypt_and_play():
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    try:
        while True:
            encrypted_data = encrypted_queue.get()
            data = cipher.decrypt(encrypted_data)
            stream.write(data)
    finally:
        stream.stop_stream()
        stream.close()

# Start threads
t1 = threading.Thread(target=capture_and_encrypt)
t2 = threading.Thread(target=decrypt_and_play)
t1.start()
t2.start()

t1.join()
t2.join()

p.terminate()
