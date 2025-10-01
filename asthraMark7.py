import pygame
import random
import math
import cv2
import mediapipe as mp
import numpy as np
import logging
import os

# Set working directory to script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"Working directory set to: {os.getcwd()}")

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logging.getLogger('mediapipe').setLevel(logging.ERROR)

# Suppress TensorFlow Lite warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Initialize Pygame
pygame.init()
logging.info("Pygame initialized")

# Set up display in fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_info = pygame.display.Info()
WIDTH = screen_info.current_w
HEIGHT = screen_info.current_h
CAM_WIDTH = 200
CAM_HEIGHT = 150
pygame.display.set_caption("Retro Space Shooter with Hand Tracking")

# Initialize OpenCV webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    logging.error("Failed to open webcam")
    exit()
logging.info("Webcam initialized")

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
logging.info("MediaPipe Hands initialized")

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (100, 100, 100)
PURPLE = (255, 0, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)

# Font setup
font = pygame.font.Font(None, 74)
title_font = pygame.font.Font(None, 100)
game_font = pygame.font.Font(None, 36)
instruction_font = pygame.font.Font(None, 24)

# Background with stars
background = pygame.Surface((WIDTH, HEIGHT))
background.fill(BLACK)
for _ in range(int(WIDTH * HEIGHT / 4000)):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    pygame.draw.circle(background, WHITE, (x, y), random.randint(1, 3))

# Load custom spaceship image
SPACESHIP_IMAGE_PATH = r"C:\Users\Deon George\OneDrive\Desktop\python programs\Retro_Space_shooter\spaceship.png"
ALIEN_IMAGE_PATH = r"C:\Users\Deon George\OneDrive\Desktop\python programs\Retro_Space_shooter\Alien_image.xcf"
ASTEROID_IMAGE_PATH = r"C:\Users\Deon George\OneDrive\Desktop\python programs\Retro_Space_shooter\asteroid.xcf"
try:
    spaceship_base_image = pygame.image.load(SPACESHIP_IMAGE_PATH).convert_alpha()
    player_spaceship_image = pygame.transform.scale(spaceship_base_image, (80, 60))
    menu_spaceship_image = pygame.transform.scale(spaceship_base_image, (80, 60))
except FileNotFoundError:
    print(f"Error: Could not load {SPACESHIP_IMAGE_PATH}. Using fallback.")
    player_spaceship_image = pygame.Surface((40, 30), pygame.SRCALPHA)
    pygame.draw.polygon(player_spaceship_image, GREEN, [(20, 0), (0, 30), (40, 30)])
    menu_spaceship_image = pygame.Surface((50, 40), pygame.SRCALPHA)
    pygame.draw.polygon(menu_spaceship_image, GREEN, [(25, 0), (0, 40), (50, 40)])

try:
    alien_base_image = pygame.image.load(ALIEN_IMAGE_PATH).convert_alpha()
    alien_image = pygame.transform.scale(alien_base_image, (60, 40))
except FileNotFoundError:
    print(f"Error: Could not load {ALIEN_IMAGE_PATH}. Using fallback.")
    alien_image = pygame.Surface((30, 20), pygame.SRCALPHA)
    pygame.draw.rect(alien_image, PURPLE, (0, 0, 30, 20))
    pygame.draw.circle(alien_image, PURPLE, (15, 10), 10)

try:
    asteroid_base_image = pygame.image.load(ASTEROID_IMAGE_PATH).convert_alpha()
    asteroid_image = pygame.transform.scale(asteroid_base_image, (40, 30))
except FileNotFoundError:
    print(f"Error: Could not load {ASTEROID_IMAGE_PATH}. Using fallback.")
    asteroid_image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(asteroid_image, GRAY, (15, 15), 15)

# Player (Spaceship)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_spaceship_image
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5
        self.lives = 3
        self.last_shot = 0
        self.shoot_delay = 500
        self.direction = "none"

    def update(self, direction="none"):
        self.direction = direction
        if direction == "left" and self.rect.left > 0:
            self.rect.x -= self.speed
        elif direction == "right" and self.rect.right < WIDTH - CAM_WIDTH:
            self.rect.x += self.speed
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH - CAM_WIDTH, HEIGHT))
        self.image = self.original_image.copy()
        if direction != "none":
            for _ in range(random.randint(1, 3)):
                pygame.draw.circle(self.image, ORANGE if random.random() > 0.5 else YELLOW,
                                 (20, 32), random.randint(3, 6))

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot >= self.shoot_delay:
            laser = Laser(self.rect.centerx, self.rect.top)
            all_sprites.add(laser)
            lasers.add(laser)
            laser_sound.play()
            print("Laser sound should play")
            self.last_shot = current_time

