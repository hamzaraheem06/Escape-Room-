"""
Quick Demo: AI Solver vs Human Player
Shows how the AI automatically solves the escape room
"""

from ai_solver import AISolver
import time


def demo_ai_solver():
    """Demonstrate the AI solver capabilities"""
    
    print("🤖 AI ESCAPE ROOM SOLVER DEMO")
    print("="*60)
    print("This demo shows how the AI automatically solves the escape room")
    print("using all the advanced algorithms we've implemented:")
    print("• A* Search with trap-aware heuristics")
    print("• Bayesian reasoning for trap prediction")
    print("• Automated CSP puzzle solving")
    print("• Strategic pathfinding and risk assessment")
    print("• Minimax-based guard evasion")
    print("="*60)
    
    input("\nPress Enter to start the AI solver...")
    
    # Run the solver
    success = run_ai_with_summary()
    
    return success


def run_ai_with_summary():
    """Run AI solver with smart verbosity"""
    
    print("\n🎯 Starting AI Solver...")
    print("The AI will automatically:")
    print("  1. Use Bayesian reasoning to avoid dangerous rooms")
    print("  2. Find optimal paths using A* search")
    print("  3. Solve CSP puzzles automatically")
    print("  4. Make strategic decisions about movement")
    print("  5. Evade the guard using Minimax predictions")
    print()
    
    # Create solver with moderate verbosity
    solver = AISolver(verbose=True)
    original_log = solver.log
    
    def smart_log(message: str):
        # Show key decisions and events
        if any(keyword in message for keyword in [
            "🎯 Target:", "🧩 Solving puzzle", "✅ Puzzle solved", 
            "🏆 VICTORY", "💀 Agent died", "⏰ Maximum turns",
            "No path found", "Guard nearby"
        ]):
            original_log(message)
        elif "Turn" in message and any(keyword in message for keyword in [
            "Moved to Room", "Found KEY", "TRAP TRIGGERED"
        ]):
            original_log(message)
    
    solver.log = smart_log
    
    success = solver.solve_escape_room()
    
    return success


def compare_strategies():
    """Compare different AI strategies"""
    
    print("\n📊 STRATEGY COMPARISON")
    print("="*40)
    
    strategies = [
        ("Conservative (Low Risk)", {"risk_tolerance": 0.1, "use_astar": True}),
        ("Balanced (Medium Risk)", {"risk_tolerance": 0.3, "use_astar": True}),
        ("Aggressive (High Risk)", {"risk_tolerance": 0.7, "use_astar": True}),
        ("Fast BFS (No Heuristic)", {"risk_tolerance": 0.3, "use_astar": False}),
    ]
    
    results = []
    
    for name, params in strategies:
        print(f"\n🔄 Testing: {name}")
        print("-" * 30)
        
        # Create new solver with specific parameters
        solver = AISolver(verbose=False)
        solver.risk_tolerance = params["risk_tolerance"]
        solver.use_astar = params["use_astar"]
        
        start_time = time.time()
        success = solver.solve_escape_room()
        elapsed = time.time() - start_time
        
        results.append({
            "strategy": name,
            "success": success,
            "turns": solver.turn,
            "health": solver.agent.health,
            "keys": len(solver.agent.keys_collected),
            "time": elapsed
        })
        
        print(f"Result: {'✅ Success' if success else '❌ Failed'}")
        print(f"Turns: {solver.turn}, Health: {solver.agent.health}, Keys: {len(solver.agent.keys_collected)}")
        print(f"Time: {elapsed:.2f}s")
    
    # Summary
    print(f"\n{'='*60}")
    print("STRATEGY COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"{'Strategy':<25} {'Success':<8} {'Turns':<8} {'Health':<8} {'Keys':<6} {'Time':<8}")
    print("-" * 60)
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{result['strategy']:<25} {status:<8} {result['turns']:<8} "
              f"{result['health']:<8} {result['keys']:<6} {result['time']:<8.2f}s")
    
    return results


if __name__ == "__main__":
    print("🎮 Choose demo mode:")
    print("1. Single AI solver demo")
    print("2. Strategy comparison (4 different approaches)")
    print("3. Quick test (silent mode)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        demo_ai_solver()
    elif choice == "2":
        compare_strategies()
    elif choice == "3":
        print("\n🏃 Running quick test...")
        solver = AISolver(verbose=False)
        success = solver.solve_escape_room()
        print(f"\nQuick test result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    else:
        print("Invalid choice. Running demo...")
        demo_ai_solver()