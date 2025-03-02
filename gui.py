# gui.py
import tkinter as tk
from tkinter import messagebox
from collections import deque
from logic import WumpusGame
import pickle
import matplotlib.pyplot as plt
import time

class WumpusGameGUI_Auto:
    def __init__(self, master, size=20, pit_prob=0.2):
        self.master = master
        self.master.title("Wumpus World - Enhanced Agent")
        self.master.geometry("1920x1800")
        self.master.configure(bg="white")
        
        self.game = WumpusGame(size, pit_prob)
        self.score = 0
        self.size = size
        self.cell_width = 50.8
        self.cell_height = 37
        
        # Tracking visited, safe cells, stench cells, etc.
        self.visited = {(self.game.agent.x, self.game.agent.y)}
        self.safe_set = {(self.game.agent.x, self.game.agent.y)}
        self.visited_percepts = {}
        self.stench_cells = set()
        
        # Knowledge dictionary
        self.knowledge = {
            (x, y): {'pit': 0.5, 'wumpus': 0.5}
            for x in range(self.size)
            for y in range(self.size)
        }
        self.knowledge[(0, 0)]['pit'] = 0
        self.knowledge[(0, 0)]['wumpus'] = 0
        
        self.action_delay = 5  # ms delay for auto-run steps
        
        # Iteration mode variables
        self.iteration_mode = False
        self.iterations_to_run = 0
        self.current_iteration = 0
        self.iteration_scores = []
        self.iteration_wins = []
        self.iteration_outcomes = []
        self.iteration_times = []
        self.start_time = None
        
        self.build_gui()
        self.draw_grid()
        self.update_status()
        self.update_visited_display()
        self.bind_keys()
    
    # ------------------- GUI Setup -------------------
    def build_gui(self):
        # Left panel
        self.left_frame = tk.Frame(self.master, relief=tk.RIDGE, borderwidth=2,
                                   padx=10, pady=10, bg="white")
        self.left_frame.grid(row=0, column=0, sticky="n", padx=10, pady=10)

        self.score_label = tk.Label(self.left_frame, text=f"Score: {self.score}",
                                    font=("Arial", 10), bg="white")
        self.score_label.pack(anchor="w")
        self.pos_label = tk.Label(self.left_frame,
                                  text=f"Pos: {self.game.agent.x, self.game.agent.y}",
                                  font=("Arial", 10), bg="white")
        self.pos_label.pack(anchor="w")
        self.ori_label = tk.Label(self.left_frame,
                                  text=f"Ori: {self.game.agent.orientation}",
                                  font=("Arial", 10), bg="white")
        self.ori_label.pack(anchor="w")
        self.arrow_label = tk.Label(self.left_frame,
                                    text=f"Arrows: {self.game.agent.arrows}",
                                    font=("Arial", 10), bg="white")
        self.arrow_label.pack(anchor="w")
        self.gold_label = tk.Label(self.left_frame,
                                   text=f"Gold: {'Yes' if self.game.agent.has_gold else 'No'}",
                                   font=("Arial", 10), bg="white")
        self.gold_label.pack(anchor="w")
        self.wumpus_label = tk.Label(self.left_frame,
                                     text=f"Wumpuses: {self.game.world.count_wumpuses()}",
                                     font=("Arial", 10), bg="white")
        self.wumpus_label.pack(anchor="w")
        self.pit_label = tk.Label(self.left_frame,
                                  text=f"Pits: {self.game.world.count_pits()}",
                                  font=("Arial", 10), bg="white")
        self.pit_label.pack(anchor="w")
        
        instr_text = (
            "Instructions:\n"
            "Arrow Keys = Turn/Move\n"
            "Space = Shoot\n"
            "Enter = Grab\n"
            "(Press arrow once to turn; \npress again to move.)"
        )
        self.instr_label = tk.Label(self.left_frame, text=instr_text,
                                    font=("Arial", 10), justify="left", bg="white")
        self.instr_label.pack(anchor="w", pady=(10, 0))
        
        # Center panel (canvas)
        self.canvas = tk.Canvas(self.master,
                                width=self.cell_width*self.size,
                                height=self.cell_height*self.size,
                                bg="white")
        self.canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        
        # Right panel
        self.right_frame = tk.Frame(self.master, relief=tk.RIDGE, borderwidth=2,
                                    bg="white")
        self.right_frame.grid(row=0, column=2, sticky="n", padx=10, pady=10)

        self.visited_label = tk.Label(self.right_frame, text="Visited Cells",
                                      font=("Arial", 10), bg="white")
        self.visited_label.pack(pady=(5, 0))
        self.visited_listbox = tk.Listbox(self.right_frame, width=40, height=20)
        self.visited_listbox.pack(side="top", fill="both", expand=True,
                                  padx=5, pady=5)
        self.visited_scrollbar = tk.Scrollbar(self.right_frame, orient="vertical")
        self.visited_scrollbar.config(command=self.visited_listbox.yview)
        self.visited_listbox.config(yscrollcommand=self.visited_scrollbar.set)
        self.visited_scrollbar.pack(side="right", fill="y")

        # Iteration progress label
        self.iteration_progress_label = tk.Label(self.right_frame, text="",
                                                 font=("Arial", 12), bg="white",
                                                 fg="blue")
        self.iteration_progress_label.pack(pady=(5,5))
        
        # Control buttons
        self.right_button_frame = tk.Frame(self.right_frame, bg="white")
        self.right_button_frame.pack(side="bottom", fill="x", pady=10)
        self.automate_button = tk.Button(self.right_button_frame,
                                         text="Automate", font=("Arial", 12),
                                         command=self.start_automation)
        self.automate_button.pack(side="top", pady=5)
        self.exit_button = tk.Button(self.right_button_frame,
                                     text="Exit", font=("Arial", 12),
                                     command=self.exit_game)
        self.exit_button.pack(side="top", pady=5)
        self.restart_button = tk.Button(self.right_button_frame,
                                        text="Restart", font=("Arial", 12),
                                        command=self.restart_game)
        self.restart_button.pack(side="top", pady=5)
        self.iter_label = tk.Label(self.right_button_frame,
                                   text="Iterations:", font=("Arial", 10),
                                   bg="white")
        self.iter_label.pack(side="top", pady=2)
        self.iter_entry = tk.Entry(self.right_button_frame, font=("Arial", 10))
        self.iter_entry.pack(side="top", pady=2)
        self.run_iterations_btn = tk.Button(self.right_button_frame,
                                            text="Run Iterations",
                                            font=("Arial", 12),
                                            command=self.run_iterations)
        self.run_iterations_btn.pack(side="top", pady=5)
        
        self.message_label = tk.Label(self.master, text="",
                                      font=("Arial", 10), bg="white")
        self.message_label.grid(row=3, column=0, columnspan=3, pady=5)

    def bind_keys(self):
        """Bind keys for manual movement/shoot/grab in a two-step orientation + move style."""
        self.master.bind("<Left>", lambda event: self.handle_move('W'))
        self.master.bind("<Right>", lambda event: self.handle_move('E'))
        self.master.bind("<Up>", lambda event: self.handle_move('N'))
        self.master.bind("<Down>", lambda event: self.handle_move('S'))
        self.master.bind("<space>", lambda event: self.handle_shoot())
        self.master.bind("<Return>", lambda event: self.handle_grab())
    
    # ------------------- Manual Movement: Two-step Approach -------------------
    def handle_move(self, direction):
        """
        If the agent is not already facing 'direction', just rotate (orientation).
        Otherwise, move forward manually.
        """
        if self.game.game_over:
            return
        if self.game.agent.orientation != direction:
            # Step 1: Rotate to face that direction
            self.game.agent.orientation = direction
            self.update_status()
            self.draw_grid()
        else:
            # Step 2: Actually move forward manually
            self.move_manual()

    def move_manual(self):
        """Manual forward movement (similar to 4×4 reference)."""
        if self.game.game_over:
            return
        bump = self.game.agent.move_forward(self.game.world)
        self.score -= 1
        if bump:
            self.display_message("Bumped into a wall!", "orange")
        else:
            current = (self.game.agent.x, self.game.agent.y)
            self.visited.add(current)
            self.record_percepts(*current)
            self.update_visited_display()

            if self.check_for_hazard():
                self.update_status()
                self.draw_grid()
                return

            self.display_message("Moved successfully.", "black")
        self.update_status()
        self.draw_grid()
        self.check_win_condition()

    def handle_shoot(self):
        if self.game.game_over:
            return
        self.shoot()

    def handle_grab(self):
        if self.game.game_over:
            return
        self.grab()

    # ------------------- Utility / Display Methods -------------------
    def display_message(self, text, color="black"):
        self.message_label.config(text=text, fg=color)

    def update_status(self):
        self.score_label.config(text=f"Score: {self.score}")
        self.pos_label.config(text=f"Pos: {(self.game.agent.x, self.game.agent.y)}")
        self.ori_label.config(text=f"Ori: {self.game.agent.orientation}")
        self.arrow_label.config(text=f"Arrows: {self.game.agent.arrows}")
        self.gold_label.config(text=f"Gold: {'Yes' if self.game.agent.has_gold else 'No'}")
        self.wumpus_label.config(text=f"Wumpuses: {self.game.world.count_wumpuses()}")
        self.pit_label.config(text=f"Pits: {self.game.world.count_pits()}")
        if self.iteration_mode:
            remaining = self.iterations_to_run - self.current_iteration
            self.iteration_progress_label.config(text=f"Iterations Remaining: {remaining}")
        else:
            self.iteration_progress_label.config(text="")

    def draw_grid(self):
        self.canvas.delete("all")
        for x in range(self.size):
            for y in range(self.size):
                cx0 = x * self.cell_width
                cy0 = (self.size - 1 - y) * self.cell_height
                cx1 = (x + 1) * self.cell_width
                cy1 = (self.size - y) * self.cell_height

                # Color the cell if visited
                if (x, y) in self.visited:
                    percepts = self.visited_percepts.get((x, y), [])
                    if "glitter" in percepts:
                        fill_color = "yellow"
                    elif "breeze" in percepts:
                        fill_color = "light blue"
                    elif "stench" in percepts:
                        fill_color = "light coral"
                    else:
                        fill_color = "light green"
                else:
                    fill_color = "white"

                self.canvas.create_rectangle(cx0, cy0, cx1, cy1,
                                             fill=fill_color, outline="black")

                # Optionally display the percept text if visited
                if (x, y) in self.visited_percepts:
                    ptext = self.visited_percepts[(x, y)]
                    if ptext:
                        label_strs = ", ".join(ptext)
                    else:
                        label_strs = "empty"
                    self.canvas.create_text(cx0 + self.cell_width/2,
                                            cy1 - 10,
                                            text=label_strs,
                                            fill="black",
                                            font=("Arial", 10, "bold"))
        # Draw the agent arrow
        ax, ay = self.game.agent.x, self.game.agent.y
        center_x = ax * self.cell_width + self.cell_width/2
        center_y = (self.size - 1 - ay) * self.cell_height + self.cell_height/2
        arrow_len = self.cell_width/3

        if self.game.agent.orientation == 'N':
            dx, dy = 0, -arrow_len
        elif self.game.agent.orientation == 'S':
            dx, dy = 0, arrow_len
        elif self.game.agent.orientation == 'E':
            dx, dy = arrow_len, 0
        else:  # 'W'
            dx, dy = -arrow_len, 0

        self.canvas.create_line(center_x, center_y,
                                center_x + dx, center_y + dy,
                                arrow=tk.LAST, fill="blue", width=2)
        self.canvas.update()

    def update_visited_display(self):
        self.visited_listbox.delete(0, tk.END)
        for cell in sorted(self.visited, reverse=True):
            per = self.visited_percepts.get(cell, [])
            entry = f"{cell}: {', '.join(per) if per else 'empty'}"
            self.visited_listbox.insert(tk.END, entry)

    # ------------------- Knowledge / Inference Logic -------------------
    def record_percepts(self, x, y):
        per = self.game.world.get_percepts(x, y)
        self.visited_percepts[(x, y)] = per
        if "stench" in per:
            self.stench_cells.add((x, y))

    def update_knowledge(self):
        changed = True
        while changed:
            changed = False
            for (vx, vy) in self.visited:
                per = self.visited_percepts.get((vx, vy), [])
                neighbors = self.get_neighbors((vx, vy))

                # If no stench, mark neighbors as safe from wumpus
                if "stench" not in per:
                    for n in neighbors:
                        if self.knowledge[n]['wumpus'] != 0:
                            self.knowledge[n]['wumpus'] = 0
                            changed = True
                else:
                    # If exactly one unknown neighbor, that might be a wumpus
                    uncertain = [n for n in neighbors if self.knowledge[n]['wumpus'] == 0.5]
                    if len(uncertain) == 1:
                        wn = uncertain[0]
                        if self.knowledge[wn]['wumpus'] != 1:
                            self.knowledge[wn]['wumpus'] = 1
                            changed = True

                # If no breeze, mark neighbors as safe from pit
                if "breeze" not in per:
                    for n in neighbors:
                        if self.knowledge[n]['pit'] != 0:
                            self.knowledge[n]['pit'] = 0
                            changed = True
                else:
                    # If exactly one unknown neighbor, that might be a pit
                    uncertain = [n for n in neighbors if self.knowledge[n]['pit'] == 0.5]
                    if len(uncertain) == 1:
                        pn = uncertain[0]
                        if self.knowledge[pn]['pit'] != 1:
                            self.knowledge[pn]['pit'] = 1
                            changed = True

            # If a cell is known safe, add to self.safe_set
            for cell, info in self.knowledge.items():
                if info['pit'] == 0 and info['wumpus'] == 0 and cell not in self.safe_set:
                    self.safe_set.add(cell)
                    changed = True

    def get_neighbors(self, pos):
        x, y = pos
        nbrs = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                nbrs.append((nx, ny))
        return nbrs

    def vantage_spots(self, wx, wy):
        vantage = []
        for vx in range(self.size):
            vantage.append((vx, wy))
        for vy in range(self.size):
            vantage.append((wx, vy))
        return list(set(vantage))

    def find_path_to_any(self, start, candidates):
        from collections import deque
        queue = deque([[start]])
        visited = {start}
        while queue:
            path = queue.popleft()
            if path[-1] in candidates:
                return path
            for nb in self.get_neighbors(path[-1]):
                if nb not in visited:
                    if self.knowledge[nb]['pit'] == 0 and self.knowledge[nb]['wumpus'] == 0:
                        visited.add(nb)
                        queue.append(path + [nb])
        return None

    def find_path_knowledge(self, start, goals):
        from collections import deque
        queue = deque([[start]])
        visited = {start}
        while queue:
            path = queue.popleft()
            if path[-1] in goals:
                return path
            for neighbor in self.get_neighbors(path[-1]):
                if neighbor not in visited:
                    if (self.knowledge[neighbor]['pit'] == 0 and
                        self.knowledge[neighbor]['wumpus'] == 0):
                        visited.add(neighbor)
                        queue.append(path + [neighbor])
        return None

    def find_path_ground_truth(self, start, goal):
        from collections import deque
        visited = {start}
        queue = deque([[start]])
        while queue:
            path = queue.popleft()
            if path[-1] == goal:
                return path
            for neighbor in self.get_neighbors(path[-1]):
                if neighbor not in visited:
                    cell = self.game.world.grid[neighbor[0]][neighbor[1]]
                    if not cell.has_pit and not cell.has_wumpus:
                        visited.add(neighbor)
                        queue.append(path + [neighbor])
        return None

    # ------------------- Iteration Mode Functions -------------------
    def run_iterations(self):
        try:
            iters = int(self.iter_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of iterations.")
            return
        self.iterations_to_run = iters
        self.current_iteration = 0
        self.iteration_scores = []
        self.iteration_wins = []
        self.iteration_outcomes = []
        self.iteration_times = []
        self.iteration_mode = True
        self.start_time = time.time()
        self.restart_game()
        self.auto_run()

    def iteration_finished(self):
        win = (self.game.agent.has_gold and
               (self.game.world.count_wumpuses() == 0))
        self.iteration_scores.append(self.score)
        self.iteration_wins.append(win)
        outcome = "win" if win else "loose"
        self.iteration_outcomes.append(f"itr-{self.current_iteration + 1}: {outcome}")
        iter_time = time.time() - self.start_time
        self.iteration_times.append(iter_time)
        self.current_iteration += 1

        if self.current_iteration < self.iterations_to_run:
            self.restart_game()
            self.start_time = time.time()
            self.master.after(500, self.auto_run)
        else:
            avg = sum(self.iteration_scores) / len(self.iteration_scores)
            wr = sum(1 for w in self.iteration_wins if w) / len(self.iteration_wins) * 100
            details = "\n".join(self.iteration_outcomes)

            # Bar chart
            win_count = sum(1 for outcome in self.iteration_outcomes
                            if "win" in outcome.lower())
            loss_count = self.iterations_to_run - win_count
            outcomes = ["Wins", "Losses"]
            counts = [win_count, loss_count]
            plt.figure(figsize=(6, 4), dpi=300)
            bars = plt.bar(outcomes, counts, color=["green", "red"])
            plt.title(f"Iteration Outcomes ({self.iterations_to_run} Iterations)",
                      fontsize=18)
            plt.xlabel("Outcome", fontsize=16)
            plt.ylabel("Count", fontsize=16)
            plt.ylim(0, max(counts) + 1)
            for bar, cnt in zip(bars, counts):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{cnt}',
                         ha='center', va='bottom', fontsize=14)
            plt.tight_layout()
            plt.savefig("Results\Graphs\iteration_result.png", dpi=300)
            plt.close()

            # Scatter plot for iteration times
            iterations = list(range(1, self.iterations_to_run + 1))
            plt.figure(figsize=(6, 4), dpi=300)
            plt.scatter(iterations, self.iteration_times, color="blue")
            plt.plot(iterations, self.iteration_times, linestyle="--", color="blue")
            plt.title(f"Iteration Time per Iteration ({self.iterations_to_run} Iterations)",
                      fontsize=18)
            plt.xlabel("Iteration Number", fontsize=16)
            plt.ylabel("Time (seconds)", fontsize=16)
            plt.tight_layout()
            plt.savefig("Results\Timing\iteration_times.png", dpi=300)
            plt.close()

            messagebox.showinfo("Iteration Results",
                f"Iterations: {self.iterations_to_run}\n"
                f"Average Score: {avg:.2f}\nWin Rate: {wr:.2f}%\n\nDetails:\n{details}")
            
            results = {
                "iterations": self.iterations_to_run,
                "win_rate": wr,
                "avg_score": avg,
                "outcomes": self.iteration_outcomes,
                "iteration_times": self.iteration_times
            }
            with open("iteration_results.pkl", "wb") as f:
                pickle.dump(results, f)
            self.iteration_mode = False

    def auto_run(self):
        """Auto-run loop for AI moves."""
        if self.game.game_over:
            if self.iteration_mode:
                self.iteration_finished()
            return
        self.update_knowledge()
        decision, param = self.choose_next_move()
        if decision == "wait":
            self.display_message("No safe moves - waiting... Loss.", "orange")
            self.game.game_over = True
            if self.iteration_mode:
                self.iteration_finished()
            return
        self.execute_action(decision, param)

        ax, ay = self.game.agent.x, self.game.agent.y
        self.visited.add((ax, ay))
        self.record_percepts(ax, ay)
        if decision == "shoot" and not self.game.world.count_wumpuses():
            # Re-record stench for all visited cells if all wumpuses are dead
            for cell in self.visited:
                self.record_percepts(cell[0], cell[1])

        self.update_status()
        self.draw_grid()
        self.update_visited_display()
        self.master.after(self.action_delay, self.auto_run)

    def start_automation(self):
        """Start auto-run after a short delay."""
        self.master.after(self.action_delay, self.auto_run)

    # ------------------- Decision Logic for Auto Mode -------------------
    def choose_next_move(self):
        agent = self.game.agent
        current = (agent.x, agent.y)
        wcount = self.game.world.count_wumpuses()

        # If agent has gold and no wumpuses => go home
        if agent.has_gold and wcount == 0:
            if current == (0, 0):
                return ("exit", None)
            p = self.find_path_ground_truth(current, (0, 0))
            if p and len(p) > 1:
                return ("move", p[1])
            else:
                return ("wait", None)
        
        # If current cell has gold => grab
        if "glitter" in self.game.world.get_percepts(*current):
            return ("grab", None)
        
        # Attempt to shoot a known wumpus if possible
        known_wumpus = [c for c, inf in self.knowledge.items() if inf['wumpus'] == 1]
        if known_wumpus and agent.arrows > 0:
            candidate = None
            max_cnt = 0
            for c in known_wumpus:
                # Count how many stench cells are next to c
                cnt = sum(1 for s in self.stench_cells if c in self.get_neighbors(s))
                if cnt > max_cnt:
                    max_cnt = cnt
                    candidate = c
            if candidate:
                (wx, wy) = candidate
                # If aligned => shoot
                if wx == agent.x or wy == agent.y:
                    if wx == agent.x:
                        return ("shoot", 'N' if wy > agent.y else 'S')
                    else:
                        return ("shoot", 'E' if wx > agent.x else 'W')
                else:
                    # Move to vantage spot
                    vantage = [v for v in self.vantage_spots(wx, wy) if v in self.safe_set]
                    path = self.find_path_to_any(current, vantage)
                    if path and len(path) > 1:
                        return ("move", path[1])
                    return ("wait", None)
        
        # Otherwise, move to a safe, unvisited neighbor
        neighbors = self.get_neighbors(current)
        safe_nbr = [n for n in neighbors if n in self.safe_set and n not in self.visited]
        if safe_nbr:
            return ("move", safe_nbr[0])

        # BFS to any unvisited safe cell
        unvisited = [c for c in self.safe_set if c not in self.visited]
        if unvisited:
            p = self.find_path_knowledge(current, unvisited)
            if p and len(p) > 1:
                return ("move", p[1])

        # No safe moves => wait => treat as loss
        return ("wait", None)

    def execute_action(self, action, param):
        if action == "move":
            # For auto-run, we do the existing move approach
            self.turn_to_cell(param)
            self.move_auto()
        elif action == "grab":
            self.grab()
        elif action == "shoot":
            if self.game.agent.arrows > 0:
                self.game.agent.orientation = param
                self.update_status()
                self.draw_grid()
                self.shoot()
        elif action == "exit":
            self.exit_game()
        elif action == "wait":
            self.display_message("No safe moves - waiting... Loss.", "orange")
            self.game.game_over = True
            if self.iteration_mode:
                self.iteration_finished()

    def turn_to_cell(self, cell):
        """For auto-run: turn to face the next cell if needed, then move."""
        ax, ay = self.game.agent.x, self.game.agent.y
        cx, cy = cell
        desired = None
        if cx > ax:
            desired = 'E'
        elif cx < ax:
            desired = 'W'
        elif cy > ay:
            desired = 'N'
        elif cy < ay:
            desired = 'S'
        if desired and self.game.agent.orientation != desired:
            self.game.agent.orientation = desired
            self.update_status()
            self.draw_grid()

    def move_auto(self):
        """Auto-run movement logic (the old 'move' function)."""
        if self.game.game_over:
            return
        bump = self.game.agent.move_forward(self.game.world)
        self.score -= 1
        if bump:
            self.display_message("Bumped into a wall!", "orange")
        else:
            if self.check_for_hazard():
                self.update_status()
                self.draw_grid()
                return
            self.display_message("Moved safely.", "black")
        self.update_status()
        self.draw_grid()
        self.check_win_condition()

    # ------------------- Basic Game Actions -------------------
    def check_for_hazard(self):
        cell = self.game.world.grid[self.game.agent.x][self.game.agent.y]
        if cell.has_pit:
            self.game.agent.alive = False
            self.game.game_over = True
            self.score -= 1000
            self.display_message("You fell into a pit! Game Over.", "red")
            if not self.iteration_mode:
                self.master.after(2000, self.master.destroy)
            return True
        if cell.has_wumpus:
            self.game.agent.alive = False
            self.game.game_over = True
            self.score -= 1000
            self.display_message("You encountered a live Wumpus! Game Over.", "red")
            if not self.iteration_mode:
                self.master.after(2000, self.master.destroy)
            return True
        return False

    def check_win_condition(self):
        if (self.game.agent.has_gold and
            self.game.world.count_wumpuses() == 0 and
            not self.game.game_over):
            self.game.game_over = True
            if not self.iteration_mode:
                messagebox.showinfo("Victory",
                    f"You killed all Wumpuses and grabbed the gold!\nFinal Score: {self.score}")
                self.master.after(2000, self.master.destroy)

    def shoot(self):
        if self.game.game_over:
            return
        if self.game.agent.arrows <= 0:
            self.display_message("No arrows left!", "orange")
            return
        self.score -= 10
        self.game.agent.arrows -= 1
        x, y = self.game.agent.x, self.game.agent.y
        orientation = self.game.agent.orientation
        killed, posk = self.game.world.shoot_arrow(x, y, orientation)
        if killed:
            self.display_message("You killed a Wumpus!", "green")
            self.score += 100
            if posk:
                # Remove stench from neighbors
                for nb in self.get_neighbors(posk):
                    if nb in self.visited_percepts and "stench" in self.visited_percepts[nb]:
                        self.visited_percepts[nb].remove("stench")
        else:
            self.display_message("You missed! Game Over.", "red")
            self.score -= 1000
            self.game.game_over = True
            self.update_status()
            self.draw_grid()
            if not self.iteration_mode:
                self.master.after(2000, self.master.destroy)
            return
        self.update_status()
        self.check_win_condition()

    def grab(self):
        if self.game.game_over:
            return
        cell = self.game.world.grid[self.game.agent.x][self.game.agent.y]
        if cell.has_gold:
            cell.has_gold = False
            self.game.agent.has_gold = True
            self.display_message("You picked up the gold!", "green")
            self.score += 500
        else:
            self.display_message("No gold here!", "orange")
        self.update_status()
        self.draw_grid()
        self.check_win_condition()

    def exit_game(self):
        if self.game.game_over:
            return
        if self.game.agent.has_gold and self.game.world.count_wumpuses() == 0:
            self.score += 1000
            self.display_message("You exited with gold & all Wumpuses dead! Victory!", "green")
        else:
            self.display_message("Exited early. (Goal not fully met)", "black")
        self.game.game_over = True
        if not self.iteration_mode:
            self.master.after(2000, self.master.destroy)

    def restart_game(self):
        self.game = WumpusGame(self.size, 0.2)
        self.score = 0
        self.visited = {(self.game.agent.x, self.game.agent.y)}
        self.safe_set = {(self.game.agent.x, self.game.agent.y)}
        self.visited_percepts = {}
        self.stench_cells = set()
        self.knowledge = {
            (x, y): {'pit': 0.5, 'wumpus': 0.5}
            for x in range(self.size)
            for y in range(self.size)
        }
        self.knowledge[(0, 0)]['pit'] = 0
        self.knowledge[(0, 0)]['wumpus'] = 0
        self.update_status()
        self.draw_grid()
        self.update_visited_display()
        self.display_message("")

# ------------------- Main Entry Point -------------------
if __name__ == '__main__':
    root = tk.Tk()
    root.state("zoomed")
    app = WumpusGameGUI_Auto(root, size=20, pit_prob=0.2)
    root.mainloop()
