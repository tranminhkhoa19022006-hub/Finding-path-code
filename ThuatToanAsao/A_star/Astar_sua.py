import pygame
import math
from queue import PriorityQueue
import time
import pickle

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = col * width   # x theo cột
        self.y = row * width   # y theo hàng
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self): return self.row, self.col
    def is_closed(self): return self.color == RED
    def is_open(self): return self.color == GREEN
    def is_barrier(self): return self.color == BLACK
    def is_start(self): return self.color == ORANGE
    def is_end(self): return self.color == TURQUOISE
    def reset(self): self.color = WHITE
    def make_start(self): self.color = ORANGE
    def make_closed(self): self.color = RED
    def make_open(self): self.color = GREEN
    def make_barrier(self): self.color = BLACK
    def make_end(self): self.color = TURQUOISE
    def make_path(self): self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # 4 hướng
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])
        # Chéo có kiểm tra góc
        if self.row > 0 and self.col > 0:
            if (not grid[self.row - 1][self.col].is_barrier() and
                not grid[self.row][self.col - 1].is_barrier() and
                not grid[self.row - 1][self.col - 1].is_barrier()):
                self.neighbors.append(grid[self.row - 1][self.col - 1])
        if self.row > 0 and self.col < self.total_rows - 1:
            if (not grid[self.row - 1][self.col].is_barrier() and
                not grid[self.row][self.col + 1].is_barrier() and
                not grid[self.row - 1][self.col + 1].is_barrier()):
                self.neighbors.append(grid[self.row - 1][self.col + 1])
        if self.row < self.total_rows - 1 and self.col > 0:
            if (not grid[self.row + 1][self.col].is_barrier() and
                not grid[self.row][self.col - 1].is_barrier() and
                not grid[self.row + 1][self.col - 1].is_barrier()):
                self.neighbors.append(grid[self.row + 1][self.col - 1])
        if self.row < self.total_rows - 1 and self.col < self.total_rows - 1:
            if (not grid[self.row + 1][self.col].is_barrier() and
                not grid[self.row][self.col + 1].is_barrier() and
                not grid[self.row + 1][self.col + 1].is_barrier()):
                self.neighbors.append(grid[self.row + 1][self.col + 1])

    def __lt__(self, other): return False

# ✅ Heuristic (Manhattan)
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def a_star(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    f_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score[start] = h(start.get_pos(), end.get_pos())
    open_set_hash = {start}

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            r1, c1 = current.get_pos()
            r2, c2 = neighbor.get_pos()
            step_cost = math.sqrt(2) if (r1 != r2 and c1 != c2) else 1
            temp_g_score = g_score[current] + step_cost

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()
        if current != start:
            current.make_closed()
    return False

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos   # x trước, y sau
    row = y // gap
    col = x // gap
    return row, col

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None
    run = True
    step_mode = False   # bật/tắt step mode
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Chuột trái: đặt start, end, barrier
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()

            # Chuột phải: xóa
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start: start = None
                elif spot == end: end = None

            # Phím bấm
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    start_time = time.time()
                    a_star(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    elapsed = time.time() - start_time
                    print(f"⏱️ Thời gian tìm đường: {elapsed:.4f} giây")

                if event.key == pygame.K_r:  # reset
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

                if event.key == pygame.K_s:  # lưu bản đồ
                    with open("map.pkl", "wb") as f:
                        pickle.dump([[spot.color for spot in row] for row in grid], f)
                    print("💾 Đã lưu bản đồ")

                if event.key == pygame.K_l:  # tải bản đồ
                    try:
                        with open("map.pkl", "rb") as f:
                            colors = pickle.load(f)
                        for i in range(ROWS):
                            for j in range(ROWS):
                                grid[i][j].color = colors[i][j]
                        print("📂 Đã tải bản đồ")
                    except:
                        print("⚠️ Không tìm thấy file map.pkl")

                if event.key == pygame.K_t:  # thống kê màu
                    stats = {"start":0,"end":0,"barrier":0,"path":0,"open":0,"closed":0}
                    for row in grid:
                        for spot in row:
                            if spot.is_start(): stats["start"]+=1
                            elif spot.is_end(): stats["end"]+=1
                            elif spot.is_barrier(): stats["barrier"]+=1
                            elif spot.color == PURPLE: stats["path"]+=1
                            elif spot.is_open(): stats["open"]+=1
                            elif spot.is_closed(): stats["closed"]+=1
                    print("📊 Thống kê:", stats)

                if event.key == pygame.K_m:  # bật/tắt step mode
                    step_mode = not step_mode
                    print("🔄 Step mode:", "ON" if step_mode else "OFF")

    pygame.quit()

main(WIN, WIDTH)