# Laser
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = asteroid_image
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - CAM_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed = random.randrange(1, 4)
        self.angle = 0
        self.rotation_speed = random.uniform(-3, 3)

    def update(self):
        self.rect.y += self.speed
        self.angle = (self.angle + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(0, WIDTH - CAM_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed = random.randrange(1, 4)

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = alien_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - CAM_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed = random.randrange(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(0, WIDTH - CAM_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed = random.randrange(2, 5)

# Explosion Animation
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        for i in range(8):
            img = pygame.Surface((50, 50), pygame.SRCALPHA)
            radius = (i + 1) * 6
            alpha = int(255 * (1 - i / 8))
            pygame.draw.circle(img, (ORANGE[0], ORANGE[1], ORANGE[2], alpha), (25, 25), radius, 3)
            pygame.draw.circle(img, (YELLOW[0], YELLOW[1], YELLOW[2], alpha), (25, 25), radius - 3, 2)
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.frame_rate = 4
        self.frame_count = 0
        self.particles = [(random.randint(-3, 3), random.randint(-3, 3)) for _ in range(8)]

    def update(self):
        self.frame_count += 1
        if self.frame_count >= self.frame_rate:
            self.frame_count = 0
            self.index += 1
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index].copy()
                for i, (dx, dy) in enumerate(self.particles):
                    px = self.rect.centerx + dx * self.index * 2
                    py = self.rect.centery + dy * self.index * 2
                    pygame.draw.circle(self.image, YELLOW, (int(px - self.rect.x), int(py - self.rect.y)), 2)

# Hand tracking function
def get_hand_input():
    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to read webcam frame")
        return None, False, None
    
    try:
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        direction = None
        shoot = False
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                wrist = hand_landmarks.landmark[0]
                index_tip = hand_landmarks.landmark[8]
                thumb_tip = hand_landmarks.landmark[4]
                
                wrist_x = wrist.x * WIDTH
                index_x = index_tip.x * WIDTH
                
                if index_x < wrist_x - 50:
                    direction = "left"
                elif index_x > wrist_x + 50:
                    direction = "right"
                    
                thumb_index_dist = math.sqrt(
                    (thumb_tip.x - index_tip.x)**2 + 
                    (thumb_tip.y - index_tip.y)**2
                )
                print(f"Thumb-Index Distance: {thumb_index_dist}")
                if thumb_index_dist < 0.1:
                    shoot = True
                    print("Shoot detected")
                    
                cv2.putText(frame, f"Dir: {direction or 'None'}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
                cv2.putText(frame, f"Shoot: {shoot}", (10, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        
        frame = cv2.resize(frame, (CAM_WIDTH, CAM_HEIGHT))
        frame_surface = pygame.surfarray.make_surface(np.rot90(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        logging.debug("Deonex accessing the camera successfully")
        return direction, shoot, frame_surface
    except Exception as e:
        logging.error(f"Error processing hand input: {e}")
        return None, False, None

# Sprite groups
all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
aliens = pygame.sprite.Group()
lasers = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# Sound setup
pygame.mixer.quit()
pygame.mixer.init(frequency=44100, size=-16, channels=2)
print("Mixer initialized with frequency=44100, size=-16, channels=2")
laser_sound = pygame.mixer.Sound(r"C:\Users\Deon George\OneDrive\Desktop\python programs\Retro_Space_shooter\laser_sound\laser1.mp3")
laser_sound.set_volume(1.0)
explosion_sound = pygame.mixer.Sound(r"C:\Users\Deon George\OneDrive\Desktop\python programs\Retro_Space_shooter\explosion_sound\explosion1.mp3")
explosion_sound.set_volume(1.0)
# NEW: Background music setup
BACKGROUND_MUSIC_PATH = r"C:\Users\Deon George\OneDrive\Desktop\python programs\Retro_Space_shooter\interstellar_background_music.mp3"
try:
    pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
    pygame.mixer.music.set_volume(0.5)  # Set to 50% volume (adjust as needed)
    print("Background music loaded successfully")
except pygame.error as e:
    print(f"Error loading background music: {e}")

print("Sounds loaded successfully at full volume")

# Function to reset the game
def reset_game():
    global all_sprites, asteroids, aliens, lasers, explosions, player, score
    all_sprites.empty()
    asteroids.empty()
    aliens.empty()
    lasers.empty()
    explosions.empty()
    player = Player()
    all_sprites.add(player)
    for i in range(8):
        asteroid = Asteroid()
        all_sprites.add(asteroid)
        asteroids.add(asteroid)
    for i in range(4):
        alien = Alien()
        all_sprites.add(alien)
        aliens.add(alien)
    score = 0

# Menu spaceship animation
original_spaceship = menu_spaceship_image
spaceship_angle = 0
spaceship_rotation_speed = 2
spaceship_y_offset = 0

# Initial game state
game_state = "menu"
score = 0

# Instruction text
instruction_text = instruction_font.render("Hand: Move left/right, Thumb near index to shoot", True, WHITE)
title_text = title_font.render("Retro Space Shooter", True, WHITE)

# Game loop
clock = pygame.time.Clock()
running = True

# NEW: Start background music before the game loop
pygame.mixer.music.play(-1)  # -1 means loop indefinitely

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "menu" and start_button.collidepoint(mouse_pos):
                reset_game()
                game_state = "playing"
            elif game_state == "game_over" and play_again_button.collidepoint(mouse_pos):
                reset_game()
                game_state = "playing"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                laser_sound.play()
                print("Manually playing laser sound")
            elif event.key == pygame.K_e:
                explosion_sound.play()
                print("Manually playing explosion sound")
            # NEW: Add key to toggle music
            elif event.key == pygame.K_m:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                    print("Music paused")
                else:
                    pygame.mixer.music.unpause()
                    print("Music resumed")

    if game_state == "menu":
        screen.blit(background, (0, 0))
        
        spaceship_angle = (spaceship_angle + spaceship_rotation_speed) % 360
        spaceship_y_offset = math.cos(math.radians(spaceship_angle)) * 10
        menu_spaceship = pygame.transform.rotate(original_spaceship, math.sin(math.radians(spaceship_angle)) * 15)
        spaceship_rect = menu_spaceship.get_rect(center=(WIDTH // 2 - 150, HEIGHT // 2 - 100 + spaceship_y_offset))
        thruster_surface = menu_spaceship.copy()
        for _ in range(random.randint(1, 3)):
            pygame.draw.circle(thruster_surface, ORANGE if random.random() > 0.5 else YELLOW,
                             (25, 42), random.randint(4, 7))
        screen.blit(thruster_surface, spaceship_rect)
        
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(title_text, title_rect)
        
        start_text = font.render("Start", True, YELLOW)
        start_button = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        button_bg_color = DARK_GRAY if start_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, button_bg_color, start_button.inflate(20, 10))
        pygame.draw.rect(screen, RED, start_button.inflate(20, 10), 2)
        screen.blit(start_text, start_button)

    elif game_state == "playing":
        direction, shoot, frame_surface = get_hand_input()
        
        player.update(direction)
        if shoot:
            player.shoot()

        all_sprites.update()
        explosions.update()

        hits = pygame.sprite.groupcollide(aliens, lasers, True, True)
        for hit in hits:
            score += 10
            explosion = Explosion(hit.rect.centerx, hit.rect.centery)
            all_sprites.add(explosion)
            explosions.add(explosion)
            explosion_sound.play()
            print("Explosion sound should play")
            alien = Alien()
            all_sprites.add(alien)
            aliens.add(alien)

        asteroid_hits = pygame.sprite.spritecollide(player, asteroids, True)
        alien_hits = pygame.sprite.spritecollide(player, aliens, True)
        if asteroid_hits or alien_hits:
            player.lives -= 1
            explosion_sound.play()
            print("Explosion sound should play (player hit)")
            for hit in asteroid_hits:
                asteroid = Asteroid()
                all_sprites.add(asteroid)
                asteroids.add(asteroid)
            for hit in alien_hits:
                alien = Alien()
                all_sprites.add(alien)
                aliens.add(alien)
            if player.lives <= 0:
                game_state = "game_over"

        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        explosions.draw(screen)
        
        score_text = game_font.render(f"Score: {score}", True, WHITE)
        lives_text = game_font.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))

        instruction_rect = instruction_text.get_rect(topright=(WIDTH - 10, 10))
        screen.blit(instruction_text, instruction_rect)

        if frame_surface:
            cam_x = max(0, min(WIDTH - CAM_WIDTH, WIDTH - CAM_WIDTH))
            cam_y = max(0, min(HEIGHT - CAM_HEIGHT, HEIGHT - CAM_HEIGHT))
            screen.blit(frame_surface, (cam_x, cam_y))
            pygame.draw.rect(screen, RED, (cam_x, cam_y, CAM_WIDTH, CAM_HEIGHT), 2)
        else:
            logging.warning("No frame surface returned from get_hand_input")

    elif game_state == "game_over":
        screen.blit(background, (0, 0))
        game_over_text = font.render("Game Over!!", True, WHITE)
        score_text = game_font.render(f"Final Score: {score}", True, WHITE)
        play_again_text = font.render("Play Again", True, YELLOW)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        play_again_button = play_again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        button_bg_color = DARK_GRAY if play_again_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, button_bg_color, play_again_button.inflate(20, 10))
        pygame.draw.rect(screen, RED, play_again_button.inflate(20, 10), 2)
        screen.blit(game_over_text, game_over_rect)
        screen.blit(score_text, score_rect)
        screen.blit(play_again_text, play_again_button)

    pygame.display.flip()
    clock.tick(60)

# NEW: Stop music when game ends
pygame.mixer.music.stop()
cap.release()
pygame.quit()