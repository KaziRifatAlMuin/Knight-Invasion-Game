# 🧠 Knight Invasion Game

A strategic **two-player AI board game** where two intelligent agents compete using different decision-making techniques: **Minimax vs Fuzzy Logic**.

---

## 🎯 Overview

**Knight Invasion** is played on a **9×9 grid**, where each player controls a knight.

### Objective:
- Reach the opponent’s starting row before they reach yours.
- Use movement and blocking strategies to gain advantage.

---

## 🤖 AI Agents

- **🔴 agent_red (Red Knight)**
  - Algorithm: Minimax
  - Developer: Kazi Rifat Al Muin
  - Strategy: Optimal decision making using game tree search

- **🔵 agent_blue (Blue Knight)**
  - Algorithm: Fuzzy Logic
  - Developer: Dipta Chowdhury
  - Strategy: Heuristic-based decision making

---

## 🎮 Game Setup

- Board Size: **9 × 9**
- Initial Positions:
  - Red Knight → (1, 5)
  - Blue Knight → (9, 5)

---

## 🕹️ Gameplay Mechanics

Each turn, a player chooses ONE action:

### ♞ 1. Knight Movement
- Moves like a chess knight:
  - 2 steps in one direction + 1 step perpendicular
- Cannot move to:
  - Blocked cells
  - Fire cells
  - Opponent’s position

### 🚫 2. Blocking Cells
- Block exactly **two empty cells**
- Blocked cells:
  - Are permanent
  - Cannot be used again

---

## 🧩 Game Rules

### 🏆 Objective
- Red wins → reaches **row 9**
- Blue wins → reaches **row 1**

### 🔄 Turn Rule
- Only one action per turn:
  - Move OR block

### 🚧 Path Validity Rule
- Blocking must NOT remove all valid paths
- Opponent must always have at least one path to goal
- Path checking done using **BFS**

### ⚠️ Blocking Constraint
- Invalid if it breaks path rule
- If no valid block possible → must move

---

## 🔥 Fire Mechanics

- Random cells contain fire at start
- Fire cells:
  - Cannot be entered
  - Cannot be blocked
  - Are symmetrically placed
  - Never block all paths

---

## 🧠 AI Strategy

| Agent       | Technique     | Description                      |
|------------|--------------|----------------------------------|
| Red Knight | Minimax      | Optimal adversarial search       |
| Blue Knight| Fuzzy Logic  | Rule-based heuristic decisions   |

---

## 🛠️ Technologies Used

- Python (assumed)
- Artificial Intelligence
- Minimax Algorithm
- Fuzzy Logic System
- BFS (Graph Traversal)

---

## 🚀 How to Run

```bash
# Clone the repository
git clone https://github.com/KaziRifatAlMuin/Knight-Invasion-Game.git

# Go to project folder
cd Knight-Invasion-Game

# Run the game
python main.py
```


## 📁 Project Structure

    Knight-Invasion-Game/
    │── main.py
    │── game/
    │   ├── board.py
    │   ├── rules.py
    │── agents/
    │   ├── minimax_agent.py
    │   ├── fuzzy_agent.py
    │── utils/
    │   ├── bfs.py
    │── assets/
    │── README.md

---

## 👥 Contributors

**Kazi Rifat Al Muin**  
Roll: 2107042  
Minimax AI  

**Dipta Chowdhury**  
Roll: 2107038  
Fuzzy AI  

---

## 🎯 Project Goal

- Compare **Minimax vs Fuzzy Logic**
- Analyze performance in adversarial environment
- Study optimal vs heuristic decision-making

---

## 📌 Features

- AI vs AI gameplay  
- Strategic blocking system  
- Path validation using BFS  
- Random obstacles (fire)  
- Turn-based mechanics  

---

## 📜 License

This project is developed for academic purposes under  
**CSE 3210: Artificial Intelligence Laboratory**