"""
Quick Start Guide - AI Escape Room
Run this for a quick demonstration of the system
"""

from config import Config
from environment import Environment
from agent import Agent
from guard import Guard
from csp_solver import generate_puzzle, CSPSolver


def quick_demo():
    """Quick demonstration of all AI components"""
    
    print("\n" + "="*70)
    print("AI ESCAPE ROOM - QUICK DEMO")
    print("="*70)
    
    # 1. Environment Setup
    print("\n1️⃣  SETTING UP ENVIRONMENT")
    print("-" * 70)
    config = Config()
    config.MAP_SIZE = "small"  # Small map for quick demo
    config.VERBOSE = False
    
    env = Environment(config)
    print(f"✓ Created escape room with {env.room_count} rooms")
    print(f"✓ Placed {config.NUM_KEYS} keys and {config.NUM_TRAPS} traps")
    print(f"✓ Start: Room {env.start_room_id}, Exit: Room {env.exit_room_id}")
    
    # 2. Agent Creation
    print("\n2️⃣  CREATING AI AGENT")
    print("-" * 70)
    agent = Agent(env, config)
    print(f"✓ Agent initialized at {env.rooms[agent.current_room].name}")
    print(f"✓ Health: {agent.health}")
    print(f"✓ Search algorithm: {config.SEARCH_ALGORITHM.upper()}")
    
    # 3. Demonstrate Search Algorithms
    print("\n3️⃣  DEMONSTRATING SEARCH ALGORITHMS")
    print("-" * 70)
    
    # Find path to exit
    print("\n📍 Finding path to exit using A*...")
    path_to_exit = agent.find_path_astar(agent.current_room, env.exit_room_id)
    if path_to_exit:
        print(f"✓ Path found: {' → '.join(map(str, path_to_exit))}")
        print(f"  Distance: {len(path_to_exit) - 1} rooms")
    
    # Find nearest key
    print("\n🔑 Finding nearest key...")
    key_result = agent.find_nearest_key()
    if key_result:
        key_room, path = key_result
        print(f"✓ Nearest key in Room {key_room}")
        print(f"  Path: {' → '.join(map(str, path))}")
    
    # 4. Demonstrate CSP Solver
    print("\n4️⃣  DEMONSTRATING CSP PUZZLE SOLVER")
    print("-" * 70)
    
    for difficulty in ["easy", "medium", "hard"]:
        puzzle = generate_puzzle(difficulty)
        solver = CSPSolver(puzzle)
        solution = solver.solve()
        
        print(f"\n{difficulty.upper()} Puzzle:")
        print(f"  Variables: {puzzle.variables}")
        print(f"  Solution: {solution}")
        print(f"  Nodes expanded: {solver.nodes_expanded}, Backtracks: {solver.backtracks}")
    
    # 5. Demonstrate Bayesian Reasoning
    print("\n5️⃣  DEMONSTRATING BAYESIAN REASONING")
    print("-" * 70)
    
    print("\nInitial trap beliefs:")
    for room_id in range(min(5, env.room_count)):
        prob = agent.belief_system.get_trap_probability(room_id)
        print(f"  Room {room_id}: P(trap) = {prob:.3f}")
    
    # Simulate observations
    print("\n📊 Simulating observations...")
    agent.belief_system.update_belief(2, "safe")
    print(f"  After entering Room 2 safely:")
    print(f"    Room 2: P(trap) = {agent.belief_system.get_trap_probability(2):.3f}")
    
    agent.belief_system.update_belief(4, "trap")
    print(f"  After triggering trap in Room 4:")
    print(f"    Room 4: P(trap) = {agent.belief_system.get_trap_probability(4):.3f}")
    
    # 6. Demonstrate Minimax Guard
    print("\n6️⃣  DEMONSTRATING MINIMAX GUARD AI")
    print("-" * 70)
    
    guard = Guard(env, config)
    print(f"✓ Guard initialized at Room {guard.current_room}")
    print(f"✓ Using Minimax algorithm with depth {config.MINIMAX_DEPTH}")
    
    print("\nSimulating 3 guard moves:")
    player_pos = 0
    for turn in range(3):
        old_pos = guard.current_room
        distance_before = guard._distance_to_room(guard.current_room, player_pos)
        new_room, message = guard.make_move(player_pos)
        distance_after = guard._distance_to_room(new_room, player_pos)
        
        print(f"  Turn {turn + 1}:")
        print(f"    Guard: Room {old_pos} → Room {new_room}")
        print(f"    Distance to player: {distance_before} → {distance_after}")
        
        player_pos += 1  # Simulate player moving
    
    # 7. Summary
    print("\n7️⃣  DEMO COMPLETE")
    print("-" * 70)
    print("\n✅ Successfully demonstrated all AI components:")
    print("   • Search Algorithms (BFS, A*)")
    print("   • Constraint Satisfaction Problem Solving")
    print("   • Bayesian Belief Updates")
    print("   • Minimax Adversarial Search")
    
    print("\n🎮 To play the full game, run: python game.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    quick_demo()
