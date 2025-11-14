# AI Escape Room 🎮

An intelligent, gamified simulation where an autonomous agent navigates a dynamic maze-like environment to escape. The project demonstrates the integration of multiple AI paradigms working together to solve complex problems in uncertain and adversarial environments.

## 🤖 AI Techniques Integrated

### 1. **Search Algorithms** (Pathfinding & Planning)
- **BFS (Breadth-First Search)**: Finds shortest path to goals
- **A* Search**: Optimal pathfinding with heuristics considering trap risks
- Used for: Finding keys, planning escape routes, exploring the environment

### 2. **Constraint Satisfaction Problems (CSP)**
- **Backtracking solver**: Solves puzzles to unlock doors
- **Progressive difficulty**: Easy → Medium → Hard puzzles
- Demonstrates: Variable assignment, domain constraints, and constraint propagation

### 3. **Adversarial Search (Minimax)**
- **Minimax algorithm**: Guard AI that strategically pursues the player
- **Depth-limited search**: Looks ahead multiple moves
- **Alpha-Beta pruning** ready for optimization
- Demonstrates: Zero-sum game theory, optimal adversarial strategy

### 4. **Bayesian Reasoning**
- **Belief updating**: Agent maintains probabilistic beliefs about trap locations
- **Bayes' theorem**: Updates beliefs based on observations
- **Risk assessment**: Evaluates path safety using probability distributions
- Demonstrates: Decision-making under uncertainty

## 📂 Project Structure

```
├── config.py              # Configuration settings
├── environment.py         # Room graph, map generation
├── agent.py              # Player agent with search algorithms
├── guard.py              # Adversarial guard with Minimax
├── csp_solver.py         # CSP puzzle generator and solver
├── bayesian_reasoning.py # Bayesian belief system
├── game.py               # Terminal game loop
├── gui_pygame.py         # 🎨 Pygame GUI version
├── launcher.py           # Game launcher (choose interface)
├── test_components.py    # Component testing
├── quick_demo.py         # Quick demonstration
└── GUI_GUIDE.md          # GUI usage guide
```

## 🎯 Game Objective

- **Collect all keys** hidden throughout the rooms
- **Solve puzzles** (CSP) to unlock doors
- **Avoid traps** using Bayesian reasoning
- **Evade the guard** that uses Minimax to catch you
- **Reach the exit** before running out of health or turns

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- **Terminal version**: No dependencies (uses Python standard library)
- **GUI version**: Requires pygame (`pip install pygame`)

### Easy Launcher (Recommended)

```bash
python launcher.py
```

Choose from:
1. Terminal Version (text-based)
2. GUI Version (visual Pygame interface)
3. Quick Demo
4. Run Tests

### Running Directly

**Terminal Version:**
```bash
python game.py
```

**GUI Version (Visual):**
```bash
# Install pygame first
pip install pygame

# Run GUI
python gui_pygame.py
```

**Quick Demo:**
```bash
python quick_demo.py
```

### Testing Individual Components

```bash
# Test all components
python test_components.py

# Test specific components
python csp_solver.py          # Test CSP puzzles
python bayesian_reasoning.py  # Test Bayesian belief system
python agent.py               # Test search algorithms
python guard.py               # Test Minimax guard AI
```

## ⚙️ Configuration

Edit `config.py` or modify settings in `game.py` to customize:

```python
# Map size
MAP_SIZE = "medium"  # Options: "small", "medium", "large"

# Search algorithm
SEARCH_ALGORITHM = "astar"  # Options: "bfs", "astar"

# Puzzle difficulty
PUZZLE_DIFFICULTY = "progressive"  # Options: "easy", "medium", "hard", "progressive"

# Guard settings
GUARD_ENABLED = True
MINIMAX_DEPTH = 3
GUARD_VISION_RANGE = 3

# Game parameters
NUM_KEYS = 3
NUM_TRAPS = 4
MAX_TURNS = 100
```

## 🎮 How to Play

### Available Actions

1. **Move to adjacent room**: Navigate through connected rooms
2. **Solve puzzle**: Use CSP solver to unlock doors
3. **Find path to nearest key**: AI plans route to closest uncollected key
4. **Plan escape route**: AI calculates optimal path to exit
5. **View belief state**: See Bayesian probability estimates for traps
6. **View guard status**: Check guard location and Minimax decisions

### Game Elements

- **🔑 Keys**: Collect all to unlock the final exit
- **🧩 Puzzles**: Logic puzzles modeled as CSPs
- **⚠️ Traps**: Hidden dangers that reduce health
- **👮 Guard**: Adversarial AI hunting the player
- **🚪 Exit**: Goal location to escape

### Strategy Tips

- Use A* search to find efficient paths while avoiding risky rooms
- Update your beliefs about traps as you explore
- Solve puzzles strategically to open new routes
- Keep distance from the guard (check distances regularly)
- Balance risk vs. reward when choosing paths

