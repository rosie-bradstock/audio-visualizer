import pyaudio
import math
import pygame
import struct
import random

# Initialize PyAudio
p = pyaudio.PyAudio()

# Audio stream parameters
FORMAT = pyaudio.paInt16    # Defines the bit depth of audio samples (e.g., 16-bit PCM).
CHANNELS = 1                # Defines the number of audio channels (e.g., mono or stereo).
RATE = 44100                # Defines how many samples are captured or played per second (sample rate).
CHUNK = 1024                # Defines the number of samples processed in each buffer (chunk size).

# Open the audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

def get_rms(data):
    
    # Convert the raw data to a list of 16-bit integers
    audio_data = list(struct.unpack('<' + 'h' * (len(data) // 2), data))
    
    # Calculate the RMS (Root Mean Square) value to gauge volume
    sum_squares = sum((sample**2 for sample in audio_data))
    rms = math.sqrt(sum_squares / len(audio_data))
    return rms


# Initialize Pygame
pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visualiser")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()

# Colors
background_color = (0, 0, 0)

running = True

while running:
    clock.tick(50)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read audio data from the stream (specified number of samples) and calculate the rms
    rms = get_rms(stream.read(CHUNK))

    # Clear the screen
    screen.fill(background_color)
    
    # Update the sprites
    all_sprites.update()
    all_sprites.draw(screen)

    # Update the display
    pygame.display.flip()

# Clean up
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()