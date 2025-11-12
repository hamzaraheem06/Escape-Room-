"""
Environment representation for AI Escape Room
Includes room graph, keys, traps, and puzzles
"""

import random
from typing import Dict, List, Set, Tuple, Optional
from config import Config


class Room:
    """Represents a single room in the escape room"""
    
    def __init__(self, room_id: int, name: str):
        self.id = room_id
        self.name = name
        self.has_key = False
        self.key_id = None
        self.has_trap = False
        self.trap_triggered = False
        self.has_puzzle = False
        self.puzzle = None
        self.puzzle_solved = False
        self.visited = False
        self.is_exit = False
        self.neighbors: List[Tuple[int, bool]] = []  # (room_id, is_locked)
        
    def add_neighbor(self, room_id: int, is_locked: bool = False):
        """Add a neighboring room"""
        self.neighbors.append([room_id, is_locked])
        
    def unlock_door(self, neighbor_id: int):
        """Unlock door to a neighbor"""
        for i, (nid, locked) in enumerate(self.neighbors):
            if nid == neighbor_id:
                self.neighbors[i][1] = False
                
    def __repr__(self):
        return f"Room({self.id}: {self.name})"


class Environment:
    """Game environment with room graph"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.rooms: Dict[int, Room] = {}
        self.start_room_id = 0
        self.exit_room_id = None
        self.keys_collected = set()
        self.total_keys = self.config.NUM_KEYS
        self.room_count = self.config.get_room_count()
        
        # Initialize environment
        self._generate_rooms()
        self._connect_rooms()
        self._place_keys()
        self._place_traps()
        self._place_puzzles()
        
    def _generate_rooms(self):
        """Generate rooms based on configuration"""
        room_names = [
            "Entrance Hall", "Storage Room", "Library", "Armory", 
            "Kitchen", "Dungeon", "Guard Room", "Treasury",
            "Laboratory", "Chapel", "Throne Room", "Garden",
            "Tower", "Cellar", "Study", "Gallery",
            "Chamber", "Vault", "Courtyard", "Crypt",
            "Workshop", "Barracks", "Dining Hall", "Prison",
            "Observatory", "Archive", "Forge", "Sanctuary",
            "Quarters", "Hall of Mirrors"
        ]
        
        for i in range(self.room_count):
            name = room_names[i] if i < len(room_names) else f"Room {i}"
            self.rooms[i] = Room(i, name)
            
        # Set start and exit
        self.start_room_id = 0
        self.rooms[0].name = "Entrance (START)"
        
        self.exit_room_id = self.room_count - 1
        self.rooms[self.exit_room_id].name = "Exit Door (ESCAPE)"
        self.rooms[self.exit_room_id].is_exit = True
        
    def _connect_rooms(self):
        """Create a connected graph of rooms"""
        # Create a path from start to exit (ensure solvability)
        for i in range(self.room_count - 1):
            self.rooms[i].add_neighbor(i + 1, is_locked=False)
            self.rooms[i + 1].add_neighbor(i, is_locked=False)
            
        # Add additional connections for complexity
        additional_edges = self.room_count // 3
        for _ in range(additional_edges):
            room1 = random.randint(0, self.room_count - 1)
            room2 = random.randint(0, self.room_count - 1)
            
            if room1 != room2 and not self._are_neighbors(room1, room2):
                # Some doors are locked
                is_locked = random.random() < 0.4
                self.rooms[room1].add_neighbor(room2, is_locked=is_locked)
                self.rooms[room2].add_neighbor(room1, is_locked=is_locked)
                
    def _are_neighbors(self, room1_id: int, room2_id: int) -> bool:
        """Check if two rooms are already connected"""
        return any(nid == room2_id for nid, _ in self.rooms[room1_id].neighbors)
        
    def _place_keys(self):
        """Place keys in random rooms (not start or exit)"""
        available_rooms = list(range(1, self.room_count - 1))
        random.shuffle(available_rooms)
        
        for i in range(min(self.config.NUM_KEYS, len(available_rooms))):
            room_id = available_rooms[i]
            self.rooms[room_id].has_key = True
            self.rooms[room_id].key_id = i
            
    def _place_traps(self):
        """Place hidden traps in random rooms"""
        available_rooms = list(range(1, self.room_count - 1))
        random.shuffle(available_rooms)
        
        for i in range(min(self.config.NUM_TRAPS, len(available_rooms))):
            room_id = available_rooms[i]
            if not self.rooms[room_id].has_key:  # Don't put trap in key rooms
                self.rooms[room_id].has_trap = True
                
    def _place_puzzles(self):
        """Place puzzles on locked doors"""
        # Find locked doors and assign puzzles
        puzzle_count = 0
        for room_id, room in self.rooms.items():
            for neighbor_id, is_locked in room.neighbors:
                if is_locked:
                    room.has_puzzle = True
                    puzzle_count += 1
                    break  # One puzzle per room is enough
                    
    def get_room(self, room_id: int) -> Optional[Room]:
        """Get room by ID"""
        return self.rooms.get(room_id)
        
    def get_unlocked_neighbors(self, room_id: int) -> List[int]:
        """Get list of accessible neighbor room IDs"""
        room = self.rooms[room_id]
        return [nid for nid, locked in room.neighbors if not locked]
        
    def get_all_neighbors(self, room_id: int) -> List[Tuple[int, bool]]:
        """Get all neighbors with lock status"""
        return self.rooms[room_id].neighbors
        
    def unlock_door_between(self, room1_id: int, room2_id: int):
        """Unlock door between two rooms"""
        self.rooms[room1_id].unlock_door(room2_id)
        self.rooms[room2_id].unlock_door(room1_id)
        
    def collect_key(self, room_id: int) -> bool:
        """Collect key from room if present"""
        room = self.rooms[room_id]
        if room.has_key and room.key_id not in self.keys_collected:
            self.keys_collected.add(room.key_id)
            return True
        return False
        
    def trigger_trap(self, room_id: int) -> bool:
        """Trigger trap in room if present"""
        room = self.rooms[room_id]
        if room.has_trap and not room.trap_triggered:
            room.trap_triggered = True
            return True
        return False
        
    def get_map_summary(self) -> str:
        """Get text summary of the map"""
        summary = [f"\n{'='*60}"]
        summary.append(f"ESCAPE ROOM MAP ({self.config.MAP_SIZE.upper()} - {self.room_count} rooms)")
        summary.append(f"{'='*60}")
        summary.append(f"Keys to collect: {self.total_keys}")
        summary.append(f"Keys collected: {len(self.keys_collected)}")
        summary.append(f"Start: Room {self.start_room_id}")
        summary.append(f"Exit: Room {self.exit_room_id}")
        summary.append(f"{'='*60}\n")
        return '\n'.join(summary)
