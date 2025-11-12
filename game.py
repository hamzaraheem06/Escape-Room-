"""
Main game loop - AI Escape Room
Integrates all AI components: Search, CSP, Minimax, Bayesian Reasoning
"""

import random
from typing import Optional
from config import Config
from environment import Environment, Room
from agent import Agent
from guard import Guard
from csp_solver import CSPPuzzle, CSPSolver, generate_puzzle
from bayesian_reasoning import BayesianBeliefSystem


class EscapeRoomGame:
    """Main game controller"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.env = Environment(self.config)
        self.agent = Agent(self.env, self.config)
        self.guard = Guard(self.env, self.config)
        self.turn = 0
        self.game_over = False
        self.victory = False
        
        # Track puzzle difficulty progression
        self.puzzles_encountered = 0
        
    def start(self):
        """Start the game"""
        print("\n" + "="*70)
        print("🎮 WELCOME TO AI ESCAPE ROOM 🎮")
        print("="*70)
        print("\n📖 STORY:")
        print("You are trapped in a mysterious escape room complex.")
        print("Navigate through locked rooms, solve puzzles, avoid traps,")
        print("and escape before the guard catches you!")
        print("\n🎯 OBJECTIVE:")
        print(f"- Collect all {self.env.total_keys} keys")
        print(f"- Reach Room {self.env.exit_room_id} (Exit)")
        print("- Survive! (Don't let health reach 0)")
        print("- Avoid the guard!")
        print("\n🤖 AI TECHNIQUES USED:")
        print("- Search Algorithms (BFS/A*) for pathfinding")
        print("- CSP Solver for puzzle solving")
        print("- Minimax for adversarial guard AI")
        print("- Bayesian Reasoning for trap prediction")
        print("="*70)
        
        print(self.env.get_map_summary())
        print("\n🎲 Environment Generated:")
        print(f"   Total Rooms: {self.env.room_count}")
        print(f"   Hidden Traps: {self.config.NUM_TRAPS}")
        print(f"   Keys to Find: {self.config.NUM_KEYS}")
        print(f"   Guard: {'Enabled' if self.config.GUARD_ENABLED else 'Disabled'}")
        
        input("\n\nPress ENTER to begin your escape...")
        self.game_loop()
        
    def game_loop(self):
        """Main game loop"""
        while not self.game_over and self.turn < self.config.MAX_TURNS:
            self.turn += 1
            print(f"\n{'='*70}")
            print(f"TURN {self.turn}")
            print(f"{'='*70}")
            
            # Show agent status
            print(self.agent.get_status())
            
            # Agent's turn
            action = self.get_player_action()
            
            if action == "quit":
                print("\n👋 Thanks for playing!")
                self.game_over = True
                break
                
            self.execute_action(action)
            
            # Check win/loss conditions
            if self.check_game_end():
                break
                
            # Guard's turn (if enabled)
            if self.config.GUARD_ENABLED and not self.game_over:
                print("\n--- Guard's Turn ---")
                new_room, message = self.guard.make_move(self.agent.current_room)
                print(message)
                
                # Check if guard caught player
                if self.guard.player_caught:
                    self.game_over = True
                    self.victory = False
                    break
                    
        self.end_game()
        
    def get_player_action(self) -> str:
        """Get player's chosen action"""
        print("\n📋 AVAILABLE ACTIONS:")
        print("1. Move to adjacent room")
        print("2. Solve puzzle (if present)")
        print("3. Find path to nearest key")
        print("4. Plan escape route")
        print("5. View belief state (trap probabilities)")
        print("6. View guard status")
        print("7. Quit game")
        
        while True:
            choice = input("\nChoose action (1-7): ").strip()
            
            if choice in ["1", "2", "3", "4", "5", "6", "7"]:
                return choice
            elif choice.lower() == "quit":
                return "quit"
            else:
                print("Invalid choice. Please enter 1-7.")
                
    def execute_action(self, action: str):
        """Execute the chosen action"""
        if action == "1":
            self.action_move()
        elif action == "2":
            self.action_solve_puzzle()
        elif action == "3":
            self.action_find_key()
        elif action == "4":
            self.action_plan_escape()
        elif action == "5":
            self.action_view_beliefs()
        elif action == "6":
            self.action_view_guard()
            
    def action_move(self):
        """Action: Move to adjacent room"""
        neighbors = self.env.get_unlocked_neighbors(self.agent.current_room)
        
        if not neighbors:
            print("\n❌ No accessible rooms from here!")
            return
            
        print("\n🚪 Available rooms:")
        for i, room_id in enumerate(neighbors, 1):
            room = self.env.get_room(room_id)
            trap_prob = self.agent.belief_system.get_trap_probability(room_id)
            risk_level = "🔴HIGH" if trap_prob > 0.6 else "🟡MED" if trap_prob > 0.3 else "🟢LOW"
            visited = "✓" if room.visited else "NEW"
            print(f"  {i}. Room {room_id}: {room.name} - Risk: {risk_level} ({trap_prob:.2f}) [{visited}]")
            
        choice = input(f"\nChoose room (1-{len(neighbors)}) or 'back': ").strip()
        
        if choice.lower() == "back":
            return
            
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(neighbors):
                target_room = neighbors[idx]
                success, message = self.agent.move_to(target_room)
                print(f"\n{message}")
            else:
                print("Invalid choice!")
        except ValueError:
            print("Invalid input!")
            
    def action_solve_puzzle(self):
        """Action: Attempt to solve a puzzle"""
        current_room = self.env.get_room(self.agent.current_room)
        
        # Check if current room has locked doors
        locked_neighbors = [(nid, locked) for nid, locked in current_room.neighbors if locked]
        
        if not locked_neighbors:
            print("\n❌ No locked doors in this room!")
            return
            
        print(f"\n🧩 Found {len(locked_neighbors)} locked door(s)!")
        
        # Determine puzzle difficulty
        if self.config.PUZZLE_DIFFICULTY == "progressive":
            if self.puzzles_encountered == 0:
                difficulty = "easy"
            elif self.puzzles_encountered < 3:
                difficulty = "medium"
            else:
                difficulty = "hard"
        else:
            difficulty = self.config.PUZZLE_DIFFICULTY
            
        # Generate and display puzzle
        puzzle = generate_puzzle(difficulty)
        self.puzzles_encountered += 1
        
        print("\n" + "="*60)
        print(puzzle.description)
        print("="*60)
        
        # Solve puzzle automatically (demonstrating CSP solver)
        solver = CSPSolver(puzzle)
        solution = solver.solve()
        
        if solution:
            print(f"\n🤖 CSP Solver found solution: {solution}")
            print(f"   Nodes expanded: {solver.nodes_expanded}")
            print(f"   Backtracks: {solver.backtracks}")
            
            # Unlock doors
            for neighbor_id, locked in locked_neighbors:
                if locked:
                    self.env.unlock_door_between(self.agent.current_room, neighbor_id)
                    neighbor = self.env.get_room(neighbor_id)
                    print(f"   🔓 Unlocked door to Room {neighbor_id}: {neighbor.name}")
                    
            self.agent.puzzles_solved += 1
            print(f"\n✅ Puzzle solved! Doors unlocked.")
        else:
            print("\n❌ CSP Solver couldn't find solution (puzzle error)")
            
    def action_find_key(self):
        """Action: Find path to nearest key"""
        result = self.agent.find_nearest_key()
        
        if result is None:
            print("\n✅ All keys have been collected!")
            return
            
        key_room, path = result
        room = self.env.get_room(key_room)
        
        print(f"\n🔍 Nearest key found in Room {key_room}: {room.name}")
        print(f"📍 Path: {' → '.join(map(str, path))}")
        print(f"   Distance: {len(path) - 1} rooms")
        
        # Estimate risk
        risk = self.agent.belief_system.estimate_path_risk(path)
        print(f"   Estimated risk: {risk:.2f}")
        
    def action_plan_escape(self):
        """Action: Plan route to exit"""
        path = self.agent.plan_escape_route()
        
        if path is None:
            print("\n❌ No path to exit found!")
            print("   Hint: You may need to solve puzzles to unlock doors.")
            return
            
        print(f"\n🗺️ Escape route planned!")
        print(f"📍 Path: {' → '.join(map(str, path))}")
        print(f"   Distance: {len(path) - 1} rooms")
        
        # Estimate risk
        risk = self.agent.belief_system.estimate_path_risk(path)
        print(f"   Estimated risk: {risk:.2f}")
        
        # Show room details
        print("\n   Route details:")
        for i, room_id in enumerate(path):
            room = self.env.get_room(room_id)
            trap_prob = self.agent.belief_system.get_trap_probability(room_id)
            risk_label = "🔴" if trap_prob > 0.6 else "🟡" if trap_prob > 0.3 else "🟢"
            print(f"   {i+1}. Room {room_id}: {room.name} {risk_label}")
            
    def action_view_beliefs(self):
        """Action: View Bayesian belief state"""
        print(self.agent.belief_system.get_belief_summary())
        
    def action_view_guard(self):
        """Action: View guard status"""
        print(self.guard.get_status())
        
        if self.guard.can_see_player(self.agent.current_room):
            print("⚠️  ALERT: Guard can detect your location!")
        else:
            distance = self.guard._distance_to_room(self.guard.current_room, 
                                                     self.agent.current_room)
            print(f"✅ Guard is {distance} rooms away")
            
    def check_game_end(self) -> bool:
        """Check if game has ended"""
        # Check death
        if not self.agent.is_alive():
            print("\n💀 GAME OVER: Health reached 0!")
            self.game_over = True
            self.victory = False
            return True
            
        # Check victory
        if self.agent.has_won():
            print("\n🎉 VICTORY! You escaped!")
            self.game_over = True
            self.victory = True
            return True
            
        # Check guard caught player
        if self.guard.player_caught:
            print("\n👮 GAME OVER: Caught by the guard!")
            self.game_over = True
            self.victory = False
            return True
            
        # Check turn limit
        if self.turn >= self.config.MAX_TURNS:
            print(f"\n⏰ GAME OVER: Turn limit reached ({self.config.MAX_TURNS} turns)")
            self.game_over = True
            self.victory = False
            return True
            
        return False
        
    def end_game(self):
        """Display end game statistics"""
        print("\n" + "="*70)
        print("GAME OVER - FINAL STATISTICS")
        print("="*70)
        
        if self.victory:
            print("🏆 Result: VICTORY! You escaped successfully!")
        else:
            print("💀 Result: DEFEAT")
            
        print(f"\n📊 Agent Performance:")
        print(f"   Turns taken: {self.turn}")
        print(f"   Moves made: {self.agent.moves_made}")
        print(f"   Final health: {self.agent.health}/{self.config.AGENT_HEALTH}")
        print(f"   Keys collected: {len(self.agent.keys_collected)}/{self.env.total_keys}")
        print(f"   Rooms explored: {len(self.agent.rooms_visited)}/{self.env.room_count}")
        print(f"   Traps triggered: {self.agent.traps_triggered}")
        print(f"   Puzzles solved: {self.agent.puzzles_solved}")
        
        print(f"\n👮 Guard Performance:")
        print(f"   Moves made: {self.guard.moves_made}")
        print(f"   Final position: Room {self.guard.current_room}")
        
        print("="*70)


def main():
    """Main entry point"""
    # Setup configuration
    config = Config()
    
    # You can customize settings here
    # config.MAP_SIZE = "medium"  # small, medium, large
    # config.SEARCH_ALGORITHM = "astar"  # bfs, astar
    # config.GUARD_ENABLED = True
    # config.PUZZLE_DIFFICULTY = "progressive"  # easy, medium, hard, progressive
    
    # Create and start game
    game = EscapeRoomGame(config)
    game.start()


if __name__ == "__main__":
    main()
