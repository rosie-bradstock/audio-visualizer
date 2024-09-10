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
pygame.display.set_caption("Visualizer")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()

# Colors
background_color = (0, 0, 0)

# Set up font
font = pygame.font.Font(None, 50)

# Dot class
class Dot(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        center = (random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10))
        self.movement_center = (0, 0)
        self.movement_spread = (0, 0)

        # Make the image
        self.image = pygame.Surface((10, 10))
        pygame.draw.circle(self.image, (255, 255, 255), (5, 5), 5)
        self.rect = self.image.get_rect()

        # Set initial position
        self.rect.center = center

    def go_to_center(self, rms):
        self.movement_center = (
            (WIDTH // 2 - self.rect.center[0]) / (20 - (rms / 1000)),
            (HEIGHT // 2 - self.rect.center[1]) / (20 - (rms / 1000))
        )

    def spread(self, rms):
        self.movement_spread = (
            (self.rect.center[0] - WIDTH // 2) / (20 - (rms / 1000)),
            (self.rect.center[1] - HEIGHT // 2) / (20 - (rms / 1000))
        )
    
    def update(self):
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
        elif self.rect.bottom < 0:
            self.rect.top = HEIGHT

        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH

        # Add some randomness to make the movement more natural
        random_movement = (
            random.uniform(-2, 2),
            random.uniform(-2, 2)
        )

        # Movement based on either center or spread, plus random movement
        self.movement = (
            self.movement_center[0] + self.movement_spread[0] + random_movement[0],
            self.movement_center[1] + self.movement_spread[1] + random_movement[1]
        )

        # Update the dot's position
        self.rect.center = (
            self.rect.center[0] + self.movement[0],
            self.rect.center[1] + self.movement[1]
        )

        # Gradually decrease the influence of movement_center and movement_spread
        self.movement_center = (self.movement_center[0] * 0.9, self.movement_center[1] * 0.9)
        self.movement_spread = (self.movement_spread[0] * 0.9, self.movement_spread[1] * 0.9)

# Make some dots
for i in range(50):
    dot = Dot()
    all_sprites.add(dot)

running = True

while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read audio data from the stream (specified number of samples) and calculate the rms
    rms = get_rms(stream.read(CHUNK))

    if rms > 100:
        for sprite in all_sprites:
            sprite.go_to_center(rms)
    else:
        for sprite in all_sprites:
            sprite.spread(rms)

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
