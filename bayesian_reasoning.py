"""
Bayesian reasoning module for probabilistic trap detection
"""

from typing import Dict, List
from config import Config


class BayesianBeliefSystem:
    """Maintains and updates probabilistic beliefs about trap locations"""
    
    def __init__(self, num_rooms: int, config: Config = None):
        self.config = config or Config()
        self.num_rooms = num_rooms
        
        # Belief state: probability that each room has a trap
        self.trap_beliefs: Dict[int, float] = {}
        
        # Initialize with prior probabilities
        for room_id in range(num_rooms):
            self.trap_beliefs[room_id] = self.config.INITIAL_TRAP_PROBABILITY
            
        # Evidence collected
        self.observations: Dict[int, str] = {}  # room_id -> "safe" or "trap"
        
    def update_belief(self, room_id: int, observation: str):
        """
        Update belief about a room based on observation using Bayes' theorem
        
        P(trap|observation) = P(observation|trap) * P(trap) / P(observation)
        
        Args:
            room_id: The room being observed
            observation: Either "safe" (no trap triggered) or "trap" (trap triggered)
        """
        if room_id not in self.trap_beliefs:
            return
            
        self.observations[room_id] = observation
        
        # Prior probability
        prior = self.trap_beliefs[room_id]
        
        # Likelihood: P(observation | trap exists)
        if observation == "trap":
            # If trap triggered, we're certain there's a trap
            likelihood_trap = 1.0
            likelihood_no_trap = 0.0
        else:  # observation == "safe"
            # If we entered safely, could mean:
            # - No trap exists (certain)
            # - Trap exists but didn't trigger (unlikely)
            likelihood_trap = 1.0 - self.config.OBSERVATION_RELIABILITY
            likelihood_no_trap = self.config.OBSERVATION_RELIABILITY
            
        # Posterior using Bayes' theorem
        # P(trap|safe) = P(safe|trap) * P(trap) / P(safe)
        # where P(safe) = P(safe|trap)*P(trap) + P(safe|no_trap)*P(no_trap)
        
        evidence = (likelihood_trap * prior) + (likelihood_no_trap * (1 - prior))
        
        if evidence > 0:
            posterior = (likelihood_trap * prior) / evidence
        else:
            posterior = 0.0
            
        self.trap_beliefs[room_id] = posterior
        
        # Update beliefs about neighboring rooms based on evidence
        self._propagate_beliefs(room_id, observation)
        
    def _propagate_beliefs(self, observed_room: int, observation: str):
        """
        Propagate belief updates to nearby rooms
        Traps tend to cluster, so observing a trap increases nearby room probabilities
        """
        if observation == "trap":
            # Increase probability of traps in nearby rooms
            for room_id in self.trap_beliefs:
                if room_id != observed_room and room_id not in self.observations:
                    distance = abs(room_id - observed_room)
                    if distance <= 2:
                        # Closer rooms have higher probability increase
                        increase = 0.1 * (1 / distance)
                        self.trap_beliefs[room_id] = min(0.95, 
                                                         self.trap_beliefs[room_id] + increase)
                                                         
        elif observation == "safe":
            # Slightly decrease probability of traps in nearby rooms
            for room_id in self.trap_beliefs:
                if room_id != observed_room and room_id not in self.observations:
                    distance = abs(room_id - observed_room)
                    if distance <= 2:
                        decrease = 0.05 * (1 / distance)
                        self.trap_beliefs[room_id] = max(0.05,
                                                         self.trap_beliefs[room_id] - decrease)
                                                         
    def get_trap_probability(self, room_id: int) -> float:
        """Get current belief probability that room has a trap"""
        return self.trap_beliefs.get(room_id, 0.0)
        
    def get_safest_rooms(self, room_ids: List[int], top_n: int = 3) -> List[int]:
        """Get the safest rooms from a list based on current beliefs"""
        sorted_rooms = sorted(room_ids, key=lambda rid: self.trap_beliefs.get(rid, 1.0))
        return sorted_rooms[:top_n]
        
    def get_riskiest_rooms(self, room_ids: List[int], top_n: int = 3) -> List[int]:
        """Get the riskiest rooms from a list based on current beliefs"""
        sorted_rooms = sorted(room_ids, key=lambda rid: self.trap_beliefs.get(rid, 0.0), 
                             reverse=True)
        return sorted_rooms[:top_n]
        
    def estimate_path_risk(self, path: List[int]) -> float:
        """
        Estimate total risk of a path as sum of trap probabilities
        Lower is safer
        """
        total_risk = 0.0
        for room_id in path:
            # Don't count rooms we've already observed
            if room_id not in self.observations:
                total_risk += self.trap_beliefs.get(room_id, 0.0)
        return total_risk
        
    def get_belief_summary(self) -> str:
        """Get a text summary of current beliefs"""
        summary = ["\n" + "="*50]
        summary.append("BAYESIAN BELIEF STATE (Trap Probabilities)")
        summary.append("="*50)
        
        # Group by probability ranges
        high_risk = []
        medium_risk = []
        low_risk = []
        verified = []
        
        for room_id, prob in self.trap_beliefs.items():
            if room_id in self.observations:
                verified.append((room_id, prob, self.observations[room_id]))
            elif prob > 0.6:
                high_risk.append((room_id, prob))
            elif prob > 0.3:
                medium_risk.append((room_id, prob))
            else:
                low_risk.append((room_id, prob))
                
        if verified:
            summary.append("\nVERIFIED (Observed):")
            for room_id, prob, obs in sorted(verified):
                status = "HAS TRAP" if obs == "trap" else "SAFE"
                summary.append(f"  Room {room_id}: {status} (P={prob:.2f})")
                
        if high_risk:
            summary.append("\nHIGH RISK (P > 0.6):")
            for room_id, prob in sorted(high_risk, key=lambda x: x[1], reverse=True):
                summary.append(f"  Room {room_id}: P={prob:.2f}")
                
        if medium_risk:
            summary.append("\nMEDIUM RISK (0.3 < P < 0.6):")
            for room_id, prob in sorted(medium_risk, key=lambda x: x[1], reverse=True):
                summary.append(f"  Room {room_id}: P={prob:.2f}")
                
        # Only show a few low risk rooms
        if low_risk:
            summary.append(f"\nLOW RISK (P < 0.3): {len(low_risk)} rooms")
            
        summary.append("="*50 + "\n")
        return '\n'.join(summary)


if __name__ == "__main__":
    # Test Bayesian belief system
    print("Testing Bayesian Belief System\n")
    
    belief_system = BayesianBeliefSystem(num_rooms=10)
    
    print("Initial beliefs (all rooms):")
    for room_id in range(10):
        print(f"Room {room_id}: P(trap) = {belief_system.get_trap_probability(room_id):.2f}")
        
    print("\n--- Agent enters Room 3 safely ---")
    belief_system.update_belief(3, "safe")
    print(belief_system.get_belief_summary())
    
    print("\n--- Agent triggers trap in Room 7 ---")
    belief_system.update_belief(7, "trap")
    print(belief_system.get_belief_summary())
    
    print("\n--- Agent enters Room 8 safely ---")
    belief_system.update_belief(8, "safe")
    print(belief_system.get_belief_summary())
