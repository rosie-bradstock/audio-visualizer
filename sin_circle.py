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

class Sin_circle:

    def __init__(self):
        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.rect = self.image.get_rect()

    # Draw a sin wave in the shape of a circle
    def create(self, rms):

        self.image.fill((0, 0, 0, 0))

        points = 1000
        point_list = []
        for i in range(points):
            angle = 2 * math.pi * i / points

            radius = 100 + (rms / 30) * (1 + math.sin(2 * math.pi * 5 * angle))
            x = CENTER[0] + (radius + rms/80 * math.sin(2 * math.pi * rms/500 * angle)) * math.cos(angle)
            y = CENTER[1] + (radius + rms/80 * math.sin(2 * math.pi * rms/500 * angle)) * math.sin(angle)

            point_list.append((x,y))

        if rms//3 > 255:
            x = 255
        else:
            x = rms //3

        pygame.draw.lines(self.image, (x, 255-x, 255), True, point_list, width=4)
        screen.blit(self.image, (0,0))

# Initialize Pygame
pygame.init()
WIDTH = 800
HEIGHT = 600
CENTER = (WIDTH /2, HEIGHT / 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visualiser")
clock = pygame.time.Clock()

circle = Sin_circle()

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

    # Draw the circle
    circle.create(rms)

    # Update the display
    pygame.display.flip()

# Clean up
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()