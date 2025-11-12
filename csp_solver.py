"""
Constraint Satisfaction Problem (CSP) solver for door puzzles
"""

import random
from typing import List, Dict, Set, Tuple, Optional, Callable


class CSPPuzzle:
    """Represents a CSP puzzle for unlocking doors"""
    
    def __init__(self, difficulty: str = "easy"):
        self.difficulty = difficulty
        self.variables: List[str] = []
        self.domains: Dict[str, List[int]] = {}
        self.constraints: List[Callable] = []
        self.solution: Dict[str, int] = {}
        self.description = ""
        
        self._generate_puzzle()
        
    def _generate_puzzle(self):
        """Generate a puzzle based on difficulty"""
        if self.difficulty == "easy":
            self._generate_easy_puzzle()
        elif self.difficulty == "medium":
            self._generate_medium_puzzle()
        elif self.difficulty == "hard":
            self._generate_hard_puzzle()
        else:
            self._generate_easy_puzzle()
            
    def _generate_easy_puzzle(self):
        """Generate an easy 2-variable puzzle"""
        self.variables = ["X", "Y"]
        self.domains = {
            "X": [1, 2, 3, 4],
            "Y": [1, 2, 3, 4]
        }
        
        # Generate solution
        target_sum = random.randint(4, 7)
        
        # Constraints
        def constraint_sum(assignment):
            if "X" in assignment and "Y" in assignment:
                return assignment["X"] + assignment["Y"] == target_sum
            return True
            
        def constraint_different(assignment):
            if "X" in assignment and "Y" in assignment:
                return assignment["X"] != assignment["Y"]
            return True
            
        self.constraints = [constraint_sum, constraint_different]
        self.description = f"[EASY PUZZLE] Find X and Y where:\n  - X + Y = {target_sum}\n  - X ≠ Y\n  - Both are between 1-4"
        
    def _generate_medium_puzzle(self):
        """Generate a medium 3-variable puzzle"""
        self.variables = ["A", "B", "C"]
        self.domains = {
            "A": [1, 2, 3, 4, 5],
            "B": [1, 2, 3, 4, 5],
            "C": [1, 2, 3, 4, 5]
        }
        
        target_sum = random.randint(8, 12)
        
        def constraint_sum(assignment):
            if all(v in assignment for v in ["A", "B", "C"]):
                return assignment["A"] + assignment["B"] + assignment["C"] == target_sum
            return True
            
        def constraint_all_different(assignment):
            assigned = [assignment[v] for v in assignment]
            return len(assigned) == len(set(assigned))
            
        def constraint_order(assignment):
            if "A" in assignment and "B" in assignment:
                return assignment["A"] < assignment["B"]
            return True
            
        self.constraints = [constraint_sum, constraint_all_different, constraint_order]
        self.description = f"[MEDIUM PUZZLE] Find A, B, C where:\n  - A + B + C = {target_sum}\n  - All different values\n  - A < B\n  - Each is between 1-5"
        
    def _generate_hard_puzzle(self):
        """Generate a hard 4-variable puzzle"""
        self.variables = ["W", "X", "Y", "Z"]
        self.domains = {
            "W": [1, 2, 3, 4, 5, 6],
            "X": [1, 2, 3, 4, 5, 6],
            "Y": [1, 2, 3, 4, 5, 6],
            "Z": [1, 2, 3, 4, 5, 6]
        }
        
        # Generate a valid solution first to ensure solvability
        # Valid combinations: W*X products and Y+Z sums
        valid_combinations = [
            (2, 6, 1, 5, 12, 6),  # W=2, X=6, Y=1, Z=5: 2*6=12, 1+5=6
            (3, 4, 1, 5, 12, 6),  # W=3, X=4, Y=1, Z=5: 3*4=12, 1+5=6
            (2, 5, 1, 6, 10, 7),  # W=2, X=5, Y=1, Z=6: 2*5=10, 1+6=7
            (3, 5, 1, 4, 15, 5),  # W=3, X=5, Y=1, Z=4: 3*5=15, 1+4=5
            (4, 5, 1, 3, 20, 4),  # W=4, X=5, Y=1, Z=3: 4*5=20, 1+3=4
        ]
        
        w_val, x_val, y_val, z_val, target_product, target_sum = random.choice(valid_combinations)
        
        def constraint_product_sum(assignment):
            if all(v in assignment for v in ["W", "X", "Y", "Z"]):
                return assignment["W"] * assignment["X"] == target_product and \
                       assignment["Y"] + assignment["Z"] == target_sum
            return True
            
        def constraint_all_different(assignment):
            assigned = [assignment[v] for v in assignment]
            return len(assigned) == len(set(assigned))
            
        def constraint_ordering(assignment):
            if "W" in assignment and "X" in assignment:
                return assignment["W"] <= assignment["X"]
            return True
            
        self.constraints = [constraint_product_sum, constraint_all_different, constraint_ordering]
        self.description = f"[HARD PUZZLE] Find W, X, Y, Z where:\n  - W × X = {target_product}\n  - Y + Z = {target_sum}\n  - All different values\n  - W ≤ X\n  - Each is between 1-6"