## 🎨 GUI Version (Pygame)

### Visual Features

The Pygame GUI provides a rich visual experience:

- **🗺️ Interactive Map**: Circular room layout with real-time visualization
- **🎨 Bayesian Heatmap**: Color-coded rooms showing trap probabilities
  - 🟢 Green = Low risk (< 30%)
  - 🟡 Yellow = Medium risk (30-60%)
  - 🔴 Red = High risk (> 60%)
- **🔍 Path Visualization**: Yellow lines showing A* search paths
- **📊 Live Statistics**: Health bars, key count, turn tracking
- **🎮 Click Controls**: Interactive buttons for all actions
- **📝 Event Log**: Scrolling log of all game events
- **🤖 AI Visualization**: Watch agents move in real-time

### GUI Controls

- **Auto Move** - Agent moves to safest adjacent room
- **Find Key** - Displays optimal path to nearest key
- **Plan Escape** - Shows complete route to exit
- **Solve Puzzle** - Unlocks doors using CSP solver
- **Next Turn** - Process guard's move

**Keyboard:**
- **ESC** - Quit game
- **R** - Restart (when game over)

### Installation

```bash
# Install pygame
pip install pygame

# Or install all dependencies
pip install -r requirements.txt

# Run GUI
python gui_pygame.py
```

For detailed GUI instructions, see <filepath>GUI_GUIDE.md</filepath>

## 📊 Technical Details

### Search Algorithms
- **State space**: Agent location, keys collected, doors unlocked, guard position
- **Actions**: Move, solve puzzle, wait
- **Heuristics**: Distance to goal + trap risk probability

### CSP Formulation
- **Variables**: Lock digits/symbols
- **Domains**: Possible values (1-6 typically)
- **Constraints**: Sum constraints, ordering, uniqueness, arithmetic

### Minimax Implementation
- **Utility function**: Distance-based evaluation
- **Depth-limited**: Configurable look-ahead depth
- **Assumptions**: Both players act optimally
- **Pruning ready**: Alpha-beta optimization available

### Bayesian Belief Updates
- **Prior**: Initial uniform probability distribution
- **Likelihood**: Observation reliability (configurable)
- **Posterior**: Updated using Bayes' theorem
- **Propagation**: Spatial correlation of trap probabilities

## 📈 Evaluation Metrics

The game tracks performance across multiple dimensions:

- **Success rate**: Victory vs. defeat
- **Efficiency**: Turns and moves to escape
- **Algorithm performance**: Nodes expanded, backtracks
- **Health preservation**: Trap avoidance effectiveness
- **Puzzle solving**: CSP solver performance

## 🎓 Educational Value

This project demonstrates:

1. **AI Integration**: How multiple AI paradigms work together
2. **Search vs. Planning**: Difference between finding paths and strategic planning
3. **Deterministic vs. Probabilistic**: CSP/Search vs. Bayesian reasoning
4. **Adversarial AI**: Game theory and optimal strategies
5. **Real-world Applications**: Robotics, security, adaptive systems

## 🔮 Future Extensions

- **Reinforcement Learning**: Train agent to learn optimal strategies
- **Multi-agent scenarios**: Multiple guards or cooperative agents
- **3D environments**: Expand to three-dimensional spaces
- **Natural Language Processing**: Puzzle hints and story elements
- **GUI Interface**: Pygame or web-based visualization
- **Dynamic environments**: Rooms that change over time
- **Multiple difficulty modes**: Beginner to expert challenges

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_components.py
```

This tests:
- Environment generation and connectivity
- Search algorithm correctness
- CSP solver accuracy
- Bayesian belief updates
- Minimax decision-making
- Game integration

## 📝 Implementation Notes

### Design Principles
- **Modularity**: Each AI component is independent
- **Extensibility**: Easy to add new features
- **Configurability**: Adjust difficulty and behavior
- **Testability**: Each module has standalone tests

### Code Organization
- **Separation of concerns**: AI logic separate from game logic
- **Type hints**: Modern Python typing for clarity
- **Documentation**: Comprehensive docstrings
- **Clean interfaces**: Well-defined APIs between modules

## 👥 Contributing

This project was built as an educational AI demonstration. Potential contributions:

- Additional puzzle types (Sudoku, graph coloring)
- GUI implementation
- Performance optimizations
- Machine learning integration
- More sophisticated heuristics

## 📄 License

This project is intended for educational purposes.

## 🙏 Acknowledgments

Built to demonstrate practical applications of:
- Classical AI search techniques
- Constraint satisfaction solving
- Game theory and adversarial search
- Probabilistic reasoning under uncertainty

---

**Author**: MiniMax Agent  
**Purpose**: AI Education & Research  
**Techniques**: Search, CSP, Minimax, Bayesian Inference  
