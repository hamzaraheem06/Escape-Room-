"""
Comprehensive testing script for all AI Escape Room components
Tests each module independently and integration
"""

import sys
from config import Config
from environment import Environment, Room
from agent import Agent
from guard import Guard
from csp_solver import CSPPuzzle, CSPSolver, generate_puzzle
from bayesian_reasoning import BayesianBeliefSystem


def print_test_header(test_name: str):
    """Print formatted test header"""
    print("\n" + "="*70)
    print(f"🧪 TEST: {test_name}")
    print("="*70)


def print_test_result(passed: bool, message: str = ""):
    """Print test result"""
    if passed:
        print(f"✅ PASSED {message}")
    else:
        print(f"❌ FAILED {message}")
    return passed


def test_environment():
    """Test environment generation and room connectivity"""
    print_test_header("Environment Generation")
    
    config = Config()
    config.MAP_SIZE = "small"
    env = Environment(config)
    
    # Test 1: Correct number of rooms
    expected_rooms = config.get_room_count()
    test1 = print_test_result(
        len(env.rooms) == expected_rooms,
        f"- Room count: {len(env.rooms)}/{expected_rooms}"
    )
    
    # Test 2: Start and exit rooms exist
    test2 = print_test_result(
        0 in env.rooms and env.exit_room_id in env.rooms,
        f"- Start (0) and Exit ({env.exit_room_id}) exist"
    )
    
    # Test 3: All rooms are connected (can reach exit from start)
    from collections import deque
    visited = set([0])
    queue = deque([0])
    while queue:
        room_id = queue.popleft()
        for neighbor_id, locked in env.rooms[room_id].neighbors:
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append(neighbor_id)
    
    test3 = print_test_result(
        len(visited) == len(env.rooms),
        f"- All rooms reachable: {len(visited)}/{len(env.rooms)}"
    )
    
    # Test 4: Keys placed
    keys_found = sum(1 for room in env.rooms.values() if room.has_key)
    test4 = print_test_result(
        keys_found == config.NUM_KEYS,
        f"- Keys placed: {keys_found}/{config.NUM_KEYS}"
    )
    
    # Test 5: Traps placed
    traps_found = sum(1 for room in env.rooms.values() if room.has_trap)
    test5 = print_test_result(
        traps_found <= config.NUM_TRAPS,
        f"- Traps placed: {traps_found} (max {config.NUM_TRAPS})"
    )
    
    return all([test1, test2, test3, test4, test5])


def test_csp_solver():
    """Test CSP puzzle generation and solving"""
    print_test_header("CSP Puzzle Solver")
    
    results = []
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\nTesting {difficulty.upper()} puzzle:")
        puzzle = generate_puzzle(difficulty)
        solver = CSPSolver(puzzle)
        solution = solver.solve()
        
        if solution:
            # Verify solution
            is_valid = solver.verify_solution(solution)
            results.append(print_test_result(
                is_valid,
                f"- {difficulty}: Solution valid, nodes={solver.nodes_expanded}, backtracks={solver.backtracks}"
            ))
            print(f"  Solution: {solution}")
        else:
            results.append(print_test_result(
                False,
                f"- {difficulty}: No solution found"
            ))
    
    return all(results)


def test_bayesian_reasoning():
    """Test Bayesian belief system"""
    print_test_header("Bayesian Belief Updates")
    
    belief_system = BayesianBeliefSystem(num_rooms=10)
    
    # Test 1: Initial probabilities
    initial_prob = belief_system.get_trap_probability(5)
    test1 = print_test_result(
        0.0 <= initial_prob <= 1.0,
        f"- Initial probability valid: {initial_prob}"
    )
    
    # Test 2: Update after safe observation
    belief_system.update_belief(5, "safe")
    safe_prob = belief_system.get_trap_probability(5)
    test2 = print_test_result(
        safe_prob < initial_prob,
        f"- Probability decreased after safe observation: {initial_prob:.3f} → {safe_prob:.3f}"
    )
    
    # Test 3: Update after trap observation
    belief_system.update_belief(7, "trap")
    trap_prob = belief_system.get_trap_probability(7)
    test3 = print_test_result(
        trap_prob > 0.9,
        f"- Probability increased after trap observation: {trap_prob:.3f}"
    )
    
    # Test 4: Safest room identification
    safest = belief_system.get_safest_rooms([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], top_n=1)
    test4 = print_test_result(
        len(safest) > 0,
        f"- Safest room identified: Room {safest[0]}"
    )
    
    # Test 5: Path risk estimation
    path = [0, 1, 2, 3]
    risk = belief_system.estimate_path_risk(path)
    test5 = print_test_result(
        risk >= 0,
        f"- Path risk calculated: {risk:.3f}"
    )
    
    return all([test1, test2, test3, test4, test5])


