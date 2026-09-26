import config

# Cardinal directions in clockwise order
DIRS = ['N', 'E', 'S', 'W']

class MineMapper:
    def __init__(self):
        self.grid_size = config.GRID_SIZE
        # Cell state: 0=unexplored, 1=safe, 2=hazardous, 3=blocked
        self.map_grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.rover_pos = [0, 0]  # [x, y], origin at bottom-left
        self.facing = 'N'        # Start facing North
        
    def move_forward(self):
        x, y = self.rover_pos
        if self.facing == 'N' and y < self.grid_size - 1:
            y += 1
        elif self.facing == 'S' and y > 0:
            y -= 1
        elif self.facing == 'E' and x < self.grid_size - 1:
            x += 1
        elif self.facing == 'W' and x > 0:
            x -= 1
        self.rover_pos = [x, y]
        
    def turn_right(self):
        """Clockwise 90 degrees: N->E->S->W->N"""
        idx = DIRS.index(self.facing)
        self.facing = DIRS[(idx + 1) % 4]
        
    def turn_left(self):
        """Counter-clockwise 90 degrees: N->W->S->E->N"""
        idx = DIRS.index(self.facing)
        self.facing = DIRS[(idx - 1) % 4]
        
    def mark_section(self, pos, status):
        x, y = pos[0], pos[1]
        val_map = {'safe': 1, 'hazardous': 2, 'blocked': 3}
        self.map_grid[y][x] = val_map.get(status, 0)
        
    def get_current_location(self):
        return list(self.rover_pos)  # Return a copy to prevent external mutation
        
    def get_map_state(self):
        return {
            'grid': self.map_grid,
            'rover_pos': self.rover_pos,
            'facing': self.facing
        }
