import tkinter as tk
from tkinter import messagebox, filedialog

COLOR_WALL = "#333333"
COLOR_PATH = "#ffffff"
COLOR_START = "#4CAF50"    # Зелёный
COLOR_EXIT = "#F44336"     # Красный
COLOR_VISITED = "#BBDEFB"  # Светло-голубой
COLOR_PATH_FOUND = "#FFEB3B"  # Жёлтый (финальный путь)
COLOR_CURRENT = "#2196F3"  # Синий (таракан)

CELL_SIZE = 30  # пикселей

class MazeSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Таракан в поиске дома")
        self.canvas = None
        self.maze = []
        self.start = None
        self.exit = None
        self.path = []
        self.visited_order = []
        self.animation_running = False

        self.setup_ui()
    
    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        load_btn = tk.Button(top_frame, text="Загрузить лабиринт", command=self.load_maze)
        load_btn.pack(side=tk.LEFT, padx=5)

        solve_btn = tk.Button(top_frame, text="Решить (DFS)", command=self.solve_and_animate)
        solve_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(top_frame, text="Загрузите файл с лабиринтом", fg="gray")
        self.status_label.pack(side=tk.LEFT, padx=10)

    def load_maze(self):
        filepath = filedialog.askopenfilename(
            title="Выберите файл лабиринта",
            filetypes=[("Text files", "*.txt")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            self.maze = []
            self.start = None
            self.exit = None

            for i, line in enumerate(lines):
                row = []
                for j, ch in enumerate(line):
                    if ch == '1':
                        row.append(1)
                    elif ch == '0':
                        row.append(0)
                    elif ch == 'S':
                        row.append(0)
                        if self.start:
                            raise ValueError("Найдено более одного старта (S)!")
                        self.start = (i, j)
                    elif ch == 'E':
                        row.append(0)
                        if self.exit:
                            raise ValueError("Найдено более одного выхода (E)!")
                        self.exit = (i, j)
                    else:
                        raise ValueError(f"Недопустимый символ '{ch}' в файле!")
                self.maze.append(row)

            if not self.start:
                raise ValueError("Старт (S) не найден!")
            if not self.exit:
                raise ValueError("Выход (E) не найден!")

            self.draw_maze()
            self.status_label.config(text="Лабиринт загружен. Нажмите 'Решить'.", fg="green")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить лабиринт:\n{e}")

    def draw_maze(self):
        if self.canvas:
            self.canvas.destroy()

        rows = len(self.maze)
        cols = len(self.maze[0]) if rows > 0 else 0

        canvas_width = cols * CELL_SIZE
        canvas_height = rows * CELL_SIZE

        self.canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack(pady=10)

        for i in range(rows):
            for j in range(cols):
                x1 = j * CELL_SIZE
                y1 = i * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                if self.maze[i][j] == 1:
                    color = COLOR_WALL
                else:
                    color = COLOR_PATH

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#ccc")

        # Прорисовываю старт и выход поверх
        self.draw_cell(self.start, COLOR_START, text="S")
        self.draw_cell(self.exit, COLOR_EXIT, text="E")

    def draw_cell(self, pos, color, text=""):
        i, j = pos
        x1 = j * CELL_SIZE + 2
        y1 = i * CELL_SIZE + 2
        x2 = x1 + CELL_SIZE - 4
        y2 = y1 + CELL_SIZE - 4
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        if text:
            self.canvas.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2,
                text=text, fill="white", font=("Arial", 10, "bold")
            )

    def solve_maze(self):
        start = self.start
        goal = self.exit
        rows, cols = len(self.maze), len(self.maze[0])

        stack = [start]
        came_from = {}
        visited = []
        visited_set = set()

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while stack:
            current = stack.pop()
            if current in visited_set:
                continue

            visited_set.add(current)
            visited.append(current)

            if current == goal:
                # Восстановление пути
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path, visited
                
            for dx, dy in reversed(directions):
                neighbor = (current[0] + dx, current[1] + dy)
                if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols):
                    continue
                if self.maze[neighbor[0]][neighbor[1]] == 1:
                    continue
                if neighbor in visited_set:
                    continue

                came_from[neighbor] = current
                stack.append(neighbor)

        return None, visited  #Путь не найден

    def solve_and_animate(self):
        if not self.maze:
            messagebox.showwarning("Внимание", "Сначала загрузите лабиринт!")
            return

        if self.animation_running:
            return

        path, visited = self.solve_maze()
        if path is None:
            messagebox.showinfo("Результат", "Выход не найден!")
            return

        self.path = path
        self.visited_order = visited
        self.animation_running = True
        self.status_label.config(text="Тараканчик ползёт по лабиринту...", fg="blue")
        self.animate_visited()

    def animate_visited(self, idx=0):
        if idx >= len(self.visited_order) or not self.animation_running:
            self.animate_path()
            return

        pos = self.visited_order[idx]
        if pos != self.start and pos != self.exit:
            self.draw_cell(pos, COLOR_VISITED)

        self.root.after(50, self.animate_visited, idx + 1)

    def animate_path(self, idx=0):
        if idx >= len(self.path) or not self.animation_running:
            for pos in self.path:
                if pos != self.exit:
                    self.draw_cell(pos, COLOR_PATH_FOUND)
            self.draw_cell(self.exit, COLOR_EXIT, text="E")
            self.status_label.config(text="Таракашка выбрался из лабиринта!", fg="green")
            self.animation_running = False
            return

        pos = self.path[idx]
        self.draw_cell(pos, COLOR_CURRENT)

        self.root.after(200, self.animate_path, idx + 1)

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeSolverApp(root)
    root.mainloop()
