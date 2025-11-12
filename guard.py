"""
Guard AI with Minimax adversarial search
"""

from typing import List, Tuple, Optional
import random
from config import Config
from environment import Environment


class Guard:
    """Adversarial guard that uses Minimax to catch the player"""
    
    def __init__(self, environment: Environment, config: Config = None):
        self.config = config or Config()
        self.env = environment
        
        # Start guard in a random middle room (not start or exit)
        available_starts = list(range(2, environment.room_count - 2))
        self.current_room = random.choice(available_starts) if available_starts else 1
        
        self.moves_made = 0
        self.player_caught = False
        
    def can_see_player(self, player_room: int) -> bool:
        """Check if guard can see/detect the player"""
        distance = self._distance_to_room(self.current_room, player_room)
        return distance <= self.config.GUARD_VISION_RANGE
        
    def _distance_to_room(self, from_room: int, to_room: int) -> int:
        """
        Calculate approximate distance between rooms
        Using simple BFS distance
        """
        if from_room == to_room:
            return 0
            
        from collections import deque
        queue = deque([(from_room, 0)])
        visited = {from_room}
        
        while queue:
            current, dist = queue.popleft()
            
            for neighbor in self.env.get_unlocked_neighbors(current):
                if neighbor == to_room:
                    return dist + 1
                    
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
                    
        return 999  # No path found
        
    def make_move(self, player_room: int) -> Tuple[int, str]:
        """
        Make adversarial move using Minimax
        Returns: (new_room, message)
        """
        if not self.config.GUARD_ENABLED:
            return self.current_room, "Guard is disabled"
            
        # Use Minimax to decide best move
        best_move = self._minimax_decision(player_room)
        
        if best_move is not None:
            old_room = self.current_room
            self.current_room = best_move
            self.moves_made += 1
            
            # Check if caught player
            if self.current_room == player_room:
                self.player_caught = True
                return self.current_room, f"👮 GUARD moved from Room {old_room} to Room {best_move} and CAUGHT THE PLAYER!"
            else:
                distance = self._distance_to_room(self.current_room, player_room)
                return self.current_room, f"👮 Guard moved from Room {old_room} to Room {best_move} (distance to player: {distance})"
        else:
            return self.current_room, "Guard couldn't find a move"
            
    def _minimax_decision(self, player_room: int) -> Optional[int]:
        """
        Make decision using Minimax algorithm
        Guard maximizes (wants to catch player - minimize distance)
        Player minimizes (wants to escape - maximize distance)
        """
        neighbors = self.env.get_unlocked_neighbors(self.current_room)
        
        if not neighbors:
            return None
            
        # Evaluate each possible move
        best_move = None
        best_value = float('-inf')
        
        for neighbor in neighbors:
            # Simulate moving to this room
            value = self._minimax(neighbor, player_room, self.config.MINIMAX_DEPTH - 1, False)
            
            if value > best_value:
                best_value = value
                best_move = neighbor
                
        return best_move
        
    def _minimax(self, guard_room: int, player_room: int, depth: int, is_maximizing: bool) -> float:
        """
        Minimax algorithm with depth-limited search
        
        Args:
            guard_room: Current guard position in simulation
            player_room: Current player position
            depth: Remaining search depth
            is_maximizing: True if guard's turn, False if player's turn
            
        Returns:
            Utility value (higher = better for guard)
        """
        # Terminal conditions
        if depth == 0 or guard_room == player_room:
            return self._evaluate_position(guard_room, player_room)
            
        if is_maximizing:
            # Guard's turn - maximize
            max_value = float('-inf')
            neighbors = self.env.get_unlocked_neighbors(guard_room)
            
            if not neighbors:
                return self._evaluate_position(guard_room, player_room)
                
            for neighbor in neighbors:
                value = self._minimax(neighbor, player_room, depth - 1, False)
                max_value = max(max_value, value)
                
            return max_value
        else:
            # Player's turn - minimize (from guard's perspective)
            min_value = float('inf')
            neighbors = self.env.get_unlocked_neighbors(player_room)
            
            if not neighbors:
                return self._evaluate_position(guard_room, player_room)
                
            for neighbor in neighbors:
                value = self._minimax(guard_room, neighbor, depth - 1, True)
                min_value = min(min_value, value)
                
            return min_value
            
    def _evaluate_position(self, guard_room: int, player_room: int) -> float:
        """
        Evaluate a position (utility function)
        Higher value = better for guard (closer to player)
        
        Returns value in range approximately [-100, 100]
        """
        if guard_room == player_room:
            return 100.0  # Guard caught player - maximum utility
            
        distance = self._distance_to_room(guard_room, player_room)
        
        if distance == 999:
            return -50.0  # No path to player
            
        # Inverse of distance (closer = better for guard)
        # Scale to reasonable range
        utility = 50.0 / (distance + 1)
        
        return utility
        
    def get_status(self) -> str:
        """Get guard status"""
        room = self.env.get_room(self.current_room)
        status = ["\n" + "="*60]
        status.append("GUARD STATUS")
        status.append("="*60)
        status.append(f"Location: {room.name} (Room {self.current_room})")
        status.append(f"Moves made: {self.moves_made}")
        status.append(f"Using: Minimax Algorithm (depth {self.config.MINIMAX_DEPTH})")
        status.append("="*60 + "\n")
        return '\n'.join(status)


class MinimaxAlphaBeta:
    """
    Extended Minimax with Alpha-Beta pruning for better performance
    This is a static utility class
    """
    
    @staticmethod
    def minimax_alpha_beta(guard, guard_room: int, player_room: int, 
                           depth: int, alpha: float, beta: float, 
                           is_maximizing: bool) -> float:
        """
        Minimax with alpha-beta pruning
        
        Args:
            guard: Guard instance for accessing environment
            guard_room: Current guard position
            player_room: Current player position
            depth: Remaining depth
            alpha: Best value for maximizer
            beta: Best value for minimizer
            is_maximizing: True if guard's turn
            
        Returns:
            Utility value
        """
        # Terminal conditions
        if depth == 0 or guard_room == player_room:
            return guard._evaluate_position(guard_room, player_room)
            
        if is_maximizing:
            max_value = float('-inf')
            neighbors = guard.env.get_unlocked_neighbors(guard_room)
            
            for neighbor in neighbors:
                value = MinimaxAlphaBeta.minimax_alpha_beta(
                    guard, neighbor, player_room, depth - 1, alpha, beta, False
                )
                max_value = max(max_value, value)
                alpha = max(alpha, value)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
                    
            return max_value
        else:
            min_value = float('inf')
            neighbors = guard.env.get_unlocked_neighbors(player_room)
            
            for neighbor in neighbors:
                value = MinimaxAlphaBeta.minimax_alpha_beta(
                    guard, guard_room, neighbor, depth - 1, alpha, beta, True
                )
                min_value = min(min_value, value)
                beta = min(beta, value)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
                    
            return min_value


if __name__ == "__main__":
    # Test guard AI
    from environment import Environment
    from config import Config
    
    print("Testing Guard AI with Minimax\n")
    
    config = Config()
    config.MAP_SIZE = "small"
    config.GUARD_ENABLED = True
    
    env = Environment(config)
    guard = Guard(env, config)
    
    print(guard.get_status())
    
    # Simulate some moves
    player_room = 0
    for turn in range(5):
        print(f"\nTurn {turn + 1}:")
        print(f"Player in Room {player_room}")
        new_room, message = guard.make_move(player_room)
        print(message)
        
        # Simulate player moving
        player_room += 1