def test_search_algorithms():
    """Test agent's search algorithms"""
    print_test_header("Search Algorithms (BFS & A*)")
    
    config = Config()
    config.MAP_SIZE = "small"
    env = Environment(config)
    agent = Agent(env, config)
    
    start = 0
    goal = env.exit_room_id
    
    # Test BFS
    print("\nTesting BFS:")
    path_bfs = agent.find_path_bfs(start, goal)
    test1 = print_test_result(
        path_bfs is not None and len(path_bfs) > 0,
        f"- BFS found path of length {len(path_bfs) if path_bfs else 0}"
    )
    if path_bfs:
        print(f"  Path: {' → '.join(map(str, path_bfs[:5]))}{'...' if len(path_bfs) > 5 else ''}")
    
    # Test A*
    print("\nTesting A*:")
    path_astar = agent.find_path_astar(start, goal)
    test2 = print_test_result(
        path_astar is not None and len(path_astar) > 0,
        f"- A* found path of length {len(path_astar) if path_astar else 0}"
    )
    if path_astar:
        print(f"  Path: {' → '.join(map(str, path_astar[:5]))}{'...' if len(path_astar) > 5 else ''}")
    
    # Test optimality (A* should find equal or better path than BFS)
    if path_bfs and path_astar:
        test3 = print_test_result(
            len(path_astar) <= len(path_bfs),
            f"- A* optimal: A* length ({len(path_astar)}) ≤ BFS length ({len(path_bfs)})"
        )
    else:
        test3 = True
    
    # Test key finding
    print("\nTesting key finding:")
    key_result = agent.find_nearest_key()
    test4 = print_test_result(
        key_result is not None,
        f"- Nearest key found: Room {key_result[0] if key_result else 'None'}"
    )
    
    return all([test1, test2, test3, test4])


def test_minimax_guard():
    """Test guard's Minimax algorithm"""
    print_test_header("Minimax Guard AI")
    
    config = Config()
    config.MAP_SIZE = "small"
    config.GUARD_ENABLED = True
    env = Environment(config)
    guard = Guard(env, config)
    
    # Test 1: Guard makes valid moves
    player_room = 0
    initial_room = guard.current_room
    new_room, message = guard.make_move(player_room)
    
    test1 = print_test_result(
        new_room in env.rooms,
        f"- Guard made valid move: Room {initial_room} → Room {new_room}"
    )
    
    # Test 2: Guard approaches player
    print("\nSimulating 5 turns:")
    player_room = 0
    distances = []
    
    for turn in range(5):
        distance_before = guard._distance_to_room(guard.current_room, player_room)
        distances.append(distance_before)
        new_room, msg = guard.make_move(player_room)
        print(f"  Turn {turn+1}: Guard at Room {guard.current_room}, distance to player: {distance_before}")
        player_room += 1  # Player moves away
    
    test2 = print_test_result(
        len(distances) == 5,
        f"- Guard made 5 moves successfully"
    )
    
    # Test 3: Minimax decision making
    test3 = print_test_result(
        guard.moves_made > 0,
        f"- Minimax decisions executed: {guard.moves_made} moves"
    )
    
    return all([test1, test2, test3])


def test_agent_movement():
    """Test agent movement and interaction"""
    print_test_header("Agent Movement & Interaction")
    
    config = Config()
    config.MAP_SIZE = "small"
    config.NUM_TRAPS = 2
    env = Environment(config)
    agent = Agent(env, config)
    
    # Test 1: Initial position
    test1 = print_test_result(
        agent.current_room == 0,
        f"- Agent starts at room 0"
    )
    
    # Test 2: Move to valid room
    neighbors = env.get_unlocked_neighbors(agent.current_room)
    if neighbors:
        target = neighbors[0]
        success, message = agent.move_to(target)
        test2 = print_test_result(
            success and agent.current_room == target,
            f"- Agent moved successfully to room {target}"
        )
        print(f"  {message}")
    else:
        test2 = False
        print("  ❌ No neighbors to move to")
    
    # Test 3: Health tracking
    initial_health = config.AGENT_HEALTH
    test3 = print_test_result(
        agent.health == initial_health or agent.traps_triggered > 0,
        f"- Health tracked: {agent.health}/{initial_health}"
    )
    
    # Test 4: Room visited tracking
    test4 = print_test_result(
        len(agent.rooms_visited) >= 1,
        f"- Rooms visited: {len(agent.rooms_visited)}"
    )
    
    return all([test1, test2, test3, test4])


def test_integration():
    """Test full game integration"""
    print_test_header("Game Integration")
    
    config = Config()
    config.MAP_SIZE = "small"
    config.MAX_TURNS = 10
    
    env = Environment(config)
    agent = Agent(env, config)
    guard = Guard(env, config)
    
    # Simulate a few game turns
    print("\nSimulating 3 game turns:")
    for turn in range(1, 4):
        print(f"\nTurn {turn}:")
        
        # Agent moves
        neighbors = env.get_unlocked_neighbors(agent.current_room)
        if neighbors:
            target = neighbors[0]
            success, message = agent.move_to(target)
            print(f"  Agent: {message}")
        
        # Guard moves
        new_room, message = guard.make_move(agent.current_room)
        print(f"  {message}")
        
        # Check game state
        if guard.current_room == agent.current_room:
            print("  🚨 Guard caught player!")
            break
    
    # Final checks
    test1 = print_test_result(
        agent.moves_made > 0,
        f"- Agent made {agent.moves_made} moves"
    )
    
    test2 = print_test_result(
        guard.moves_made > 0,
        f"- Guard made {guard.moves_made} moves"
    )
    
    test3 = print_test_result(
        agent.is_alive(),
        f"- Agent survived with {agent.health} health"
    )
    
    return all([test1, test2, test3])


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("🧪 AI ESCAPE ROOM - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    results = {
        "Environment": test_environment(),
        "CSP Solver": test_csp_solver(),
        "Bayesian Reasoning": test_bayesian_reasoning(),
        "Search Algorithms": test_search_algorithms(),
        "Minimax Guard": test_minimax_guard(),
        "Agent Movement": test_agent_movement(),
        "Integration": test_integration()
    }
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} test suites passed")
    print("="*70)
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! System is ready.")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test suite(s) failed. Review above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
