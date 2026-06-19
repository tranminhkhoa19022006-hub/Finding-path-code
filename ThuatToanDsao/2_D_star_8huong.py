import pygame
import time

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("D* Path Finding Algorithm")

# Màu sắc
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
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_barrier(self):
        self.color = BLACK

    def make_path(self):
        if not self.is_start() and not self.is_end():
            self.color = PURPLE

    def make_open(self):
        if not self.is_start() and not self.is_end():
            self.color = GREEN

    def make_closed(self):
        if not self.is_start() and not self.is_end():
            self.color = RED

    def reset(self):
        self.color = WHITE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []

        # 4 hướng cơ bản
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

        # 4 hướng chéo (có kiểm tra góc)
        # UP-LEFT
        if self.row > 0 and self.col > 0:
            if (not grid[self.row - 1][self.col].is_barrier() and
                not grid[self.row][self.col - 1].is_barrier() and
                not grid[self.row - 1][self.col - 1].is_barrier()):
                self.neighbors.append(grid[self.row - 1][self.col - 1])

        # UP-RIGHT
        if self.row > 0 and self.col < self.total_rows - 1:
            if (not grid[self.row - 1][self.col].is_barrier() and
                not grid[self.row][self.col + 1].is_barrier() and
                not grid[self.row - 1][self.col + 1].is_barrier()):
                self.neighbors.append(grid[self.row - 1][self.col + 1])

        # DOWN-LEFT
        if self.row < self.total_rows - 1 and self.col > 0:
            if (not grid[self.row + 1][self.col].is_barrier() and
                not grid[self.row][self.col - 1].is_barrier() and
                not grid[self.row + 1][self.col - 1].is_barrier()):
                self.neighbors.append(grid[self.row + 1][self.col - 1])

        # DOWN-RIGHT
        if self.row < self.total_rows - 1 and self.col < self.total_rows - 1:
            if (not grid[self.row + 1][self.col].is_barrier() and
                not grid[self.row][self.col + 1].is_barrier() and
                not grid[self.row + 1][self.col + 1].is_barrier()):
                self.neighbors.append(grid[self.row + 1][self.col + 1])

    def __lt__(self, other):
        return False

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

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

def save_map(grid, start, end, filename="map.txt"):
    if start is None or end is None:
        print("Chưa chọn START hoặc END, không thể lưu bản đồ!")
        return
    with open(filename, "w") as f:
        for row in grid:
            for spot in row:
                if spot.is_barrier():
                    r, c = spot.get_pos()
                    f.write(f"BAR,{r},{c}\n")
        r, c = start.get_pos()
        f.write(f"START,{r},{c}\n")
        r, c = end.get_pos()
        f.write(f"END,{r},{c}\n")
    print("✅ Đã lưu bản đồ.")

def load_map(grid, filename="map.txt"):
    start = None
    end = None
    try:
        with open(filename, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if parts[0] == "BAR":
                    r, c = map(int, parts[1:])
                    grid[r][c].make_barrier()
                elif parts[0] == "START":
                    r, c = map(int, parts[1:])
                    start = grid[r][c]
                    start.make_start()
                elif parts[0] == "END":
                    r, c = map(int, parts[1:])
                    end = grid[r][c]
                    end.make_end()
    except FileNotFoundError:
        print("Chưa có file map.txt.")
    return start, end

# ---------------- D* ----------------

from math import sqrt

def process_state(open_list, close_list, h, k, b, T, grid):
    if not open_list:
        return None

    v_min = min(open_list, key=lambda v: k[v])
    k_old = k[v_min]
    open_list.remove(v_min)
    close_list.add(v_min)

    # Trường hợp 1: k_old < h[v_min]
    if k_old < h[v_min]:
        for u in v_min.neighbors:
            cost = 1 if (u.row == v_min.row or u.col == v_min.col) else sqrt(2)
            if h[u] <= k_old and h[v_min] >= h[u] + cost:
                b[v_min] = u
                h[v_min] = h[u] + cost

    # Trường hợp 2: k_old == h[v_min]
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

    # Trường hợp 3: k_old > h[v_min]
    else:
        for u in v_min.neighbors:
            cost = 1 if (u.row == v_min.row or u.col == v_min.col) else sqrt(2)
            if (T[u] == "NEW" or
                (b.get(u) == v_min and h[u] != h[v_min] + cost)):
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

    if open_list:
        return min(open_list, key=lambda v: k[v])
    return None

def d_star(draw, grid, start, end):
    open_list = set()
    close_list = set()
    h = {}
    k = {}
    b = {}
    T = {}

    for row in grid:
        for spot in row:
            h[spot] = float("inf")
            k[spot] = float("inf")
            b[spot] = None
            T[spot] = "NEW"

    h[end] = 0
    k[end] = 0
    open_list.add(end)
    T[end] = "OPEN"

    while open_list:
        v_min = process_state(open_list, close_list, h, k, b, T, grid)
        if v_min is None or v_min == start:
            break
        draw()

    # Vẽ đường đi từ end về start
    current = start
    while current in b and b[current] is not None and current != end:
        current = b[current]
        if current != start and current != end:
            current.make_path()

        draw()
        pygame.display.update()

        # Xử lý sự kiện để tránh treo cửa sổ
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

# ---------------- MAIN ----------------

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None
    run = True

    while run:
        draw(win, grid, ROWS, width)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Chuột trái: chọn start, end, barrier
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

            # Chuột phải: xóa ô
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            # Bàn phím
            if event.type == pygame.KEYDOWN:
                # SPACE: chạy D*
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    start_time = time.time()
                    d_star(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    elapsed = time.time() - start_time
                    print(f"Thời gian tìm đường (D*): {elapsed:.4f} giây")

                # C: lưu bản đồ
                if event.key == pygame.K_c:
                    save_map(grid, start, end)

                # V: tải lại bản đồ
                if event.key == pygame.K_v:
                    grid = make_grid(ROWS, width)
                    start, end = load_map(grid)
                    print("Đã tải lại bản đồ")

                # R: reset toàn bộ
                if event.key == pygame.K_r:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

# Chạy chương trình
main(WIN, WIDTH)
