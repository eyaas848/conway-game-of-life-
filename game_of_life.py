import tkinter as tk
from tkinter import ttk
import random

PRESETS = {
    "Glider": [(0,1),(1,2),(2,0),(2,1),(2,2)],
    "Pulsar": [(2,4),(2,5),(2,6),(2,10),(2,11),(2,12),
               (4,2),(4,7),(4,9),(4,14),
               (5,2),(5,7),(5,9),(5,14),
               (6,2),(6,7),(6,9),(6,14),
               (7,4),(7,5),(7,6),(7,10),(7,11),(7,12),
               (9,4),(9,5),(9,6),(9,10),(9,11),(9,12),
               (10,2),(10,7),(10,9),(10,14),
               (11,2),(11,7),(11,9),(11,14),
               (12,2),(12,7),(12,9),(12,14),
               (14,4),(14,5),(14,6),(14,10),(14,11),(14,12)],
    "Vaisseau (LWSS)": [(0,1),(0,4),(1,0),(2,0),(2,4),(3,0),(3,1),(3,2),(3,3)],
}

class GameOfLife:
    def __init__(self, root, width=50, height=40, cell_size=14):
        self.root = root
        self.root.title("Conway's Game of Life")
        self.root.configure(bg="#0d0d0d")
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.running = False
        self.speed = tk.IntVar(value=100)
        self.generation = 0

        self.grid = self.random_grid()
        self.age = [[0 for _ in range(width)] for _ in range(height)]

        top = tk.Frame(root, bg="#0d0d0d")
        top.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.gen_label = tk.Label(top, text="Génération : 0", fg="#00ff88", bg="#0d0d0d", font=("Consolas", 11, "bold"))
        self.gen_label.pack(side=tk.LEFT)

        self.pop_label = tk.Label(top, text="Population : 0", fg="#00ff88", bg="#0d0d0d", font=("Consolas", 11, "bold"))
        self.pop_label.pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(root, width=width*cell_size, height=height*cell_size, bg="#050505", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_click)

        controls = tk.Frame(root, bg="#0d0d0d")
        controls.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.start_btn = tk.Button(controls, text="Démarrer", command=self.toggle_simulation,
                                    bg="#00ff88", fg="#0d0d0d", font=("Consolas", 10, "bold"), relief=tk.FLAT, padx=10)
        self.start_btn.pack(side=tk.LEFT, padx=4)

        self.reset_btn = tk.Button(controls, text="Aléatoire", command=self.reset_grid,
                                    bg="#222222", fg="#00ff88", font=("Consolas", 10), relief=tk.FLAT, padx=10)
        self.reset_btn.pack(side=tk.LEFT, padx=4)

        self.clear_btn = tk.Button(controls, text="Effacer", command=self.clear_grid,
                                    bg="#222222", fg="#00ff88", font=("Consolas", 10), relief=tk.FLAT, padx=10)
        self.clear_btn.pack(side=tk.LEFT, padx=4)

        self.preset_var = tk.StringVar(value="Formes")
        preset_menu = ttk.Combobox(controls, textvariable=self.preset_var, values=list(PRESETS.keys()), state="readonly", width=14)
        preset_menu.pack(side=tk.LEFT, padx=4)
        preset_menu.bind("<<ComboboxSelected>>", self.place_preset)

        tk.Label(controls, text="Vitesse", fg="#00ff88", bg="#0d0d0d", font=("Consolas", 9)).pack(side=tk.LEFT, padx=(20, 4))
        speed_slider = tk.Scale(controls, from_=20, to=500, orient=tk.HORIZONTAL, variable=self.speed,
                                 bg="#0d0d0d", fg="#00ff88", troughcolor="#222222", highlightthickness=0, showvalue=0, length=120)
        speed_slider.pack(side=tk.LEFT)

        self.draw_grid()
        self.update()

    def random_grid(self):
        return [[1 if random.random() < 0.25 else 0 for _ in range(self.width)] for _ in range(self.height)]

    def cell_color(self, age):
        age = min(age, 20)
        g = 255 - int(age * 6)
        return f"#00{g:02x}44"

    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] == 1:
                    x1 = c * self.cell_size
                    y1 = r * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    color = self.cell_color(self.age[r][c])
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#050505")

    def count_neighbors(self, r, c):
        count = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if i == 0 and j == 0:
                    continue
                nr = (r + i) % self.height
                nc = (c + j) % self.width
                count += self.grid[nr][nc]
        return count

    def next_generation(self):
        new_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        new_age = [[0 for _ in range(self.width)] for _ in range(self.height)]

        for r in range(self.height):
            for c in range(self.width):
                neighbors = self.count_neighbors(r, c)
                alive = self.grid[r][c] == 1

                if alive and neighbors in (2, 3):
                    new_grid[r][c] = 1
                    new_age[r][c] = self.age[r][c] + 1
                elif not alive and neighbors == 3:
                    new_grid[r][c] = 1
                    new_age[r][c] = 0

        self.grid = new_grid
        self.age = new_age
        self.generation += 1

    def toggle_simulation(self):
        self.running = not self.running
        self.start_btn.config(text="Pause" if self.running else "Démarrer")

    def reset_grid(self):
        self.grid = self.random_grid()
        self.age = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.generation = 0
        self.draw_grid()

    def clear_grid(self):
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.age = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.generation = 0
        self.draw_grid()

    def place_preset(self, event):
        name = self.preset_var.get()
        if name not in PRESETS:
            return
        self.clear_grid()
        offset_r, offset_c = self.height // 2 - 8, self.width // 2 - 8
        for r, c in PRESETS[name]:
            rr, cc = (offset_r + r) % self.height, (offset_c + c) % self.width
            self.grid[rr][cc] = 1
        self.draw_grid()

    def on_click(self, event):
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        if 0 <= r < self.height and 0 <= c < self.width:
            self.grid[r][c] = 1
            self.age[r][c] = 0
            self.draw_grid()

    def update(self):
        pop = sum(sum(row) for row in self.grid)
        self.gen_label.config(text=f"Génération : {self.generation}")
        self.pop_label.config(text=f"Population : {pop}")

        if self.running:
            self.next_generation()
            self.draw_grid()

        self.root.after(self.speed.get(), self.update)

if __name__ == "__main__":
    window = tk.Tk()
    app = GameOfLife(window)
    window.mainloop()
