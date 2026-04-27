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

## Introduction
Knight Invasion is a two-player strategic board game on a 9×9 grid where both players use Artificial Intelligence techniques. The project focuses on implementing and comparing MiniMax and Fuzzy Logic in a competitive environment with movement and blocking constraints.

## Game Description
There are two knights on a 9×9 board.

- Knight-1 starts at (1,5)
- Knight-2 starts at (9,5)

The goal of each knight is to reach any cell of the opponent’s starting row. The player who goes first has a winning advantage.

## Allowed Moves

In each turn, a player can choose one of the following actions:

### 1. Knight Movement

- The knight moves using the standard chess knight move.
- A move consists of:
  - Two steps in one direction (up, down, left, or right), and
  - One step perpendicular to that direction.
- The knight can move to:
  - Any empty cell inside the 9×9 board
- The knight cannot move to:
  - Blocked cells
  - A cell already occupied by the opponent knight
  - A cell with Fire

### 2. Blocking Cells

- Instead of moving, a player may block exactly two empty cells in one turn.
- Blocked cells:
  - Become permanently unavailable for movement
  - Cannot contain any knight, fire, or already blocked

## Game Rules

### 1. Objective

- Knight-1 wins by reaching any cell of row 9.
- Knight-2 wins by reaching any cell of row 1.

### 2. Path Validity Rule

- After creating blocks, the opponent must still have at least one valid path
- The path must exist to at least one possible winning cell on the target row
- Path checking is done considering knight movement rules

### 3. Blocking Constraint

- A blocking move is invalid if it breaks the path validity rule.
- If it is not possible to place two valid blocks, the player must move the knight

### 4. Turn Rule

- Only one action per turn is allowed:
  - Either move the knight
  - Or block two cells

### 5. Fire Rule

- At the start of the game, randomly, some cells will burn in Fire
  - No knight can move in fire
  - No blocks can be placed here
  - Fire will never block all paths to the winning state
  - Fire placement will be symmetrical to both player sides

- Special rule
  - If the knight is adjacent to or in a corner of a fire cell, it must move

## AI Strategy

- Knight-1: Uses MiniMax Algorithm for optimal decision making.
- Knight-2: Uses Fuzzy Logic for heuristic-based decisions.
- Path validation is ensured using the graph traversal technique BFS.

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

## 🎮 Current Play Modes

- ✅ 2 Player (fully playable)
- ⏳ Player vs Fuzzy Agent (Coming Soon)
- ⏳ Player vs Minimax Agent (Coming Soon)
- ⏳ Minimax Agent vs Fuzzy Agent (Coming Soon)

---

## 🔥 Difficulty Fire Ranges

When starting a new 2-player game, difficulty controls total fire cells:

- Easy: 8-14 fire cells
- Medium: 16-22 fire cells
- Hard: 24-30 fire cells

Fire remains symmetrically generated and safe so both players keep at least one valid path.

---

## 📜 License

This project is developed for academic purposes under  
**CSE 3210: Artificial Intelligence Laboratory**