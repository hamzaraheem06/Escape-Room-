# AI Escape Room - User Guide

## 🎮 How to Play

### Starting the Game

```bash
python game.py
```

The game will display:
- Welcome screen and story
- Map information
- Your objective
- AI techniques being used

Press ENTER to begin.

## 🎯 Your Objective

1. **Collect all keys** (typically 3) hidden in rooms
2. **Reach the exit room** (usually the last room)
3. **Survive** - Don't let health reach 0
4. **Avoid the guard** - Don't get caught!

## 🕹️ Game Controls

On each turn, you can choose from 7 actions:

### 1. Move to Adjacent Room
- View all accessible rooms from your current location
- See risk levels for each room (based on Bayesian beliefs)
- See if rooms have been visited before
- Choose which room to move to

**Strategy Tips:**
- Check trap probabilities before moving
- Green (🟢) = Low risk, Yellow (🟡) = Medium risk, Red (🔴) = High risk
- Visit new rooms to explore
- Avoid rooms where guard was recently spotted

### 2. Solve Puzzle
- Unlocks doors by solving CSP puzzles
- Puzzles get progressively harder
- The AI solver will automatically solve them
- Watch the solver work through the constraints

**Strategy Tips:**
- Solve puzzles early to open new routes
- More routes = easier to avoid guard
- Check what's beyond locked doors first

### 3. Find Path to Nearest Key
- Uses A* search algorithm to find optimal path to closest key
- Shows distance and estimated risk
- Doesn't automatically move - just shows the plan

**Strategy Tips:**
- Use this to plan your key collection route
- Compare paths to different keys
- Consider trap probabilities in path risk

### 4. Plan Escape Route
- Calculates optimal path to exit
- Shows full route with room details
- Displays estimated risk for each room

**Strategy Tips:**
- Plan ahead before collecting last key
- Know your escape route in advance
- Have backup routes if guard blocks main path

### 5. View Belief State
- Shows Bayesian probability estimates for all rooms
- Categories: Verified, High Risk, Medium Risk, Low Risk
- See how your observations have updated beliefs

**Strategy Tips:**
- Check this after each trap encounter
- Notice how beliefs propagate to nearby rooms
- Use to choose safest exploration routes

### 6. View Guard Status
- Shows guard's current location
- Displays distance from you
- Indicates if guard can detect you

**Strategy Tips:**
- Monitor guard position frequently
- Stay outside guard's vision range (default: 3 rooms)
- Guard uses Minimax - it predicts your moves!

### 7. Quit Game
- Exit the game
- Shows final statistics

## 📊 Understanding the Display

### Agent Status
```
============================================================
AGENT STATUS
============================================================
Location: Library (Room 3)
Health: 80/100
Keys: 2/3 collected
Moves: 15
Traps triggered: 1
Puzzles solved: 2
Rooms visited: 8/12
```

### Available Moves
```
Available moves: 3 rooms
  → Room 2: Storage Room [Low risk, P=0.15] ✓
  → Room 4: Kitchen [HIGH RISK, P=0.75] ?
  → Room 5: Dungeon [MEDIUM RISK, P=0.45] ?
```
- ✓ = Visited before
- ? = Not yet visited
- P = Probability of trap

### Belief State
```
VERIFIED (Observed):
  Room 3: SAFE (P=0.00)
  Room 7: HAS TRAP (P=1.00)

HIGH RISK (P > 0.6):
  Room 8: P=0.72
  
MEDIUM RISK (0.3 < P < 0.6):
  Room 4: P=0.45
  Room 9: P=0.38

LOW RISK (P < 0.3): 7 rooms
```

## 🎓 AI Techniques in Action

### Watch the AI Work!

**Search Algorithms:**
```
[A*] Path found! Length: 5, Cost: 4.00, Nodes expanded: 6
Path: 0 → 1 → 3 → 7 → 11
```
- See how many nodes A* explores
- Compare with your mental path
- Lower cost = better path

**CSP Solver:**
```
[MEDIUM PUZZLE] Find A, B, C where:
  - A + B + C = 10
  - All different values
  - A < B
  - Each is between 1-5

Solution found: {'A': 1, 'B': 3, 'C': 6}
Nodes expanded: 10, Backtracks: 38
```
- Watch backtracking in action
- See constraint satisfaction

**Minimax Guard:**
```
👮 Guard moved from Room 4 to Room 3 (distance to player: 2)
```
- Guard is trying to minimize distance to you
- It predicts where you'll go next
- Uses game theory for optimal pursuit

**Bayesian Updates:**
```
Room 5: P(trap) = 0.20  [before]
→ Entered Room 5 safely
Room 5: P(trap) = 0.03  [after]
```
- Watch probabilities update with evidence
- See belief propagation to nearby rooms

## 🏆 Winning Strategies

