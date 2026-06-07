import pygame
import time
from math import sqrt

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("D* Path Finding Algorithm")

# Màu sắc
ROBOT = (255, 0, 0)
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
        self.x = col * width
        self.y = row * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self): return self.row, self.col
    def is_barrier(self): return self.color == BLACK or self.color == (255, 182, 193) # coi cả barrier thường (đen) và barrier động (hồng nhạt) là vật cản
    def is_start(self): return self.color == ORANGE
    def is_end(self): return self.color == TURQUOISE
    def reset(self): self.color = WHITE
    def make_start(self): self.color = ORANGE
    def make_end(self): self.color = TURQUOISE
    def make_barrier(self): self.color = BLACK
    def make_dynamic_barrier(self): self.color = (255, 182, 193)
    def make_path(self): self.color = PURPLE
    def make_robot(self): self.color = ROBOT
    def make_open(self): self.color = GREEN
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # 4 hướng cơ bản
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

        # thêm 4 hướng chéo, tránh corner cutting
        if self.row > 0 and self.col > 0:
            if (not grid[self.row - 1][self.col - 1].is_barrier() and
                not grid[self.row - 1][self.col].is_barrier() and
                not grid[self.row][self.col - 1].is_barrier()):
                self.neighbors.append(grid[self.row - 1][self.col - 1])
        if self.row > 0 and self.col < self.total_rows - 1:
            if (not grid[self.row - 1][self.col + 1].is_barrier() and
                not grid[self.row - 1][self.col].is_barrier() and
                not grid[self.row][self.col + 1].is_barrier()):
                self.neighbors.append(grid[self.row - 1][self.col + 1])
        if self.row < self.total_rows - 1 and self.col > 0:
            if (not grid[self.row + 1][self.col - 1].is_barrier() and
                not grid[self.row + 1][self.col].is_barrier() and
                not grid[self.row][self.col - 1].is_barrier()):
                self.neighbors.append(grid[self.row + 1][self.col - 1])
        if self.row < self.total_rows - 1 and self.col < self.total_rows - 1:
            if (not grid[self.row + 1][self.col + 1].is_barrier() and
                not grid[self.row + 1][self.col].is_barrier() and
                not grid[self.row][self.col + 1].is_barrier()):
                self.neighbors.append(grid[self.row + 1][self.col + 1])

    def __lt__(self, other): 
        return False

# ---------------- Robot ----------------
def run_robot(win, grid, rows, width, path, speed=0.5, start=None, end=None):
    current = start
    while current != end and path:
        next_spot = path.pop(0)

        # tô robot ở ô hiện tại
        if not next_spot.is_start() and not next_spot.is_end():
            next_spot.make_robot()

        # đánh dấu ô đã đi qua thành màu đỏ
        if current != start and current != end:
            current.make_path()

        current = next_spot

        draw(win, grid, rows, width)
        pygame.display.update()
        time.sleep(speed)

        # xử lý sự kiện trong lúc robot chạy
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                new_spot = grid[row][col]
                if new_spot != start and new_spot != end:
                    new_spot.make_dynamic_barrier()
                    # cập nhật lại neighbors
                    for r in grid:
                        for s in r:
                            s.update_neighbors(grid)
                    # tính lại đường đi từ vị trí hiện tại
                    new_path = d_star(lambda: draw(win, grid, rows, width), grid, current, end)
                    if new_path:
                        # vẽ thêm path mới nối tiếp
                        for spot in new_path:
                            if not spot.is_start() and not spot.is_end() and spot != current:
                                spot.make_path()
                        path = new_path

# ---------------- Draw ----------------
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
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos
    row = y // gap
    col = x // gap
    return row, col

