# AI Solver for Escape Room Game

## Overview
The AI Solver automatically plays the escape room game using advanced AI algorithms, eliminating the need for human gameplay. It demonstrates the integration of multiple AI paradigms working together to solve complex problems.

## What the AI Solver Does

### 🎯 **Intelligent Decision Making**
- **Priority-based target selection**: Keys → Exit → Exploration
- **Risk assessment**: Uses Bayesian reasoning to avoid dangerous rooms
- **Strategic pathfinding**: Chooses optimal routes based on trap probability

### 🔍 **AI Algorithms Integrated**
1. **A* Search**: Finds optimal paths considering distance + trap risk
2. **Bayesian Reasoning**: Updates trap probabilities as rooms are explored
3. **CSP Solver**: Automatically solves puzzles using backtracking
4. **Minimax Integration**: Accounts for guard movements in pathfinding

### 📊 **Strategy Options**
- **Conservative (Low Risk)**: Avoids rooms with >10% trap probability
- **Balanced (Medium Risk)**: Tolerates up to 30% trap probability  
- **Aggressive (High Risk)**: Accepts up to 70% trap probability
- **Fast BFS**: Uses shortest path regardless of risks

## How to Use

### 🚀 **Quick Start**
```bash
# Silent mode (fastest, just results)
python ai_solver.py
# Choose option 1

# Detailed mode (shows all decisions)
python ai_solver.py
# Choose option 2

# Summary mode (shows key events)
python ai_solver.py
# Choose option 3
```

### 🧪 **Strategy Comparison**
```bash
# Compare 4 different AI strategies
python demo_ai_solver.py
# Choose option 2
```

### ⚡ **Quick Test**
```bash
# Fast execution with minimal output
python demo_ai_solver.py
# Choose option 3
```

## Example Results

### 🏆 **Successful Escape Example**
```
FINAL RESULTS
============================================================
Success: ✅ YES
Turns Used: 11/100
Health Remaining: 40/100
Keys Collected: 3/3
Puzzles Solved: 0
Total Moves: 11
Rooms Explored: 12
Traps Triggered: 3
🎉 CONGRATULATIONS! The AI successfully escaped!
```

### 📈 **Strategy Comparison Results**
| Strategy | Success | Turns | Health | Efficiency |
|----------|---------|-------|---------|------------|
| Fast BFS | ✅ | 7 | 60 | **Fastest** |
| Conservative | ✅ | 11 | 40 | **Safest** |
| Balanced | ✅ | 11 | 40 | **Balanced** |
| Aggressive | ✅ | 20 | 20 | **Riskiest** |

## Key Features

### 🎮 **Automatic Gameplay**
- No human input required
- Makes intelligent decisions autonomously
- Handles all game mechanics (movement, puzzles, trap avoidance)

### 🧠 **AI Intelligence**
- **A* with custom heuristic**: Distance + trap risk
- **Bayesian updates**: Learns from room exploration
- **Automated CSP solving**: Handles puzzles of all difficulties
- **Guard prediction**: Considers adversarial movements

### 📊 **Performance Metrics**
- Turn efficiency (fewer turns = better)
- Health preservation (higher = better)
- Risk management (trap avoidance)
- Path optimization (A* vs BFS comparison)

## Technical Implementation

### 🔧 **Core Components**
```python
class AISolver:
    - Environment & Agent setup
    - Strategic target selection  
    - A*/BFS pathfinding
    - Automated puzzle solving
    - Bayesian probability updates
    - Guard movement prediction
```

### 🎯 **Decision Algorithm**
1. **Target Selection**: Keys → Exit → Safe exploration
2. **Risk Assessment**: Bayesian trap probabilities
3. **Path Planning**: A* with heuristic (distance + risk)
4. **Puzzle Solving**: Automated CSP backtracking
5. **Movement Execution**: Step-by-step navigation
6. **State Updates**: Belief system and game metrics

## Benefits

### 🎓 **Educational Value**
- Demonstrates AI algorithm integration
- Shows real-world problem solving
- Illustrates trade-offs between strategies
- Provides measurable performance metrics

### 🔬 **Research Applications**
- Algorithm comparison framework
- Performance benchmarking
- Strategy effectiveness analysis
- Multi-agent system interactions

### 🎮 **Game Development**
- Automated testing for escape rooms
- Difficulty balancing insights
- Player behavior modeling
- AI opponent generation

## Customization

### ⚙️ **Adjustable Parameters**
```python
# Risk tolerance (0.0 = very safe, 1.0 = very risky)
solver.risk_tolerance = 0.3

# Search algorithm choice
solver.use_astar = True  # A* with heuristic
# solver.use_astar = False  # BFS (faster, less optimal)

# Verbosity levels
solver.verbose = True  # Detailed output
# solver.verbose = False  # Silent execution
```

### 🧪 **Experiment Ideas**
- Compare different search algorithms
- Test various risk tolerances
- Analyze puzzle difficulty impact
- Study guard AI effectiveness
- Measure algorithm convergence

## Files Created

- **`ai_solver.py`**: Main AI solver implementation (348 lines)
- **`demo_ai_solver.py`**: Strategy comparison and demo scripts (143 lines)
- **`README_AI_SOLVER.md`**: This documentation

The AI solver successfully demonstrates how multiple AI techniques can work together to solve complex, uncertain, and adversarial problems in an automated fashion!