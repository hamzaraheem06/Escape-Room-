"""
Pygame GUI for AI Escape Room
Visual interface with room graph, agent/guard, and real-time AI visualization
"""

import pygame
import sys
import math
from typing import Dict, List, Tuple, Optional
import copy
from config import Config
from environment import Environment
from agent import Agent
from guard import Guard
from game import EscapeRoomGame
from csp_solver import generate_puzzle, CSPSolver
from ai_solver import AISolver

# Initialize Pygame
pygame.init()

# Colors
class Colors:
    # Base colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (50, 50, 50)
    
    # Game element colors
    BACKGROUND = (20, 20, 30)
    PANEL_BG = (30, 30, 45)
    
    # Room colors
    ROOM_NORMAL = (60, 80, 100)
    ROOM_VISITED = (80, 120, 150)
    ROOM_CURRENT = (100, 200, 255)
    ROOM_START = (50, 200, 50)
    ROOM_EXIT = (255, 100, 50)
    
    # Entity colors
    AGENT = (0, 255, 100)
    GUARD = (255, 50, 50)
    KEY = (255, 215, 0)
    TRAP = (255, 0, 0)
    
    # Path colors
    PATH_COLOR = (255, 255, 100)
    
    # Risk colors (for heatmap)
    RISK_LOW = (100, 255, 100)
    RISK_MEDIUM = (255, 200, 100)
    RISK_HIGH = (255, 100, 100)
    
    # UI colors
    BUTTON_NORMAL = (70, 100, 130)
    BUTTON_HOVER = (90, 130, 170)
    BUTTON_ACTIVE = (110, 150, 200)
    TEXT_COLOR = WHITE
    HEALTH_BAR = (50, 255, 50)
    HEALTH_BAR_BG = (100, 50, 50)


