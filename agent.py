"""
Agent with search algorithms for pathfinding and planning
"""

from typing import List, Dict, Optional, Tuple, Set
from collections import deque
import heapq
from config import Config
from environment import Environment
from bayesian_reasoning import BayesianBeliefSystem


class Agent:
    """Player agent with AI search capabilities"""
    
    def __init__(self, environment: Environment, config: Config = None):
        self.config = config or Config()
        self.env = environment
        self.current_room = environment.start_room_id
        self.health = self.config.AGENT_HEALTH
        self.keys_collected = set()
        self.rooms_visited = set([self.current_room])
        self.belief_system = BayesianBeliefSystem(
            num_rooms=environment.room_count,
            config=config
        )
        
        # Stats
        self.moves_made = 0
        self.traps_triggered = 0
        self.puzzles_solved = 0
        
    def move_to(self, room_id: int) -> Tuple[bool, str]:
        """
        Move to a room and handle consequences
        Returns: (success, message)
        """
        if room_id not in self.env.get_unlocked_neighbors(self.current_room):
            return False, "Cannot move to that room (locked or not connected)"
            
        self.current_room = room_id
        self.moves_made += 1
        self.rooms_visited.add(room_id)
        
        room = self.env.get_room(room_id)
        room.visited = True
        messages = [f"Moved to {room.name} (Room {room_id})"]
        
        # Check for traps
        if self.env.trigger_trap(room_id):
            self.health -= self.config.TRAP_DAMAGE
            self.traps_triggered += 1
            self.belief_system.update_belief(room_id, "trap")
            messages.append(f"⚠ TRAP TRIGGERED! Lost {self.config.TRAP_DAMAGE} health. Health: {self.health}")
        else:
            # Room is safe
            self.belief_system.update_belief(room_id, "safe")
            
        # Check for keys
        if self.env.collect_key(room_id):
            key_id = room.key_id
            self.keys_collected.add(key_id)
            messages.append(f"🔑 Found KEY #{key_id}! Total keys: {len(self.keys_collected)}/{self.env.total_keys}")
            
        return True, " | ".join(messages)
        
    def find_path_bfs(self, start: int, goal: int) -> Optional[List[int]]:
        """
        Find shortest path using Breadth-First Search
        Returns path as list of room IDs, or None if no path exists
        """
        if start == goal:
            return [start]
            
        queue = deque([(start, [start])])
        visited = {start}
        nodes_expanded = 0
        
        while queue:
            current, path = queue.popleft()
            nodes_expanded += 1
            
            # Get unlocked neighbors
            for neighbor in self.env.get_unlocked_neighbors(current):
                if neighbor == goal:
                    final_path = path + [neighbor]
                    if self.config.VERBOSE:
                        print(f"  [BFS] Path found! Length: {len(final_path)}, Nodes expanded: {nodes_expanded}")
                    return final_path
                    
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
                    
        return None  # No path found
        
    def find_path_astar(self, start: int, goal: int) -> Optional[List[int]]:
        """
        Find optimal path using A* search with heuristic
        Heuristic: distance to goal + trap risk
        """
        if start == goal:
            return [start]
            
        def heuristic(room_id: int) -> float:
            """Estimate cost to goal: distance + trap risk"""
            distance = abs(room_id - goal)
            trap_risk = self.belief_system.get_trap_probability(room_id) * 10
            return distance + trap_risk
            
        # Priority queue: (f_score, room_id, path)
        open_set = [(heuristic(start), 0, start, [start])]
        visited = set()
        nodes_expanded = 0
        
        while open_set:
            f_score, g_score, current, path = heapq.heappop(open_set)
            nodes_expanded += 1
            
            if current in visited:
                continue
                
            visited.add(current)
            
            if current == goal:
                if self.config.VERBOSE:
                    print(f"  [A*] Path found! Length: {len(path)}, Cost: {g_score:.2f}, Nodes expanded: {nodes_expanded}")
                return path
                
            # Explore neighbors
            for neighbor in self.env.get_unlocked_neighbors(current):
                if neighbor not in visited:
                    new_g_score = g_score + 1
                    new_f_score = new_g_score + heuristic(neighbor)
                    heapq.heappush(open_set, 
                                  (new_f_score, new_g_score, neighbor, path + [neighbor]))
                    
        return None  # No path found
        
    def find_path(self, start: int, goal: int) -> Optional[List[int]]:
        """Find path using configured algorithm"""
        if self.config.SEARCH_ALGORITHM == "bfs":
            return self.find_path_bfs(start, goal)
        elif self.config.SEARCH_ALGORITHM == "astar":
            return self.find_path_astar(start, goal)
        else:
            return self.find_path_bfs(start, goal)
            
    def find_nearest_key(self) -> Optional[Tuple[int, List[int]]]:
        """
        Find the nearest uncollected key
        Returns: (room_id, path) or None
        """
        key_rooms = []
        for room_id, room in self.env.rooms.items():
            if room.has_key and room.key_id not in self.keys_collected:
                key_rooms.append(room_id)
                
        if not key_rooms:
            return None
            
        # Find shortest path to any key room
        best_path = None
        best_room = None
        
        for key_room in key_rooms:
            path = self.find_path(self.current_room, key_room)
            if path and (best_path is None or len(path) < len(best_path)):
                best_path = path
                best_room = key_room
                
        if best_path:
            return best_room, best_path
        return None
        
    def plan_escape_route(self) -> Optional[List[int]]:
        """
        Plan route to exit
        Returns path or None if exit not reachable
        """
        return self.find_path(self.current_room, self.env.exit_room_id)
        
    def get_status(self) -> str:
        """Get agent status summary"""
        room = self.env.get_room(self.current_room)
        status = ["\n" + "="*60]
        status.append("AGENT STATUS")
        status.append("="*60)
        status.append(f"Location: {room.name} (Room {self.current_room})")
        status.append(f"Health: {self.health}/{self.config.AGENT_HEALTH}")
        status.append(f"Keys: {len(self.keys_collected)}/{self.env.total_keys} collected")
        status.append(f"Moves: {self.moves_made}")
        status.append(f"Traps triggered: {self.traps_triggered}")
        status.append(f"Puzzles solved: {self.puzzles_solved}")
        status.append(f"Rooms visited: {len(self.rooms_visited)}/{self.env.room_count}")
        
        # Show available moves
        neighbors = self.env.get_unlocked_neighbors(self.current_room)
        status.append(f"\nAvailable moves: {len(neighbors)} rooms")
        for nid in neighbors:
            neighbor = self.env.get_room(nid)
            trap_prob = self.belief_system.get_trap_probability(nid)
            risk = "HIGH RISK" if trap_prob > 0.6 else "MEDIUM RISK" if trap_prob > 0.3 else "Low risk"
            visited = "✓" if neighbor.visited else "?"
            status.append(f"  → Room {nid}: {neighbor.name} [{risk}, P={trap_prob:.2f}] {visited}")
            
        status.append("="*60 + "\n")
        return '\n'.join(status)
        
    def is_alive(self) -> bool:
        """Check if agent is still alive"""
        return self.health > 0
        
    def has_won(self) -> bool:
        """Check if agent has escaped"""
        return self.current_room == self.env.exit_room_id


if __name__ == "__main__":
    # Test agent search capabilities
    from config import Config
    from environment import Environment
    
    print("Testing Agent Search Algorithms\n")
    
    config = Config()
    config.MAP_SIZE = "small"
    env = Environment(config)
    agent = Agent(env, config)
    
    print(env.get_map_summary())
    print(agent.get_status())
    
    # Test pathfinding
    print("\nTesting BFS pathfinding to exit:")
    path = agent.find_path_bfs(agent.current_room, env.exit_room_id)
    if path:
        print(f"Path: {' → '.join(map(str, path))}")
    else:
        print("No path found")
        
    print("\nTesting A* pathfinding to exit:")
    path = agent.find_path_astar(agent.current_room, env.exit_room_id)
    if path:
        print(f"Path: {' → '.join(map(str, path))}")
    else:
        print("No path found")
