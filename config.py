"""
Configuration settings for AI Escape Room
"""

class Config:
    """Game configuration parameters"""
    
    # Map Settings
    MAP_SIZE = "medium"  # Options: "small" (5-8 rooms), "medium" (10-15 rooms), "large" (20-30 rooms)
    
    # Room counts by size
    ROOM_COUNTS = {
        "small": 6,
        "medium": 12,
        "large": 24
    }
    
    # Game Elements
    NUM_KEYS = 3  # Number of keys to collect
    NUM_TRAPS = 4  # Number of hidden traps
    TRAP_DAMAGE = 20  # Damage from trap
    
    # Puzzle Difficulty
    PUZZLE_DIFFICULTY = "progressive"  # Options: "easy", "medium", "hard", "progressive"
    
    # Guard AI
    GUARD_ENABLED = True
    MINIMAX_DEPTH = 3  # Look-ahead depth for guard
    GUARD_VISION_RANGE = 3  # Rooms within which guard can detect player
    
    # Bayesian Reasoning
    INITIAL_TRAP_PROBABILITY = 0.2  # Prior belief that a room has a trap
    OBSERVATION_RELIABILITY = 0.9  # How reliable are observations
    
    # Agent Settings
    AGENT_HEALTH = 100
    SEARCH_ALGORITHM = "astar"  # Options: "bfs", "dfs", "astar"
    
    # Display
    SHOW_FULL_MAP = False  # If True, shows all rooms; if False, fog of war
    VERBOSE = True  # Detailed output
    
    # Game Rules
    MAX_TURNS = 100  # Maximum turns before game over
    
    @classmethod
    def get_room_count(cls):
        """Get number of rooms based on map size"""
        return cls.ROOM_COUNTS.get(cls.MAP_SIZE, 12)
