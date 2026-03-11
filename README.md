# 🧠 Battle of the Brain Rot

Welcome to **Battle of the Brain Rot**, the most unhinged hand-tracking chaos simulator known to man.  
Your mission: **smack the Gen Alpha brainrot characters** before they infect the timeline —  
but don’t destroy the *true* OG brainrot icons. Keep the legacy alive.

---

## 🎮 Gameplay

- **Move your hand** in front of your webcam — the game uses **MediaPipe + OpenCV** to track your hand.  
- **Close your fist** (or click your mouse) to *smack* characters.
- **Bad Guys (Gen Alpha brainrot):** Hit these clowns for points.
- **Good Guys (Classic brainrot):** Hit these by mistake, lose points. Skill issue.
- Timer runs for **2 minutes** — rack up the highest score you can before your sanity expires.

---

## 🖥️ Tech Stack

- 🐍 **Python 3.11**
- 🎮 **Pygame** – for graphics, sound, and chaos
- 👋 **OpenCV + MediaPipe** – for real-time hand tracking
- 🎵 **Custom sound effects** 

---

## 📦 Setup

Clone the repo and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/noah-dsouza/kill-the-brainrot.git
cd kill-the-brainrot

# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows

# Install dependencies
pip install pygame
pip install opencv-python mediapipe

# Run the game
python3 test_game_display.py
