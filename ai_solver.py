"""
Automated AI Solver for Escape Room Game
Uses all AI components: BFS/A*, CSP solving, Bayesian reasoning, Minimax evasion
"""

import time
from typing import List, Dict, Optional, Tuple
from config import Config
from environment import Environment, Room
from agent import Agent
from guard import Guard
from csp_solver import CSPPuzzle, CSPSolver, generate_puzzle
from bayesian_reasoning import BayesianBeliefSystem


class AISolver:
    """
    Automated AI that plays the escape room using intelligent algorithms
    """
    
    def __init__(self, config: Config = None, verbose: bool = True):
        self.config = config or Config()
        self.verbose = verbose
        self.env = Environment(self.config)
        self.agent = Agent(self.env, self.config)
        self.guard = Guard(self.env, self.config)
        
        # Game state tracking
        self.turn = 0
        self.max_turns = self.config.MAX_TURNS
        self.game_over = False
        self.victory = False
        
        # Strategy settings
        self.risk_tolerance = 0.3  # Maximum trap probability to consider room safe
        self.use_astar = True  # Use A* instead of BFS
        self.debug_mode = True
        
    def log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[Turn {self.turn:3d}] {message}")
    
    def get_safe_neighbors(self, room_id: int) -> List[int]:
        """Get neighboring rooms that are relatively safe"""
        neighbors = self.env.get_unlocked_neighbors(room_id)
        safe_neighbors = []
        
        for neighbor_id in neighbors:
            trap_prob = self.agent.belief_system.get_trap_probability(neighbor_id)
            if trap_prob < self.risk_tolerance:
                safe_neighbors.append(neighbor_id)
        
        return safe_neighbors
    
    def find_room_with_key(self, key_id: int) -> Optional[int]:
        """Find room ID that contains the specified key"""
        for room_id, room in self.env.rooms.items():
            if room.has_key and room.key_id == key_id:
                return room_id
        return None
    
    def find_priority_target(self) -> Optional[int]:
        """
        Determine the most important target to move toward
        Priority: Keys -> Exit -> Exploration
        """
        # Priority 1: Find nearest key
        for key_id in range(1, self.env.total_keys + 1):
            if key_id not in self.agent.keys_collected:
                key_room_id = self.find_room_with_key(key_id)
                if key_room_id is not None:
                    return key_room_id
        
        # Priority 2: Go to exit if all keys collected
        if len(self.agent.keys_collected) >= self.env.total_keys:
            return self.env.exit_room_id
        
        # Priority 3: Explore unknown safe rooms
        for room_id in range(self.env.room_count):
            if room_id not in self.agent.rooms_visited:
                trap_prob = self.agent.belief_system.get_trap_probability(room_id)
                if trap_prob < self.risk_tolerance:
                    return room_id
        
        return None
    
    def navigate_to_target(self, target_room_id: int) -> bool:
        """
        Navigate to target room using A* or BFS
        Returns True if successful, False if stuck
        """
        start_room = self.agent.current_room
        
        # Choose search algorithm
        if self.use_astar:
            path = self.agent.find_path_astar(start_room, target_room_id)
        else:
            path = self.agent.find_path_bfs(start_room, target_room_id)
        
        if not path:
            self.log(f"❌ No path found to Room {target_room_id}")
            return False
        
        # Follow the path (skip first room as it's current location)
        for i, room_id in enumerate(path[1:], 1):
            if self.game_over:
                break
                
            self.log(f"  → Moving to Room {room_id} (step {i}/{len(path)-1})")
            
            # Check if guard is nearby (avoid if possible)
            guard_distance = abs(self.guard.current_room - room_id)
            if guard_distance <= 2:
                self.log(f"  ⚠️  Guard nearby! Distance: {guard_distance}")
            
            # Execute the move
            success, message = self.agent.move_to(room_id)
            if not success:
                self.log(f"❌ Move failed: {message}")
                return False
            
            self.log(f"  ✅ {message}")
            
            # Update guard position
            guard_room, guard_message = self.guard.make_move(self.agent.current_room)
            self.log(f"  🤖 Guard moved to Room {guard_room}: {guard_message}")
            
            self.turn += 1
            if self.turn >= self.max_turns:
                self.log("⏰ Maximum turns reached!")
                self.game_over = True
                return False
            
            # Check win/lose conditions
            if self.check_victory():
                return True
            
            if self.agent.health <= 0:
                self.log("💀 Agent died!")
                self.game_over = True
                return False
        
        return True
    
    def solve_puzzle(self, room_id: int) -> bool:
        """
        Solve CSP puzzle in current room automatically
        """
        room = self.env.get_room(room_id)
        
        if not room.has_puzzle or not room.puzzle:
            return True  # No puzzle to solve
        
        self.log(f"🧩 Solving puzzle in {room.name}...")
        
        # Generate or use existing puzzle
        puzzle = CSPPuzzle()
        solver = CSPSolver()
        
        puzzle_data = room.puzzle
        difficulty = getattr(puzzle_data, 'difficulty', 'medium')
        
        if self.debug_mode:
            print(f"    Difficulty: {difficulty}")
            if hasattr(puzzle_data, 'variables'):
                print(f"    Variables: {list(puzzle_data.variables.keys())}")
        
        # Solve the puzzle
        start_time = time.time()
        solution = solver.solve(puzzle_data)
        solve_time = time.time() - start_time
        
        if solution:
            self.log(f"  ✅ Puzzle solved in {solve_time:.3f}s!")
            self.agent.puzzles_solved += 1
            
            # Mark puzzle as solved and unlock connections
            room.puzzle_solved = True
            
            # Unlock all doors from this room
            for neighbor_id, is_locked in room.neighbors:
                if is_locked:
                    self.env.unlock_door_between(room_id, neighbor_id)
            
            self.log(f"  🔓 Doors unlocked!")
            return True
        else:
            self.log(f"  ❌ Failed to solve puzzle (took {solve_time:.3f}s)")
            return False
    
    def check_victory(self) -> bool:
        """Check if game is won or lost"""
        # Victory condition: All keys collected and reached exit
        if (len(self.agent.keys_collected) >= self.env.total_keys and 
            self.agent.current_room == self.env.exit_room_id):
            self.victory = True
            self.game_over = True
            self.log("🏆 VICTORY! Escape successful!")
            return True
        
        # Loss conditions
        if self.agent.health <= 0:
            self.game_over = True
            return True
        
        return False
    
    def display_game_state(self):
        """Display current game state"""
        if not self.verbose:
            return
            
        print(f"\n{'='*50}")
        print(f"GAME STATE - Turn {self.turn}")
        print(f"{'='*50}")
        print(f"Agent Position: Room {self.agent.current_room} ({self.env.get_room(self.agent.current_room).name})")
        print(f"Guard Position: Room {self.guard.current_room}")
        print(f"Health: {self.agent.health}/{self.config.AGENT_HEALTH}")
        print(f"Keys Collected: {len(self.agent.keys_collected)}/{self.env.total_keys}")
        print(f"Keys: {sorted(self.agent.keys_collected)}")
        print(f"Rooms Visited: {len(self.agent.rooms_visited)}")
        print(f"Puzzles Solved: {self.agent.puzzles_solved}")
        print(f"Moves Made: {self.agent.moves_made}")
        
        # Show trap probabilities for nearby rooms
        print("\nTrap Probabilities (current area):")
        current_room = self.agent.current_room
        for room_id in range(max(0, current_room-2), min(self.env.room_count, current_room+3)):
            if room_id == current_room:
                print(f"  Room {room_id}: {self.agent.belief_system.get_trap_probability(room_id):.3f} (CURRENT)")
            else:
                print(f"  Room {room_id}: {self.agent.belief_system.get_trap_probability(room_id):.3f}")
        print(f"{'='*50}\n")
    
    def solve_escape_room(self) -> bool:
        """
        Main AI solving loop
        Returns True if escape successful, False otherwise
        """
        print("\n🤖 AI ESCAPE ROOM SOLVER")
        print("="*60)
        
        # Initial game state
        self.log("🚀 Starting automated escape room solution...")
        self.display_game_state()
        
        # Main solving loop
        while not self.game_over:
            # Check if we need to solve a puzzle first
            current_room = self.agent.current_room
            room = self.env.get_room(current_room)
            
            if room.has_puzzle and room.puzzle and not room.puzzle_solved:
                if not self.solve_puzzle(current_room):
                    break
            
            # Find next target
            target = self.find_priority_target()
            
            if target is None:
                self.log("🎯 No valid targets found. Exploring...")
                # Find any unvisited room
                for room_id in range(self.env.room_count):
                    if room_id not in self.agent.rooms_visited:
                        target = room_id
                        break
                
                if target is None:
                    self.log("🏁 No more rooms to explore. Finished!")
                    break
            
            self.log(f"🎯 Target: Room {target} ({self.env.get_room(target).name})")
            
            # Navigate to target
            success = self.navigate_to_target(target)
            
            if not success:
                break
            
            # Show periodic status updates
            if self.turn % 10 == 0:
                self.display_game_state()
            
            # Small delay for readability
            if self.verbose:
                time.sleep(0.1)
        
        # Final results
        print(f"\n{'='*60}")
        print("FINAL RESULTS")
        print(f"{'='*60}")
        print(f"Success: {'✅ YES' if self.victory else '❌ NO'}")
        print(f"Turns Used: {self.turn}/{self.max_turns}")
        print(f"Health Remaining: {self.agent.health}/{self.config.AGENT_HEALTH}")
        print(f"Keys Collected: {len(self.agent.keys_collected)}/{self.env.total_keys}")
        print(f"Puzzles Solved: {self.agent.puzzles_solved}")
        print(f"Total Moves: {self.agent.moves_made}")
        print(f"Rooms Explored: {len(self.agent.rooms_visited)}")
        print(f"Traps Triggered: {self.agent.traps_triggered}")
        
        if self.victory:
            print("\n🎉 CONGRATULATIONS! The AI successfully escaped!")
        else:
            print("\n😔 The AI failed to escape this time.")
        
        print(f"{'='*60}")
        
        return self.victory