class Button:
    """Interactive button"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw button"""
        color = Colors.BUTTON_HOVER if self.hovered else Colors.BUTTON_NORMAL
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, Colors.WHITE, self.rect, 2)
        
        text_surface = font.render(self.text, True, Colors.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                return True
        return False


class EscapeRoomGUI:
    """Main GUI class for AI Escape Room"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        
        
        
        
        # Screen setup
        self.screen_width = 1400
        self.screen_height = 900
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("AI Escape Room - Pygame GUI")
        
        # Game components
        self.env = Environment(self.config)
        self.agent = Agent(self.env, self.config)
        self.guard = Guard(self.env, self.config)
        
        # Game state
        self.turn = 0
        self.game_over = False
        self.victory = False
        self.paused = False

        # AI solution tracking
        self.showing_solution = False
        self.ai_solution_steps = []
        self.fullscreen = False
        self.use_astar = True
        
        
        # Visual elements
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)

        # Room positions (will be calculated)
        self.room_positions = {}   # <-- add this initialization

        # UI elements list must exist before layout recalculation
        self.buttons: List[Button] = []

        # Layout (responsive) - calculate once
        self._calculate_layout()

        # UI element creation (uses controls_area set by _calculate_layout)
        self._create_buttons()
        
        # Event log
        self.event_log: List[str] = []
        self.max_log_entries = 10
        
        # Path visualization
        self.current_path: Optional[List[int]] = None
        
        # Animation
        self.animation_progress = 0
        self.animating = False
        
        # Add welcome message
        self.add_log("Welcome to AI Escape Room!")
        self.add_log(f"Collect {self.env.total_keys} keys and reach the exit!")
        
    def _calculate_room_positions(self):
        """Calculate positions for rooms in circular/grid layout"""
        num_rooms = len(self.env.rooms)
        
        # Use circular layout for better visualization
        center_x = self.map_area.centerx
        center_y = self.map_area.centery
        radius = min(self.map_area.width, self.map_area.height) // 2 - 50
        
        for room_id in range(num_rooms):
            angle = (2 * math.pi * room_id) / num_rooms - math.pi / 2
            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            self.room_positions[room_id] = (x, y)
            
    def _create_buttons(self):
        """Create control buttons"""
        button_y = self.controls_area.y + 40
        button_width = 200
        button_height = 35
        button_x = self.controls_area.x + 125
        spacing = 45
        
        buttons_data = [
            ("Auto Move", "auto_move"),
            ("Find Key", "find_key"),
            ("Plan Escape", "plan_escape"),
            ("Solve Puzzle", "solve_puzzle"),
            ("Next Turn", "next_turn"),
            ("🤖 AI Solver", "ai_solver"),
            ("⚡ AI Step", "ai_step"),
            ("🔄 Reset", "reset_game"),
            ("⛶ Fullscreen (F11)", "toggle_fullscreen"),
        ]
        
        for i, (text, action) in enumerate(buttons_data):
            button = Button(
                button_x, button_y + i * spacing,
                button_width, button_height,
                text, action
            )
            self.buttons.append(button)
            
    def add_log(self, message: str):
        """Add message to event log"""
        self.event_log.append(message)
        if len(self.event_log) > self.max_log_entries:
            self.event_log.pop(0)
            
    def _calculate_layout(self):
        """Calculate responsive layout based on current window size"""
        width, height = self.screen.get_size()
        
        # Reserve space for margins and legend
        margin = 40
        legend_height = 120
        
        # Map takes left 60% of screen
        map_width = int(width * 0.58)
        map_height = height - (margin * 2 + legend_height)
        self.map_area = pygame.Rect(margin, margin + legend_height, map_width, map_height)
        
        # Right panel for stats, controls, and log
        right_panel_x = map_width + (margin * 2)
        right_panel_width = width - right_panel_x - margin
        
        self.stats_area = pygame.Rect(right_panel_x, margin + legend_height, right_panel_width, 180)
        self.controls_area = pygame.Rect(right_panel_x, self.stats_area.bottom + 20, right_panel_width, 350)
        self.log_area = pygame.Rect(right_panel_x, self.controls_area.bottom + 20, right_panel_width, height - self.controls_area.bottom - 40)
        
        # Recalculate room positions for new map area
        self._calculate_room_positions()
        
        # Recreate buttons with new layout
        self.buttons.clear()
        self._create_buttons()
        
    def _create_legend_surface(self) -> pygame.Surface:
        """Create a legend surface explaining the map elements"""
        legend_width = self.map_area.width - 20
        legend_height = 100
        
        surface = pygame.Surface((legend_width, legend_height), pygame.SRCALPHA)
        
        # Background
        pygame.draw.rect(surface, (40, 40, 60), (0, 0, legend_width, legend_height), border_radius=8)
        pygame.draw.rect(surface, Colors.WHITE, (0, 0, legend_width, legend_height), 2, border_radius=8)
        
        font = self.font_small
        
        # Title
        title = font.render("MAP LEGEND", True, Colors.TEXT_COLOR)
        surface.blit(title, (10, 8))
        
        # Legend items
        items = [
            ("🟢", "Unvisited Room", Colors.ROOM_NORMAL),
            ("🔵", "Current Location", Colors.ROOM_CURRENT),
            ("🟠", "Exit Room", Colors.ROOM_EXIT),
            ("🔑", "Key Location", Colors.KEY),
            ("🔴", "Trap/Guard", Colors.TRAP),
            ("🟡", "Planned Path", Colors.PATH_COLOR)
        ]
        
        x_start = 15
        y_start = 30
        for i, (emoji, text, color) in enumerate(items):
            x = x_start + (i % 3) * 110
            y = y_start + (i // 3) * 25
            
            # Draw color indicator
            pygame.draw.circle(surface, color, (x, y), 6)
            
            # Draw text
            text_surface = font.render(f"{emoji} {text}", True, Colors.TEXT_COLOR)
            surface.blit(text_surface, (x + 12, y - 8))
            
        return surface
            
    def reset_game(self):
        """Reset the game to initial state"""
        self.env = Environment(self.config)
        self.agent = Agent(self.env, self.config)
        self.guard = Guard(self.env, self.config)
        
        self.turn = 0
        self.game_over = False
        self.victory = False
        self.showing_solution = False
        self.ai_solution_steps.clear()
        
        self.add_log("🔄 Game Reset!")
        self.add_log(f"Collect {self.env.total_keys} keys and reach the exit!")
        
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
            
        self._calculate_layout()
        self.add_log(f"{'⛶ Entered Fullscreen' if self.fullscreen else '↶ Exited Fullscreen'}")
            
    def show_ai_solution_path(self, env, agent):
        """Display step-by-step AI solution based on agent's room visit history"""
        self.ai_solution_steps = []
        
        # Create step-by-step solution display
        self.ai_solution_steps.append("🎯 AI OPTIMAL SOLUTION:")
        
        # Find the path to exit
        path = agent.find_path(agent.current_room, env.exit_room_id)
        if path and len(path) > 1:
            self.ai_solution_steps.append(f"📍 Start: Room {env.start_room_id}")
            
            for i, room_id in enumerate(path):
                if room_id == env.exit_room_id:
                    self.ai_solution_steps.append(f"🏁 Step {i+1}: Reach Exit Room {room_id} ✅")
                    break
                    
                room = env.get_room(room_id)
                step_type = "Move to"
                
                # Check if this is a key room
                if room.has_key:
                    step_type = "Find key in"
                elif room.has_puzzle:
                    step_type = "Solve puzzle in"
                elif room_id not in agent.rooms_visited:
                    step_type = "Explore"
                    
                self.ai_solution_steps.append(f"⚡ Step {i+1}: {step_type} Room {room_id} ({room.name})")
        
        # Add final summary
        if len(agent.keys_collected) >= env.total_keys:
            self.ai_solution_steps.append(f"🏆 VICTORY: Escaped with {len(agent.keys_collected)}/{env.total_keys} keys in {agent.moves_made} moves")
        else:
            self.ai_solution_steps.append(f"❌ Need {env.total_keys - len(agent.keys_collected)} more keys to escape")
            
        # Add efficiency analysis
        efficiency = (env.total_keys / max(agent.moves_made, 1)) * 100
        self.ai_solution_steps.append(f"📈 Efficiency: {efficiency:.1f}% (keys per move)")
        
        self.showing_solution = True
        
    def get_room_color(self, room_id: int) -> Tuple[int, int, int]:
        """Get color for room based on state"""
        room = self.env.get_room(room_id)
        
        # Special rooms
        if room_id == self.env.start_room_id:
            return Colors.ROOM_START
        if room_id == self.env.exit_room_id:
            return Colors.ROOM_EXIT
        if room_id == self.agent.current_room:
            return Colors.ROOM_CURRENT
            
        # Based on trap probability (heatmap)
        trap_prob = self.agent.belief_system.get_trap_probability(room_id)
        if room.visited:
            # Visited rooms - show if trap was found
            if room.trap_triggered:
                return Colors.TRAP
            else:
                return Colors.ROOM_VISITED
        else:
            # Unvisited - show risk level
            if trap_prob > 0.6:
                return Colors.RISK_HIGH
            elif trap_prob > 0.3:
                return Colors.RISK_MEDIUM
            else:
                return Colors.RISK_LOW
                
    def draw_room(self, surface: pygame.Surface, room_id: int):
        """Draw a single room"""
        if room_id not in self.room_positions:
            return
            
        x, y = self.room_positions[room_id]
        room = self.env.get_room(room_id)
        color = self.get_room_color(room_id)
        
        # Draw room circle
        room_radius = 25
        pygame.draw.circle(surface, color, (x, y), room_radius)
        pygame.draw.circle(surface, Colors.WHITE, (x, y), room_radius, 2)
        
        # Draw room number
        text = self.font_small.render(str(room_id), True, Colors.BLACK)
        text_rect = text.get_rect(center=(x, y))
        surface.blit(text, text_rect)
        
        # Draw icons for room contents
        icon_y = y - room_radius - 15
        
        # Key icon
        if room.has_key and room.key_id not in self.agent.keys_collected:
            pygame.draw.circle(surface, Colors.KEY, (x, icon_y), 8)
            
        # Trap icon (if known)
        if room.trap_triggered:
            pygame.draw.polygon(surface, Colors.TRAP, [
                (x, icon_y - 8),
                (x - 7, icon_y + 5),
                (x + 7, icon_y + 5)
            ])
            
    def draw_connections(self, surface: pygame.Surface):
        """Draw connections between rooms"""
        for room_id, room in self.env.rooms.items():
            if room_id not in self.room_positions:
                continue
                
            x1, y1 = self.room_positions[room_id]
            
            for neighbor_id, is_locked in room.neighbors:
                if neighbor_id not in self.room_positions:
                    continue
                    
                # Only draw each connection once
                if neighbor_id > room_id:
                    x2, y2 = self.room_positions[neighbor_id]
                    
                    # Choose color based on lock status
                    color = Colors.GRAY if not is_locked else Colors.DARK_GRAY
                    thickness = 2 if not is_locked else 1
                    
                    # Draw line
                    pygame.draw.line(surface, color, (x1, y1), (x2, y2), thickness)
                    
                    # Draw lock icon if locked
                    if is_locked:
                        mid_x = (x1 + x2) // 2
                        mid_y = (y1 + y2) // 2
                        pygame.draw.rect(surface, Colors.DARK_GRAY,
                                       (mid_x - 5, mid_y - 5, 10, 10))
                        
    def draw_path(self, surface: pygame.Surface):
        """Draw current planned path"""
        if not self.current_path or len(self.current_path) < 2:
            return
            
        for i in range(len(self.current_path) - 1):
            room1 = self.current_path[i]
            room2 = self.current_path[i + 1]
            
            if room1 in self.room_positions and room2 in self.room_positions:
                x1, y1 = self.room_positions[room1]
                x2, y2 = self.room_positions[room2]
                
                pygame.draw.line(surface, Colors.PATH_COLOR, (x1, y1), (x2, y2), 4)
                
    def draw_agent(self, surface: pygame.Surface):
        """Draw agent"""
        if self.agent.current_room in self.room_positions:
            x, y = self.room_positions[self.agent.current_room]
            pygame.draw.circle(surface, Colors.AGENT, (x, y), 15)
            pygame.draw.circle(surface, Colors.WHITE, (x, y), 15, 2)
            
            # Draw 'A' for Agent
            text = self.font_medium.render("A", True, Colors.BLACK)
            text_rect = text.get_rect(center=(x, y))
            surface.blit(text, text_rect)
            
    def draw_guard(self, surface: pygame.Surface):
        """Draw guard"""
        if not self.config.GUARD_ENABLED:
            return
            
        if self.guard.current_room in self.room_positions:
            x, y = self.room_positions[self.guard.current_room]
            pygame.draw.circle(surface, Colors.GUARD, (x, y), 15)
            pygame.draw.circle(surface, Colors.WHITE, (x, y), 15, 2)
            
            # Draw 'G' for Guard
            text = self.font_medium.render("G", True, Colors.WHITE)
            text_rect = text.get_rect(center=(x, y))
            surface.blit(text, text_rect)
            
    def draw_map(self, surface: pygame.Surface):
        """Draw the entire map"""
        # Draw map background
        pygame.draw.rect(surface, Colors.PANEL_BG, self.map_area)
        pygame.draw.rect(surface, Colors.WHITE, self.map_area, 2)
        
        # Title
        title = self.font_large.render("Escape Room Map", True, Colors.TEXT_COLOR)
        surface.blit(title, (self.map_area.x + 10, self.map_area.y + 10))
        
        # Draw connections first (so they appear behind rooms)
        self.draw_connections(surface)
        
        # Draw planned path
        self.draw_path(surface)
        
        # Draw rooms
        for room_id in self.env.rooms:
            self.draw_room(surface, room_id)
            
        # Draw guard
        self.draw_guard(surface)
        
        # Draw agent (on top)
        self.draw_agent(surface)
        
    def draw_stats(self, surface: pygame.Surface):
        """Draw statistics panel"""
        pygame.draw.rect(surface, Colors.PANEL_BG, self.stats_area)
        pygame.draw.rect(surface, Colors.WHITE, self.stats_area, 2)
        
        x = self.stats_area.x + 15
        y = self.stats_area.y + 15
        line_height = 30
        
        # Title
        title = self.font_medium.render("Agent Status", True, Colors.TEXT_COLOR)
        surface.blit(title, (x, y))
        y += line_height + 10
        
        # Stats
        stats = [
            f"Turn: {self.turn}",
            f"Location: Room {self.agent.current_room}",
            f"Health: {self.agent.health}/{self.config.AGENT_HEALTH}",
            f"Keys: {len(self.agent.keys_collected)}/{self.env.total_keys}",
            f"Moves: {self.agent.moves_made}",
            f"Rooms Visited: {len(self.agent.rooms_visited)}/{self.env.room_count}",
        ]
        
        for stat in stats:
            text = self.font_small.render(stat, True, Colors.TEXT_COLOR)
            surface.blit(text, (x, y))
            y += line_height
            
        # Health bar
        y += 10
        bar_width = self.stats_area.width - 30
        bar_height = 25
        
        # Background
        pygame.draw.rect(surface, Colors.HEALTH_BAR_BG,
                        (x, y, bar_width, bar_height))
        
        # Health fill
        health_ratio = self.agent.health / self.config.AGENT_HEALTH
        fill_width = int(bar_width * health_ratio)
        pygame.draw.rect(surface, Colors.HEALTH_BAR,
                        (x, y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, Colors.WHITE,
                        (x, y, bar_width, bar_height), 2)
        
    def draw_controls(self, surface: pygame.Surface):
        """Draw control panel"""
        pygame.draw.rect(surface, Colors.PANEL_BG, self.controls_area)
        pygame.draw.rect(surface, Colors.WHITE, self.controls_area, 2)
        
        # Title
        title = self.font_medium.render("Controls", True, Colors.TEXT_COLOR)
        surface.blit(title, (self.controls_area.x + 15, self.controls_area.y + 10))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface, self.font_small)
            
    def draw_log(self, surface: pygame.Surface):
        """Draw event log"""
        pygame.draw.rect(surface, Colors.PANEL_BG, self.log_area)
        pygame.draw.rect(surface, Colors.WHITE, self.log_area, 2)
        
        # Title
        title = self.font_medium.render("Event Log", True, Colors.TEXT_COLOR)
        surface.blit(title, (self.log_area.x + 15, self.log_area.y + 10))
        
        # Log entries
        x = self.log_area.x + 15
        y = self.log_area.y + 45
        line_height = 18
        
        for message in self.event_log[-10:]:
            text = self.font_small.render(message[:60], True, Colors.TEXT_COLOR)
            surface.blit(text, (x, y))
            y += line_height
            
    def draw(self):
        """Draw everything"""
        self.screen.fill(Colors.BACKGROUND)
        
        # Draw legend at top
        legend_surface = self._create_legend_surface()
        self.screen.blit(legend_surface, (self.map_area.x, 10))
        
        self.draw_map(self.screen)
        self.draw_stats(self.screen)
        self.draw_controls(self.screen)
        self.draw_log(self.screen)
        
        # Draw AI solution steps if showing
        if self.showing_solution and self.ai_solution_steps:
            self.draw_ai_solution(self.screen)
        
        # Draw game over/victory
        if self.game_over:
            self.draw_game_over()
            
        pygame.display.flip()
        
    def draw_ai_solution(self, surface: pygame.Surface):
        """Draw AI solution steps overlay"""
        # Create semi-transparent background
        overlay_rect = pygame.Rect(self.map_area.x, self.map_area.y, self.map_area.width, 300)
        overlay = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        
        # Draw close button
        close_button = pygame.Rect(overlay_rect.width - 30, 10, 20, 20)
        pygame.draw.rect(overlay, Colors.GUARD, close_button)
        close_text = self.font_small.render("X", True, Colors.WHITE)
        close_rect = close_text.get_rect(center=close_button.center)
        overlay.blit(close_text, close_rect)
        
        # Draw title
        title = self.font_medium.render("AI SOLUTION STEPS", True, Colors.KEY)
        overlay.blit(title, (10, 10))
        
        # Draw solution steps
        y_offset = 40
        for step in self.ai_solution_steps[:8]:  # Show max 8 steps
            step_text = self.font_small.render(step, True, Colors.TEXT_COLOR)
            overlay.blit(step_text, (15, y_offset))
            y_offset += 22
            
        surface.blit(overlay, (overlay_rect.x, overlay_rect.y))
        
    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.victory:
            text = self.font_large.render("VICTORY!", True, Colors.KEY)
            subtext = f"Escaped in {self.turn} turns!"
        else:
            text = self.font_large.render("GAME OVER", True, Colors.GUARD)
            subtext = f"Failed after {self.turn} turns"
            
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(text, text_rect)
        
        sub = self.font_medium.render(subtext, True, Colors.TEXT_COLOR)
        sub_rect = sub.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        self.screen.blit(sub, sub_rect)
        
        restart = self.font_small.render("Press R to restart or ESC to quit", True, Colors.TEXT_COLOR)
        restart_rect = restart.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
        self.screen.blit(restart, restart_rect)
        
    def handle_button_click(self, action: str):
        """Handle button actions"""
        if self.game_over:
            return
            
        if action == "auto_move":
            self.action_auto_move()
        elif action == "find_key":
            self.action_find_key()
        elif action == "plan_escape":
            self.action_plan_escape()
        elif action == "solve_puzzle":
            self.action_solve_puzzle()
        elif action == "next_turn":
            self.next_turn()
        elif action == "ai_solver":
            self.action_ai_solver()
        elif action == "ai_step":
            self.action_ai_step()
        elif action == "reset_game":
            self.reset_game()
        elif action == "toggle_fullscreen":
            self.toggle_fullscreen()
            
    def action_auto_move(self):
        """Auto move to next logical room (fixed logic)"""
        neighbors = self.env.get_unlocked_neighbors(self.agent.current_room)
        if not neighbors:
            self.add_log("No available moves!")
            return
            
        # Priority-based intelligent move selection
        priority_targets = []
        
        # Priority 1: Find nearest key
        if len(self.agent.keys_collected) < self.env.total_keys:
            result = self.agent.find_nearest_key()
            if result:
                key_room, path = result
                if len(path) > 1:
                    priority_targets.append((path[1], "key", len(path)))
        
        # Priority 2: Go to exit if all keys collected
        if len(self.agent.keys_collected) >= self.env.total_keys:
            exit_room = self.env.exit_room_id
            path = self.agent.find_path(self.agent.current_room, exit_room)
            if path and len(path) > 1:
                priority_targets.append((path[1], "exit", len(path)))
        
        # Priority 3: Explore unvisited safe rooms
        for neighbor_id in neighbors:
            room = self.env.get_room(neighbor_id)
            if not room.visited and room.id != self.agent.current_room:
                trap_prob = self.agent.belief_system.get_trap_probability(neighbor_id)
                if trap_prob < 0.5:  # Reasonable risk threshold
                    priority_targets.append((neighbor_id, "explore", 1))
        
        # Priority 4: Move to least risky available room
        if not priority_targets:
            safest = min(neighbors, 
                        key=lambda r: self.agent.belief_system.get_trap_probability(r))
            priority_targets.append((safest, "safe", 1))
        
        # Execute the best move
        target_room, move_type, priority = priority_targets[0]
        
        success, message = self.agent.move_to(target_room)
        self.add_log(f"Auto-move ({move_type}): {message}")
        
        if success:
            self.next_turn()
            
    def action_find_key(self):
        """Find path to nearest key"""
        result = self.agent.find_nearest_key()
        if result:
            key_room, path = result
            self.current_path = path
            self.add_log(f"Path to key in Room {key_room} (length: {len(path)-1})")
        else:
            self.current_path = None
            self.add_log("All keys collected!")
            
    def action_plan_escape(self):
        """Plan path to exit"""
        path = self.agent.plan_escape_route()
        if path:
            self.current_path = path
            self.add_log(f"Escape path found (length: {len(path)-1})")
        else:
            self.current_path = None
            self.add_log("No path to exit! Solve puzzles first.")
            
    def action_solve_puzzle(self):
        """Solve puzzle in current room"""
        current_room = self.env.get_room(self.agent.current_room)
        locked_neighbors = [(nid, locked) for nid, locked in current_room.neighbors if locked]
        
        if not locked_neighbors:
            self.add_log("No locked doors here!")
            return
            
        # Generate and solve puzzle
        difficulty = "medium"
        puzzle = generate_puzzle(difficulty)
        solver = CSPSolver(puzzle)
        solution = solver.solve()
        
        if solution:
            # Unlock doors
            for neighbor_id, locked in locked_neighbors:
                if locked:
                    self.env.unlock_door_between(self.agent.current_room, neighbor_id)
                    
            self.agent.puzzles_solved += 1
            self.add_log(f"Puzzle solved! Doors unlocked.")
        else:
            self.add_log("Puzzle solving failed!")
            
    def next_turn(self):
        """Process next turn"""
        if self.game_over:
            return
        
        # Check victory conditions FIRST (before incrementing turn)
        if (len(self.agent.keys_collected) >= self.env.total_keys and 
            self.agent.current_room == self.env.exit_room_id):
            self.game_over = True
            self.victory = True
            self.add_log("🏆 VICTORY! You escaped!")
            return
            
        if self.agent.health <= 0:
            self.game_over = True
            self.victory = False
            self.add_log("💀 Game Over! Health reached zero!")
            return
        
        if self.turn >= self.config.MAX_TURNS:
            self.game_over = True
            self.victory = False
            self.add_log("⏰ Game Over! Maximum turns reached!")
            return
        
        # Increment turn counter
        self.turn += 1
        
        # Move guard
        guard_room, message = self.guard.make_move(self.agent.current_room)
        self.add_log(f"Guard: {message}")
        
        # Check if caught by guard
        if self.guard.player_caught:
            self.game_over = True
            self.victory = False
            self.add_log("🚨 CAUGHT BY GUARD!")
            return
            
    def action_ai_solver(self):
        """Run full AI solver simulation with step-by-step solution display"""
        if self.game_over:
            self.add_log("Game already over!")
            return
            
        self.add_log("🤖 Starting AI Solver...")
        self.add_log("⏳ Analyzing optimal path...")
        
        # Store current state
        original_env = Environment(self.config)
        original_env.rooms = {r_id: copy.deepcopy(room) for r_id, room in self.env.rooms.items()}
        original_env.total_keys = self.env.total_keys
        original_env.start_room_id = self.env.start_room_id
        original_env.exit_room_id = self.env.exit_room_id
        
        original_agent = Agent(original_env, self.config)
        original_agent.current_room = self.agent.current_room
        original_agent.keys_collected = set(self.agent.keys_collected)
        original_agent.health = self.agent.health
        original_agent.moves_made = self.agent.moves_made
        original_agent.rooms_visited = set(self.agent.rooms_visited)
        original_agent.belief_system = copy.deepcopy(self.agent.belief_system)
        
        # Create AI solver with clean environment
        ai_solver = AISolver(config=self.config, verbose=False)
        ai_solver.env = original_env
        ai_solver.agent = original_agent
        ai_solver.guard = Guard(original_env, self.config)
        ai_solver.turn = 0
        ai_solver.max_turns = self.config.MAX_TURNS
        
        # Run AI solver on clean state
        success = ai_solver.solve_escape_room()
        
        if success:
            self.add_log("🎉 AI Solver: Victory achieved!")
            self.add_log(f"📊 Optimal solution: {ai_solver.turn} turns, {original_agent.health} health, {len(original_agent.keys_collected)} keys")
            
            # Show step-by-step solution based on actual room visits
            self.show_ai_solution_path(ai_solver.env, original_agent)
            
        else:
            self.add_log("😔 AI Solver: Failed to escape")
            
        # Update GUI state with AI results (but don't reset current game)
        self.add_log(f"📈 AI Results: {ai_solver.turn} turns, {original_agent.health} health, {len(original_agent.keys_collected)}/{original_env.total_keys} keys")
        
        # Run AI on current game state
        ai_solver_current = AISolver(config=self.config, verbose=False)
        ai_solver_current.env = self.env
        ai_solver_current.agent = self.agent
        ai_solver_current.guard = self.guard
        ai_solver_current.turn = self.turn
        ai_solver_current.max_turns = self.config.MAX_TURNS
        
        success_current = ai_solver_current.solve_escape_room()
        self.turn = ai_solver_current.turn
        self.game_over = ai_solver_current.game_over
        self.victory = ai_solver_current.victory
        
        if success_current:
            self.add_log("🏆 Applied AI solution to current game!")
        else:
            self.add_log("⚠️ AI couldn't solve current game state")
        
    def action_ai_step(self):
        """Execute one AI step"""
        if self.game_over:
            self.add_log("Game already over!")
            return
            
        self.add_log("🤖 AI Step...")
        
        # Create temporary AI solver for one step
        ai_solver = AISolver(config=self.config, verbose=False)
        ai_solver.env = self.env
        ai_solver.agent = self.agent
        ai_solver.guard = self.guard
        ai_solver.turn = self.turn
        
        # Execute one AI decision
        current_room = self.agent.current_room
        room = self.env.get_room(current_room)
        
        # Check if puzzle needs solving
        if room.has_puzzle and room.puzzle and not room.puzzle_solved:
            # Solve puzzle
            puzzle_data = room.puzzle
            solver = CSPSolver()
            solution = solver.solve(puzzle_data)
            if solution:
                room.puzzle_solved = True
                # Unlock doors
                for neighbor_id, is_locked in room.neighbors:
                    if is_locked:
                        self.env.unlock_door_between(current_room, neighbor_id)
                self.add_log("🧩 AI: Puzzle solved!")
                self.agent.puzzles_solved += 1
            else:
                self.add_log("🧩 AI: Failed to solve puzzle")
                return
        
        # Find next target
        target = ai_solver.find_priority_target()
        
        if target:
            # Navigate one step toward target
            if self.use_astar:
                path = self.agent.find_path_astar(current_room, target)
            else:
                path = self.agent.find_path_bfs(current_room, target)
            
            if path and len(path) > 1:
                next_room = path[1]
                success, message = self.agent.move_to(next_room)
                self.add_log(f"🤖 AI: {message}")
                
                # Move guard
                guard_room, guard_message = self.guard.make_move(self.agent.current_room)
                self.add_log(f"Guard: {guard_message}")
                
                self.turn += 1
                
                # Check game end
                if (len(self.agent.keys_collected) >= self.env.total_keys and 
                    self.agent.current_room == self.env.exit_room_id):
                    self.game_over = True
                    self.add_log("🎉 Victory! AI reached the exit!")
                elif self.agent.health <= 0:
                    self.game_over = True
                    self.add_log("💀 Game Over! AI died!")
            else:
                self.add_log("🤖 AI: No valid path found")
        else:
            self.add_log("🤖 AI: No target found")
            
        self.turn += 1
        
        # Guard's turn
        if self.config.GUARD_ENABLED:
            new_room, message = self.guard.make_move(self.agent.current_room)
            self.add_log(f"Guard: {message}")
            
            if self.guard.player_caught:
                self.game_over = True
                self.victory = False
                self.add_log("CAUGHT BY GUARD!")
                
        # Check win/loss
        if self.agent.current_room == self.env.exit_room_id:
            if len(self.agent.keys_collected) == self.env.total_keys:
                self.game_over = True
                self.victory = True
                self.add_log("ESCAPED! YOU WIN!")
                
        if self.agent.health <= 0:
            self.game_over = True
            self.victory = False
            self.add_log("HEALTH DEPLETED!")
            
        if self.turn >= self.config.MAX_TURNS:
            self.game_over = True
            self.victory = False
            self.add_log("TIME'S UP!")
            
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.fullscreen:
                        self.toggle_fullscreen()
                    else:
                        return False
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                    
            if event.type == pygame.VIDEORESIZE:
                self.screen_width, self.screen_height = event.size
                self._calculate_layout()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicking AI solution close button
                if self.showing_solution:
                    close_button = pygame.Rect(self.map_area.x + self.map_area.width - 30, 
                                             self.map_area.y + 10, 20, 20)
                    if close_button.collidepoint(event.pos):
                        self.showing_solution = False
                        
            # Button handling
            for button in self.buttons:
                if button.handle_event(event):
                    self.handle_button_click(button.action)
                    
        return True
        
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(self.fps)
            
        pygame.quit()
        sys.exit()


def main():
    """Main entry point for GUI"""
    config = Config()
    config.MAP_SIZE = "large"
    config.GUARD_ENABLED = True
    
    gui = EscapeRoomGUI(config)
    gui.run()


if __name__ == "__main__":
    main()
