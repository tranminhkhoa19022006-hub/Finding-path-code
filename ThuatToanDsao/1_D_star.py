import pygame 
import math
from queue import PriorityQueue 
import time

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH)) 
pygame.display.set_caption("WEIGHTED A* Path Finding Algorithm") 

RED = (255, 0, 0) 
GREEN = (0, 255, 0) 
BLUE = (0, 255, 0) 
YELLOW = (255, 255, 0)  
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

heuristic_type = "manhattan"
def h(p1, p2): #heuristic
    x1, y1 = p1
    x2, y2 = p2

    if heuristic_type == "manhattan":
        return abs(x1 - x2) + abs(y1 - y2)
    elif heuristic_type == "euclidean":
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    elif heuristic_type == "chebyshev":
        return max(abs(x1 - x2), abs(y1 - y2))
    else:
        return 0

def print_state(current, g_score, f_score): #hàm in giá trị g_score,f_score
    print("Current position: ", end="")
    print(current.get_pos())
    print("Current gscore: ", end="")
    print(g_score[current])
    print("Current fscore: ", end="")
    print(f_score[current])

def get_clicked_pos(pos, rows, width): #xác định ô được click, chuyển tọa độ chuột thành vị trí trong lưới
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col

def draw(win, grid, rows, width): #vẽ toàn bộ cửa sổ, vẽ các ô và các lưới lên cửa sổ
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()

def draw_grid(win, rows, width): #vẽ lưới, vẽ các đường kẻ phân chia ô
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def make_grid(rows, width): #tạo lưới, tọa lưới 2D gồm các spot
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid

def reconstruct_path(came_from, current, draw): #hàm dựng lại đường đi, duyệt ngược từ điểm kết thúc về điểm bắt đầu để tô màu đường đi
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()

def save_map(grid, start, end, filename="map.txt"): #lưu map
    if start is None or end is None:
        print("Chưa chọn START hoặc END, không thể lưu bản đồ!")
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

def load_map(grid, filename="map.txt"): #tải lại map
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
        print("Chưa có file map.txt, hãy bấm C để lưu bản đồ trước.")
    return start, end

def process_state(open_list, close_list, h, k, b, T, grid): #pseudo 5
    if not open_list:
        return None

    # Lấy node có k nhỏ nhất
    v_min = min(open_list, key=lambda v: k[v])
    k_old = k[v_min]
    open_list.remove(v_min)
    close_list.add(v_min)

    # Trường hợp 1: k_old < h[v_min]
    if k_old < h[v_min]:
        for u in v_min.neighbors:
            if h[u] <= k_old and h[v_min] >= h[u] + 1:  # cost = 1 hoặc sqrt(2)
                b[v_min] = u
                h[v_min] = h[u] + 1

    # Trường hợp 2: k_old == h[v_min]
    elif k_old == h[v_min]:
        for u in v_min.neighbors:
            if (T[u] == "NEW" or
                (b.get(u) == v_min and h[u] != h[v_min] + 1) or
                (b.get(u) != v_min and h[u] > h[v_min] + 1)):
                b[u] = v_min
                h[u] = h[v_min] + 1
                k[u] = h[u]
                open_list.add(u)
                T[u] = "OPEN"

    # Trường hợp 3: k_old > h[v_min]
    else:
        for u in v_min.neighbors:
            if (T[u] == "NEW" or
                (b.get(u) == v_min and h[u] != h[v_min] + 1)):
                b[u] = v_min
                h[u] = h[v_min] + 1
                k[u] = h[u]
                open_list.add(u)
                T[u] = "OPEN"
            elif b.get(u) != v_min and h[u] > h[v_min] + 1:
                h[v_min] = h[u] + 1
                k[v_min] = h[v_min]
                open_list.add(v_min)
                T[v_min] = "OPEN"

    if open_list:
        return min(open_list, key=lambda v: k[v])
    return None

def d_star(draw, grid, start, end): #pseudo 6
    # Khởi tạo
    h = {spot: float("inf") for row in grid for spot in row}
    k = {spot: float("inf") for row in grid for spot in row}
    b = {}
    T = {spot: "NEW" for row in grid for spot in row}

    h[end] = 0
    k[end] = 0
    open_list = {end}
    close_list = set()

    # Tìm đường ban đầu
    while start not in close_list and open_list:
        v_min = process_state(open_list, close_list, h, k, b, T, grid)
        if v_min is None:
            print("Không tìm thấy đường đi.")
            return False

    # Dựng lại đường đi từ start → goal
    current = start
    while current != end:
        if current not in b:
            print("Không có backpointer, đường đi bị gián đoạn.")
            return False
        current = b[current]
        current.make_path()

    end.make_end()
    return True

def main(win, width):
    global heuristic_type  # để thay đổi heuristic từ phím
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

            # Chuột trái: vẽ điểm bắt đầu, kết thúc, vật cản
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
                # SPACE: chạy thuật toán
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    start_time = time.time()
                    d_star(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    elapsed = time.time() - start_time
                    print(f"Thời gian tìm đường: {elapsed:.4f} giây")

                # C: lưu bản đồ ra file
                if event.key == pygame.K_c:
                    save_map(grid, start, end)

                # V: tải lại bản đồ từ file
                if event.key == pygame.K_v:
                    grid = make_grid(ROWS, width)
                    start, end = load_map(grid)
                    print("Đã tải lại bản đồ")

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
                            elif spot.color == RED:
                                red += 1
                            elif spot.color == GREEN:
                                green += 1
                    print("THỐNG KÊ:")
                    print(f"PURPLE (Số ô trong đường đi): {purple}")
                    print(f"RED (Số ô đã duyệt): {red}")
                    print(f"GREEN (Số ô đang mở): {green}")

                # Chọn heuristic (1,2,3)
                if event.key == pygame.K_1:
                    heuristic_type = "manhattan"
                    print("Đã chọn heuristic: Manhattan")
                if event.key == pygame.K_2:
                    heuristic_type = "euclidean"
                    print("Đã chọn heuristic: Euclidean")
                if event.key == pygame.K_3:
                    heuristic_type = "chebyshev"
                    print("Đã chọn heuristic: Chebyshev")

    pygame.quit()

main(WIN, WIDTH)