class CSPSolver:
    """Backtracking CSP solver with constraint propagation"""
    
    def __init__(self, puzzle: CSPPuzzle):
        self.puzzle = puzzle
        self.backtracks = 0
        self.nodes_expanded = 0
        
    def solve(self) -> Optional[Dict[str, int]]:
        """Solve the CSP using backtracking"""
        self.backtracks = 0
        self.nodes_expanded = 0
        assignment = {}
        result = self._backtrack(assignment)
        return result
        
    def _backtrack(self, assignment: Dict[str, int]) -> Optional[Dict[str, int]]:
        """Recursive backtracking with forward checking"""
        self.nodes_expanded += 1
        
        # Check if assignment is complete
        if len(assignment) == len(self.puzzle.variables):
            if self._is_consistent(assignment):
                return assignment
            return None
            
        # Select unassigned variable (using MRV heuristic)
        var = self._select_unassigned_variable(assignment)
        
        # Try each value in domain
        for value in self.puzzle.domains[var]:
            assignment[var] = value
            
            # Check if consistent
            if self._is_consistent(assignment):
                result = self._backtrack(assignment)
                if result is not None:
                    return result
                    
            # Backtrack
            self.backtracks += 1
            del assignment[var]
            
        return None
        
    def _select_unassigned_variable(self, assignment: Dict[str, int]) -> str:
        """Select next variable using Minimum Remaining Values (MRV) heuristic"""
        unassigned = [v for v in self.puzzle.variables if v not in assignment]
        
        # For simplicity, return first unassigned
        # Could implement MRV by counting valid values
        return unassigned[0] if unassigned else None
        
    def _is_consistent(self, assignment: Dict[str, int]) -> bool:
        """Check if current assignment satisfies all constraints"""
        for constraint in self.puzzle.constraints:
            if not constraint(assignment):
                return False
        return True
        
    def verify_solution(self, user_solution: Dict[str, int]) -> bool:
        """Verify if a user-provided solution is correct"""
        if set(user_solution.keys()) != set(self.puzzle.variables):
            return False
            
        # Check all values are in domains
        for var, value in user_solution.items():
            if value not in self.puzzle.domains[var]:
                return False
                
        # Check all constraints
        return self._is_consistent(user_solution)


def generate_puzzle(difficulty: str) -> CSPPuzzle:
    """Generate a new puzzle of specified difficulty"""
    return CSPPuzzle(difficulty)


if __name__ == "__main__":
    # Test the CSP solver
    print("Testing CSP Puzzle Solver\n")
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\n{difficulty.upper()} Puzzle:")
        puzzle = generate_puzzle(difficulty)
        print(puzzle.description)
        
        solver = CSPSolver(puzzle)
        solution = solver.solve()
        
        if solution:
            print(f"Solution found: {solution}")
            print(f"Nodes expanded: {solver.nodes_expanded}, Backtracks: {solver.backtracks}")
        else:
            print("No solution found!")