### Early Game (Turns 1-30)
1. **Explore systematically** - Visit rooms to gather information
2. **Update beliefs** - Each safe room reduces uncertainty
3. **Solve puzzles** - Open alternative routes early
4. **Collect nearby keys** - Start with easiest keys first
5. **Avoid guard** - Keep distance > 3 rooms if possible

### Mid Game (Turns 31-60)
1. **Optimize routes** - Use A* to find efficient paths
2. **Risk management** - Balance speed vs. safety
3. **Guard tracking** - Monitor guard patterns
4. **Key collection** - Focus on collecting remaining keys
5. **Health preservation** - Avoid high-risk rooms

### End Game (Turns 61-100)
1. **Plan final escape** - Know your route to exit
2. **Collect last key** - Make final key run
3. **Execute escape** - Move quickly to exit
4. **Guard evasion** - Time your moves to avoid guard
5. **Victory!** - Reach exit room

## ⚠️ Common Mistakes

### ❌ Don't Do This:
1. **Ignoring guard** - Guard gets smarter over time
2. **Random exploration** - Wastes turns and health
3. **Skipping belief checks** - Miss important risk information
4. **Rushing to exit** - Need all keys first
5. **Forgetting puzzles** - Locked doors block escape routes

### ✅ Do This Instead:
1. **Track guard constantly** - Check position regularly
2. **Plan ahead** - Use path finding before moving
3. **Use beliefs** - Check trap probabilities
4. **Collect keys systematically** - Plan optimal order
5. **Unlock doors early** - More options = better

## 🎯 Victory Conditions

You win when:
- ✅ All keys collected
- ✅ Reached exit room
- ✅ Still alive (health > 0)
- ✅ Not caught by guard

## 💀 Game Over Conditions

You lose if:
- ❌ Health reaches 0 (too many traps)
- ❌ Guard catches you (same room)
- ❌ Turn limit reached (100 turns)

## 📈 Performance Tracking

At game end, you'll see:
- Total turns taken
- Moves made
- Final health
- Keys collected
- Rooms explored
- Traps triggered
- Puzzles solved
- Guard performance

Try to beat your best score!

## 🎮 Difficulty Settings

Edit `config.py` to adjust difficulty:

### Easier Game:
```python
MAP_SIZE = "small"          # Fewer rooms
NUM_TRAPS = 2               # Fewer traps
GUARD_ENABLED = False       # No guard
MINIMAX_DEPTH = 1          # Dumber guard
AGENT_HEALTH = 150         # More health
```

### Harder Game:
```python
MAP_SIZE = "large"          # More rooms
NUM_TRAPS = 8              # More traps
GUARD_ENABLED = True       # Guard active
MINIMAX_DEPTH = 5          # Smarter guard
AGENT_HEALTH = 50          # Less health
MAX_TURNS = 50             # Time pressure
```

## 🔧 Customization

### Map Size
- **Small**: 6 rooms - Quick games (5-15 turns)
- **Medium**: 12 rooms - Standard games (20-40 turns)
- **Large**: 24 rooms - Long games (40-80 turns)

### Search Algorithm
- **BFS**: Finds shortest path (simple)
- **A***: Optimal path with risk consideration (smart)

### Puzzle Difficulty
- **Easy**: 2 variables, simple constraints
- **Medium**: 3 variables, multiple constraints
- **Hard**: 4 variables, complex constraints
- **Progressive**: Starts easy, gets harder (recommended)

## 🆘 Troubleshooting

### "No path found"
- Some doors are locked
- Solve puzzles to unlock doors
- Collect keys to progress

### "Can't move to that room"
- Door is locked
- Room not adjacent
- Solve puzzle first

### Guard always catches me
- Increase `MINIMAX_DEPTH` for smarter guard
- Or decrease it for easier guard
- Check guard position more often
- Use belief state to predict safe routes

### Too many traps
- Reduce `NUM_TRAPS` in config
- Increase `AGENT_HEALTH`
- Use belief state more carefully
- Check probabilities before moving

## 🎓 Learning Tips

### Understanding Search:
- Watch how BFS explores all paths equally
- See how A* uses heuristics to be smarter
- Notice nodes expanded vs. path length

### Understanding CSP:
- Observe backtracking when constraints fail
- See how variables are assigned
- Notice how constraints reduce search space

### Understanding Minimax:
- Guard tries to minimize distance to you
- It assumes you'll move optimally
- Depth determines how far ahead it thinks

### Understanding Bayesian:
- Probabilities update with evidence
- Safe rooms reduce trap probability
- Traps increase nearby room probabilities
- Spatial correlation matters

## 🏁 Ready to Play!

Now you know everything to master the AI Escape Room!

**Remember:**
- Think ahead (like A*)
- Update your beliefs (like Bayesian reasoning)
- Solve puzzles (like CSP solver)
- Outsmart the guard (better than Minimax!)

**Good luck and have fun! 🎮**

---

For technical details, see `README.md` and `PROJECT_OVERVIEW.md`
