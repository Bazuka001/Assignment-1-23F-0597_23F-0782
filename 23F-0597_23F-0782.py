import tkinter as tk
from queue import Queue, PriorityQueue
import time


GRID_SIZE = 10   
CELL_SIZE = 50   
DELAY = 0.2    


COLOR_EMPTY = "white"
COLOR_WALL = "black"
COLOR_START = "green"
COLOR_TARGET = "red"
COLOR_FRONTIER = "yellow"
COLOR_EXPLORED = "blue"
COLOR_PATH = "orange"


DIRS = [(-1, 0), (0, 1), (1, 0), (1, 1), (0, -1), (-1, -1)]


grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
start = (0, 0)
target = (GRID_SIZE - 1, GRID_SIZE - 1)


for i in range(3, 7):
    grid[5][i] = 1

for i in range(5, 8):
    grid[i][7] = 1
    

class PathfinderGUI:
    def __init__(self, master):
        self.master = master
        master.title("")
        master.iconbitmap('')

        self.canvas = tk.Canvas(master, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE)
        self.canvas.pack()
        self.rects = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.draw_grid()

     
        frame = tk.Frame(master)
        frame.pack(pady=5)

        tk.Button(frame, text="BFS", command=lambda: self.run_search("BFS")).pack(side=tk.LEFT)
        tk.Button(frame, text="DFS", command=lambda: self.run_search("DFS")).pack(side=tk.LEFT)
        tk.Button(frame, text="UCS", command=lambda: self.run_search("UCS")).pack(side=tk.LEFT)
        tk.Button(frame, text="DLS", command=lambda: self.run_search("DLS")).pack(side=tk.LEFT)
        tk.Button(frame, text="IDDFS", command=lambda: self.run_search("IDDFS")).pack(side=tk.LEFT)
        tk.Button(frame, text="Bidirectional", command=lambda: self.run_search("Bidirectional")).pack(side=tk.LEFT)
        tk.Button(frame, text="Reset", command=self.reset_grid, bg="lightcoral").pack(side=tk.LEFT, padx=10)

        self.search_done = False  

    def draw_grid(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = COLOR_EMPTY
                if (r, c) == start:
                    color = COLOR_START
                elif (r, c) == target:
                    color = COLOR_TARGET
                elif grid[r][c] == 1:
                    color = COLOR_WALL
                self.rects[r][c] = self.canvas.create_rectangle(
                    c * CELL_SIZE, r * CELL_SIZE,
                    (c + 1) * CELL_SIZE, (r + 1) * CELL_SIZE,
                    fill=color, outline="gray"
                )

    def update_cell(self, pos, color):
        r, c = pos
        self.canvas.itemconfig(self.rects[r][c], fill=color)
        self.master.update()
        time.sleep(DELAY)

    def reset_grid(self):
        """Instantly clear all non-wall cells to empty."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r, c) == start:
                    color = COLOR_START
                elif (r, c) == target:
                    color = COLOR_TARGET
                elif grid[r][c] == 1:
                    color = COLOR_WALL
                else:
                    color = COLOR_EMPTY
                self.canvas.itemconfig(self.rects[r][c], fill=color)
        self.master.update()
        self.search_done = False  
    def run_search(self, algorithm):
        """Run selected algorithm; reset grid automatically between searches."""
        if self.search_done:
            self.reset_grid()

        if algorithm == "BFS":
            self.bfs()
        elif algorithm == "DFS":
            self.dfs()
        elif algorithm == "UCS":
            self.ucs()
        elif algorithm == "DLS":
            self.dls(limit=6)
        elif algorithm == "IDDFS":
            self.iddfs(max_depth=10)
        elif algorithm == "Bidirectional":
            self.bidirectional()

        self.search_done = True

    def bfs(self):
        frontier = Queue()
        frontier.put(start)
        came_from = {start: None}
        while not frontier.empty():
            current = frontier.get()
            if current == target:
                break
            self.update_cell(current, COLOR_EXPLORED)
            for dr, dc in DIRS:
                nr, nc = current[0] + dr, current[1] + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and grid[nr][nc] == 0:
                    neighbor = (nr, nc)
                    if neighbor not in came_from:
                        frontier.put(neighbor)
                        came_from[neighbor] = current
                        self.update_cell(neighbor, COLOR_FRONTIER)
        self.show_path(came_from)

    def dfs(self):
        stack = [start]
        came_from = {start: None}
        while stack:
            current = stack.pop()
            if current == target:
                break
            self.update_cell(current, COLOR_EXPLORED)
            for dr, dc in reversed(DIRS):  
                nr, nc = current[0] + dr, current[1] + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and grid[nr][nc] == 0:
                    neighbor = (nr, nc)
                    if neighbor not in came_from:
                        stack.append(neighbor)
                        came_from[neighbor] = current
                        self.update_cell(neighbor, COLOR_FRONTIER)
        self.show_path(came_from)

    def ucs(self):
        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        while not frontier.empty():
            _, current = frontier.get()
            if current == target:
                break
            self.update_cell(current, COLOR_EXPLORED)
            for dr, dc in DIRS:
                nr, nc = current[0] + dr, current[1] + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and grid[nr][nc] == 0:
                    neighbor = (nr, nc)
                    new_cost = cost_so_far[current] + 1
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        frontier.put((new_cost, neighbor))
                        came_from[neighbor] = current
                        self.update_cell(neighbor, COLOR_FRONTIER)
        self.show_path(came_from)

    def dls(self, limit):
        came_from = {start: None}

        def recursive_dls(node, depth):
            if depth > limit:
                return False
            self.update_cell(node, COLOR_EXPLORED)
            if node == target:
                return True
            for dr, dc in reversed(DIRS):
                nr, nc = node[0] + dr, node[1] + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and grid[nr][nc] == 0:
                    neighbor = (nr, nc)
                    if neighbor not in came_from:
                        came_from[neighbor] = node
                        self.update_cell(neighbor, COLOR_FRONTIER)
                        if recursive_dls(neighbor, depth + 1):
                            return True
            return False

        recursive_dls(start, 0)
        self.show_path(came_from)

    def iddfs(self, max_depth):
        for depth in range(max_depth):
            came_from = {start: None}

            def recursive_dls(node, depth_left):
                if depth_left < 0:
                    return False
                self.update_cell(node, COLOR_EXPLORED)
                if node == target:
                    return True
                for dr, dc in reversed(DIRS):
                    nr, nc = node[0] + dr, node[1] + dc
                    if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and grid[nr][nc] == 0:
                        neighbor = (nr, nc)
                        if neighbor not in came_from:
                            came_from[neighbor] = node
                            self.update_cell(neighbor, COLOR_FRONTIER)
                            if recursive_dls(neighbor, depth_left - 1):
                                return True
                return False

            found = recursive_dls(start, depth)
            if found:
                self.show_path(came_from)
                return

    def bidirectional(self):
        frontier_f = Queue()
        frontier_b = Queue()
        frontier_f.put(start)
        frontier_b.put(target)
        came_from_f = {start: None}
        came_from_b = {target: None}
        meet = None

        while not frontier_f.empty() and not frontier_b.empty():
            current_f = frontier_f.get()
            self.update_cell(current_f, COLOR_EXPLORED)
            for dr, dc in DIRS:
                nr, nc = current_f[0] + dr, current_f[1] + dc
                neighbor = (nr, nc)
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and grid[nr][nc] == 0:
                    if neighbor not in came_from_f:
                        came_from_f[neighbor] = current_f
                        frontier_f.put(neighbor)
                        self.update_cell(neighbor, COLOR_FRONTIER)
                        if neighbor in came_from_b:
                            meet = neighbor
                            break
            if meet:
                break

            current_b = frontier_b.get()
            self.update_cell(current_b, COLOR_EXPLORED)
            for dr, dc in DIRS:
                nr, nc = current_b[0] + dr, current_b[1] + dc
                neighbor = (nr, nc)
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and grid[nr][nc] == 0:
                    if neighbor not in came_from_b:
                        came_from_b[neighbor] = current_b
                        frontier_b.put(neighbor)
                        self.update_cell(neighbor, COLOR_FRONTIER)
                        if neighbor in came_from_f:
                            meet = neighbor
                            break
            if meet:
                break

        if meet:
            path = []
            node = meet
            while node:
                path.append(node)
                node = came_from_f[node]
            path = path[::-1]
            node = came_from_b[meet]
            while node:
                path.append(node)
                node = came_from_b[node]
            for p in path:
                if p != start and p != target:
                    self.update_cell(p, COLOR_PATH)

    def show_path(self, came_from):
        node = target
        while node and node != start:
            self.update_cell(node, COLOR_PATH)
            node = came_from.get(node)


root = tk.Tk()
app = PathfinderGUI(root)
root.mainloop()