def run_ai_solver(turns_to_show: int = 20):
    """
    Run the AI solver with configurable verbosity
    
    Args:
        turns_to_show: Number of turns to show in detail (0 for silent, -1 for all)
    """
    if turns_to_show == 0:
        # Silent mode
        solver = AISolver(verbose=False)
        return solver.solve_escape_room()
    elif turns_to_show < 0:
        # Full verbose mode
        solver = AISolver(verbose=True)
        return solver.solve_escape_room()
    else:
        # Semi-verbose mode (show every N turns)
        solver = AISolver(verbose=True)
        original_log = solver.log
        
        def selective_log(message: str):
            if "Turn" in message:
                turn_num = int(message.split("Turn")[1].split("]")[0].strip())
                if turn_num % turns_to_show == 0 or "🎯" in message or "🏆" in message or "💀" in message:
                    original_log(message)
            else:
                original_log(message)
        
        solver.log = selective_log
        return solver.solve_escape_room()


if __name__ == "__main__":
    print("🎮 AI Escape Room Solver")
    print("Choose execution mode:")
    print("1. Silent mode (fast execution)")
    print("2. Detailed mode (show all turns)")
    print("3. Summary mode (show every 10 turns)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        run_ai_solver(0)
    elif choice == "2":
        run_ai_solver(-1)
    elif choice == "3":
        run_ai_solver(10)
    else:
        print("Invalid choice. Running summary mode...")
        run_ai_solver(10)