# ---------------- D* ----------------
def process_state(open_list, close_list, h, k, b, T, grid):
    if not open_list: return None
    v_min = min(open_list, key=lambda v: k[v])
    k_old = k[v_min]
    open_list.remove(v_min)
    close_list.add(v_min)

    if k_old < h[v_min]:
        for u in v_min.neighbors:
            cost = 1 if (u.row == v_min.row or u.col == v_min.col) else sqrt(2)
            if h[u] <= k_old and h[v_min] >= h[u] + cost:
                b[v_min] = u
                h[v_min] = h[u] + cost

    elif k_old == h[v_min]:
        for u in v_min.neighbors:
            cost = 1 if (u.row == v_min.row or u.col == v_min.col) else sqrt(2)
            if (T[u] == "NEW" or
                (b.get(u) == v_min and h[u] != h[v_min] + cost) or
                (b.get(u) != v_min and h[u] > h[v_min] + cost)):
                b[u] = v_min
                h[u] = h[v_min] + cost
                k[u] = h[u]
                open_list.add(u)
                T[u] = "OPEN"
                if not u.is_start() and not u.is_end():
                    u.make_open()

    else: # k_old > h[v_min]
        for u in v_min.neighbors:
            cost = 1 if (u.row == v_min.row or u.col == v_min.col) else sqrt(2)
            if (T[u] == "NEW" or (b.get(u) == v_min and h[u] != h[v_min] + cost)):
                b[u] = v_min
                h[u] = h[v_min] + cost
                k[u] = h[u]
                open_list.add(u)
                T[u] = "OPEN"
                if not u.is_start() and not u.is_end():
                    u.make_open()
            elif b.get(u) != v_min and h[u] > h[v_min] + cost:
                h[v_min] = h[u] + cost
                k[v_min] = h[v_min]
                open_list.add(v_min)
                T[v_min] = "OPEN"
                if not v_min.is_start() and not v_min.is_end():
                    v_min.make_open()

    return None if not open_list else min(open_list, key=lambda v: k[v])

def d_star(draw, grid, start, end):
    open_list, close_list = set(), set()
    h, k, b, T = {}, {}, {}, {}
    for row in grid:
        for spot in row:
            h[spot] = float("inf")
            k[spot] = float("inf")
            b[spot] = None
            T[spot] = "NEW"
    h[end] = 0; k[end] = 0
    open_list.add(end); T[end] = "OPEN"

    while open_list:
        v_min = process_state(open_list, close_list, h, k, b, T, grid)
        if v_min is None: break
        if v_min == start: break
        draw()

    path = []
    current = start
    while current in b and b[current] is not None and current != end:
        current = b[current]
        if current != start and current != end:
            current.make_path()
            path.append(current)
        draw(); pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return None

    print("✅ Đã tìm ra đường đi tối ưu.")
    return path

# ---------------- MAIN ----------------
def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start, end, path = None, None, None
    robot_speed = 0.5   # tốc độ mặc định mượt nhất
    robot_running = False
    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Chuột trái: đặt start, end hoặc barrier (đen/hồng)
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                keys = pygame.key.get_pressed()

                if not start and spot != end:
                    start = spot; start.make_start()
                elif not end and spot != start:
                    end = spot; end.make_end()
                elif spot != start and spot != end:
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        # giữ Shift khi click chuột trái → barrier động (hồng)
                        spot.make_dynamic_barrier()
                    else:
                        # mặc định chuột trái → barrier thường (đen)
                        spot.make_barrier()

            # Chuột phải: reset ô
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start: start = None
                elif spot == end: end = None

            if event.type == pygame.KEYDOWN:
                # SPACE: tìm đường đi (chỉ chạy khi bấm SPACE)
                if event.key == pygame.K_SPACE and start and end:
                    for r in grid:
                        for s in r:
                            s.update_neighbors(grid)
                    path = d_star(lambda: draw(win, grid, ROWS, width), grid, start, end)

                # S: robot chạy theo đường đi
                if event.key == pygame.K_s and path:
                    robot_running = True
                    run_robot(win, grid, ROWS, width, path, robot_speed, start, end)

                # ↑ / ↓: chỉnh tốc độ robot
                if event.key == pygame.K_UP:
                    robot_speed = max(0.01, robot_speed - 0.05)
                    print(f"Tốc độ robot: {robot_speed:.2f}s/ô")
                if event.key == pygame.K_DOWN:
                    robot_speed += 0.05
                    print(f"Tốc độ robot: {robot_speed:.2f}s/ô")

                # R: reset toàn bộ lưới
                if event.key == pygame.K_r:
                    start, end, path = None, None, None
                    robot_running = False
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WIN, WIDTH)
