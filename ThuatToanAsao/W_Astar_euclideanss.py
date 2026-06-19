import pygame
import math
from queue import PriorityQueue
import time
import random

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Weighted A* Path Finding Algorithm")

# Màu sắc
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

def save_start_end(start, end, filename="start_end.txt"):
    """
    Lưu tọa độ điểm START và END vào file.
    - start, end: Spot (có thể None nếu chưa chọn)
    - filename: tên file để lưu
    """
    if start is None or end is None:
        print("⚠️ Chưa chọn START hoặc END, không thể lưu tọa độ!")
        return

    with open(filename, "w") as f:
        r1, c1 = start.get_pos()
        r2, c2 = end.get_pos()
        f.write(f"START,{r1},{c1}\n")
        f.write(f"END,{r2},{c2}\n")

    print(f"✅ Đã lưu tọa độ START ({r1},{c1}) và END ({r2},{c2}) vào {filename}")

def auto_barriers(grid, start, end, barrier_percent=30):
    """
    Sinh vật cản ngẫu nhiên trên lưới.
    - grid: ma trận Spot
    - start, end: điểm bắt đầu và kết thúc (không bị biến thành barrier)
    - barrier_percent: tỉ lệ % vật cản (0–100)
    """
    for row in grid:
        for spot in row:
            if spot != start and spot != end:
                if random.randint(1, 100) <= barrier_percent:
                    spot.make_barrier()
    print(f"✅ Đã tự động tạo vật cản với tỉ lệ {barrier_percent}%")

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

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []

        # Dọc và ngang
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

        # Chéo có kiểm tra góc
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

# Heuristic cố định: Euclidean
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# Chọn trọng số
weight_mode = "w1"  # mặc định

def weighted_a_star(draw, grid, start, end, epsilon=1e-5):
    """
    Weighted A* với 3 chế độ trọng số:
    w1 = 1.5
    w2 = 1 + g(n)/D
    w3 = 1 + h(n)/(g(n)+ε)

    Có 2 chế độ chạy:
    - S: thủ công từng bước
    - T: tự động liên tục
    """
    D = h(start.get_pos(), end.get_pos())
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}

    g_score = {spot: float("inf") for row in grid for spot in row}
    f_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score[start] = g_score[start] + h(start.get_pos(), end.get_pos())
    open_set_hash = {start}

    step_mode = True  # mặc định: thủ công

    while not open_set.empty():
        if step_mode:
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_s:   # nhấn S để đi tiếp một bước
                            waiting = False
                        elif event.key == pygame.K_t: # nhấn T để chuyển sang tự động
                            step_mode = False
                            waiting = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    step_mode = True  # quay lại chế độ thủ công

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            # reconstruct path và tính độ dài
            path_length = 0.0
            while current in came_from:
                prev = came_from[current]
                r1, c1 = current.get_pos()
                r2, c2 = prev.get_pos()
                step_cost = math.sqrt(2) if (r1 != r2 and c1 != c2) else 1
                path_length += step_cost
                current = prev
                if not current.is_start() and not current.is_end() and not current.is_barrier():
                    current.make_path()
                draw()
            end.make_end()
            print(f"📏 Độ dài quãng đường: {path_length:.4f}")
            return True

        for neighbor in current.neighbors:
            if neighbor.is_barrier():
                continue  # bỏ qua barrier

            r1, c1 = current.get_pos()
            r2, c2 = neighbor.get_pos()
            step_cost = math.sqrt(2) if (r1 != r2 and c1 != c2) else 1
            temp_g_score = g_score[current] + step_cost

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                heuristic = h(neighbor.get_pos(), end.get_pos())

                # chọn công thức trọng số
                if weight_mode == "w1":
                    weight = 1.5
                elif weight_mode == "w2":
                    weight = 1 + temp_g_score / D
                elif weight_mode == "w3":
                    weight = 1 + heuristic / (temp_g_score + epsilon)
                else:
                    weight = 1

                f_score[neighbor] = temp_g_score + weight * heuristic

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if not neighbor.is_start() and not neighbor.is_end() and not neighbor.is_barrier():
                        neighbor.make_open()

        draw()
        if current != start and not current.is_end() and not current.is_barrier():
            current.make_closed()

    return False

def save_map(grid, start, end, filename="map.txt"):
    if start is None or end is None:
        print("⚠️ Chưa chọn START hoặc END, không thể lưu bản đồ!")
        return

    with open(filename, "w") as f:
        # Lưu vật cản
        for row in grid:
            for spot in row:
                if spot.is_barrier():
                    r, c = spot.get_pos()
                    f.write(f"BAR,{r},{c}\n")

        # Lưu start
        r, c = start.get_pos()
        f.write(f"START,{r},{c}\n")

        # Lưu end
        r, c = end.get_pos()
        f.write(f"END,{r},{c}\n")

    print("✅ Đã lưu bản đồ (START, END, barriers).")

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
        print("⚠️ Chưa có file map.txt, hãy bấm C để lưu bản đồ trước.")
    return start, end

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            grid[i].append(Spot(i, j, gap, rows))
    return grid

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None
    run = True
    global weight_mode

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
                    start = spot; start.make_start()
                elif not end and spot != start:
                    end = spot; end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()

            # Chuột phải: xóa ô
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start: start = None
                elif spot == end: end = None

            # Bàn phím
            if event.type == pygame.KEYDOWN:
                # SPACE: chạy thuật toán
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    start_time = time.time()
                    weighted_a_star(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    elapsed = time.time() - start_time
                    print(f"⏱️ Thời gian tìm đường: {elapsed:.4f} giây")

                if event.key == pygame.K_x:
                    auto_barriers(grid, start, end, barrier_percent=15)  # chỉnh % ở đây

                if event.key == pygame.K_u:
                    save_start_end(start, end)

                # C: lưu bản đồ
                if event.key == pygame.K_c:
                    save_map(grid, start, end)

                # V: tải lại bản đồ
                if event.key == pygame.K_v:
                    grid = make_grid(ROWS, width)
                    start, end = load_map(grid)
                    print("✅ Đã tải lại bản đồ (start, end, vật cản).")

                # R: reset toàn bộ lưới
                if event.key == pygame.K_r:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

                # P: thống kê số ô theo màu
                if event.key == pygame.K_p:
                    purple = red = green = 0
                    for row in grid:
                        for spot in row:
                            if spot.color == PURPLE:
                                purple += 1
                                red += 1   # tính cả PURPLE vào RED
                            elif spot.color == RED:
                                red += 1
                            elif spot.color == GREEN:
                                green += 1
                    print("THỐNG KÊ:")
                    print(f"PURPLE (Số ô trong đường đi): {purple}")
                    print(f"RED (Số ô đã duyệt, gồm cả đường đi): {red}")
                    print(f"GREEN (Số ô đang mở): {green}")

                # chọn trọng số
                if event.key == pygame.K_1:
                    weight_mode = "w1"; print("Đã chọn w1 = 1.5")
                if event.key == pygame.K_2:
                    weight_mode = "w2"; print("Đã chọn w2 = 1 + g(n)/D")
                if event.key == pygame.K_3:
                    weight_mode = "w3"; print("Đã chọn w3 = 1 + h(n)/(g(n)+ε)")

    pygame.quit()

# chạy chương trình
main(WIN, WIDTH)



