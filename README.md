# Retro Space Shooter

A fullscreen browser-free arcade shooter built with Python, Pygame, OpenCV, and MediaPipe. The player controls a spaceship with hand gestures, dodges incoming asteroids, destroys alien ships, and survives as long as possible.

## ✨ Recent updates
- Fullscreen game mode with a polished starfield background
- Hand-tracking controls using MediaPipe for left/right movement and shooting gestures
- Custom spaceship, asteroid, and alien sprite assets
- Collision-based gameplay with score tracking and 3 lives
- Explosion effects and laser sound effects
- Background music support for the main game loop
- Start menu and game-over replay flow

## 🎮 Controls
- Move left/right: move your wrist or hand horizontally
- Shoot: bring your thumb close to your index finger
- Objective:
  - avoid asteroids
  - shoot alien enemies
  - survive and increase your score
- Starting lives: 3

## 🧰 Tech stack
- [Pygame](https://www.pygame.org/) — game rendering and gameplay loop
- [OpenCV](https://opencv.org/) — webcam input and image processing
- [MediaPipe](https://mediapipe.dev/) — real-time hand landmark detection
- [NumPy](https://numpy.org/) — frame manipulation and surface conversion

## 📁 Project files
- `main.py` — core game loop, hand tracking, collision logic, menus, and audio
- `requirements.txt` — Python dependencies
- `spaceship.png` — player ship sprite
- `Alien_image.xcf` — alien image source/project file
- `asteroid.xcf` — asteroid image source/project file
- `laser_sound/` — laser sound effects
- `explosion_sound/` — explosion sound effects
- `backgroundScore.mp3` — background music asset (if present in the project folder)

## ⚙️ Installation
1. Open a terminal in the project folder.
2. Create and activate a virtual environment if needed.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Run the game
```bash
python main.py
```

## 🎯 Gameplay notes
- The camera must be accessible to the machine running the game.
- The game uses a single tracked hand for movement and shooting.
- Press `Esc` to exit the game.
- Press `M` during gameplay to toggle background music on and off.

## 📝 Notes
This project is designed for local play and experimentation with hand-gesture controls. The current build assumes a webcam is connected and available through OpenCV.

