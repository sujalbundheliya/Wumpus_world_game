# logic.py
import random
from collections import deque

# ------------------- Cell Class -------------------
class Cell:
    def __init__(self):
        # Each cell can contain a pit, a wumpus, or gold.
        self.has_pit = False
        self.has_wumpus = False
        self.has_gold = False

# ------------------- WumpusWorld Class -------------------
class WumpusWorld:
    def __init__(self, size=20, pit_prob=0.2):
        """
        Create a grid with the following elements:
        - 15 Wumpuses
        - 20 pits
        - 1 gold (placed only in cells without a pit or live wumpus)
        
        A safe zone is enforced around (0,0), and the board is regenerated 
        until a safe path from (0,0) to the gold exists.
        """
        self.size = size
        self.grid = [[Cell() for _ in range(size)] for _ in range(size)]
        attempts = 0
        # Try generating a board up to 100 times until it's winnable.
        while attempts < 100:
            self.place_elements()
            if self.is_winnable():
                break
            attempts += 1
        if attempts >= 100:
            raise Exception("Could not generate a winnable board after 100 attempts.")
    
    def place_elements(self):
        # Reset grid by reinitializing each cell.
        for x in range(self.size):
            for y in range(self.size):
                self.grid[x][y] = Cell()
        
        # Define a safe starting zone around (0,0)
        safe_zone = {(0, 0), (0, 1), (1, 0), (1, 1)}
        all_positions = [(x, y) for x in range(self.size) for y in range(self.size)]
        available_positions = [pos for pos in all_positions if pos not in safe_zone]
        
        # Place 15 distinct Wumpuses in random positions.
        wumpus_positions = random.sample(available_positions, 15)
        for (x, y) in wumpus_positions:
            self.grid[x][y].has_wumpus = True
        available_positions = [pos for pos in available_positions if pos not in wumpus_positions]
        
        # Place 20 distinct pits.
        pit_positions = random.sample(available_positions, 20)
        for (x, y) in pit_positions:
            self.grid[x][y].has_pit = True
        available_positions = [pos for pos in available_positions if pos not in pit_positions]
        
        # Place gold in one cell that is free of pits and wumpuses.
        gold_pos = random.choice(available_positions)
        self.grid[gold_pos[0]][gold_pos[1]].has_gold = True

    def is_winnable(self):
        # Find the position of the gold.
        gold_pos = None
        for x in range(self.size):
            for y in range(self.size):
                if self.grid[x][y].has_gold:
                    gold_pos = (x, y)
                    break
            if gold_pos is not None:
                break
        if not gold_pos:
            return False
        
        # Ensure starting cell is safe.
        if self.grid[0][0].has_pit or self.grid[0][0].has_wumpus:
            return False
        
        # Use BFS to determine if a safe path exists from (0,0) to the gold.
        visited = set()
        queue = [(0, 0)]
        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) == gold_pos:
                return True
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if (nx, ny) not in visited:
                        if not self.grid[nx][ny].has_pit and not self.grid[nx][ny].has_wumpus:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
        return False

    def get_percepts(self, x, y):
        """
        Return a list of percepts for the cell (x,y).
        - 'glitter' if the cell has gold.
        - 'breeze' if any neighbor has a pit.
        - 'stench' if any neighbor has a wumpus.
        """
        percepts = []
        if self.grid[x][y].has_gold:
            percepts.append("glitter")
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        # Check for adjacent pits.
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if self.grid[nx][ny].has_pit:
                    percepts.append("breeze")
                    break
        # Check for adjacent wumpuses.
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if self.grid[nx][ny].has_wumpus:
                    percepts.append("stench")
                    break
        return percepts

    def shoot_arrow(self, x, y, orientation):
        """
        Shoot an arrow from (x, y) in the specified orientation.
        If a wumpus is hit, it is removed and the method returns True.
        """
        dx, dy = 0, 0
        if orientation == 'N':
            dx, dy = 0, 1
        elif orientation == 'S':
            dx, dy = 0, -1
        elif orientation == 'E':
            dx, dy = 1, 0
        elif orientation == 'W':
            dx, dy = -1, 0
        cx, cy = x, y
        # Move arrow step by step until it leaves the grid.
        while True:
            cx += dx
            cy += dy
            if not (0 <= cx < self.size and 0 <= cy < self.size):
                break
            if self.grid[cx][cy].has_wumpus:
                self.grid[cx][cy].has_wumpus = False
                return True, (cx, cy)
        return False, None

    def count_wumpuses(self):
        # Count all remaining wumpuses.
        return sum(cell.has_wumpus for row in self.grid for cell in row)

    def count_pits(self):
        # Count all pits.
        return sum(cell.has_pit for row in self.grid for cell in row)

# ------------------- Agent Class -------------------
class Agent:
    def __init__(self):
        # Initialize starting position and orientation.
        self.x = 0
        self.y = 0
        self.orientation = 'E'
        self.has_gold = False
        self.arrows = 15
        self.alive = True

    def turn_left(self):
        # Turn left based on current orientation.
        mapping = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}
        self.orientation = mapping[self.orientation]

    def turn_right(self):
        # Turn right based on current orientation.
        mapping = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
        self.orientation = mapping[self.orientation]

    def move_forward(self, world):
        # Calculate new position based on current orientation.
        dx, dy = 0, 0
        if self.orientation == 'N':
            dx, dy = 0, 1
        elif self.orientation == 'S':
            dx, dy = 0, -1
        elif self.orientation == 'E':
            dx, dy = 1, 0
        elif self.orientation == 'W':
            dx, dy = -1, 0
        new_x = self.x + dx
        new_y = self.y + dy
        # Ensure the new position is within bounds.
        if 0 <= new_x < world.size and 0 <= new_y < world.size:
            self.x, self.y = new_x, new_y
            return False  # Successfully moved.
        else:
            return True   # Bumped into a wall.

# ------------------- WumpusGame Class -------------------
class WumpusGame:
    def __init__(self, size=20, pit_prob=0.2):
        # Create the game world and the agent.
        self.world = WumpusWorld(size, pit_prob)
        self.agent = Agent()
        self.game_over = False
        self.win = False
