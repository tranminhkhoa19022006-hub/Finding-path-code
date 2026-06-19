import pygame 
import math
from queue import PriorityQueue 
import time

WIDTH = 600
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
        print("⚠️ Chưa có file map.txt, hãy bấm C để lưu bản đồ trước.")
    return start, end

def weighted_a_star(draw, grid, start, end, epsilon=1e-5):
    """
    Weighted A* với trọng số tỷ lệ giữa heuristic và chi phí thực tế.
    f(n) = g(n) + (1 + h(n)/(g(n) + ε)) * h(n)
    """
    
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}

    g_score = {spot: float("inf") for row in grid for spot in row}
    f_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0

    h_start = h(start.get_pos(), end.get_pos())
    f_score[start] = g_score[start] + (1 + h_start / (g_score[start] + epsilon)) * h_start
    open_set_hash = {start}

    step_mode = True  # Mặc định: đi từng bước bằng Enter

    while not open_set.empty():
        if step_mode:
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            waiting = False
                        elif event.key == pygame.K_t:
                            step_mode = False
                            waiting = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    step_mode = True

        current = open_set.get()[2]
        print_state(current, g_score, f_score)
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

                heuristic = h(neighbor.get_pos(), end.get_pos())
                weight = 1 + heuristic / (temp_g_score + epsilon)
                f_score[neighbor] = temp_g_score + weight * heuristic

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False

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
                    weighted_a_star(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    elapsed = time.time() - start_time
                    print(f"⏱️ Thời gian tìm đường: {elapsed:.4f} giây")

                # C: lưu bản đồ ra file
                if event.key == pygame.K_c:
                    save_map(grid, start, end)

                # V: tải lại bản đồ từ file
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
#một điểm rất quan trọng trong lý thuyết thuật toán tìm đường. Trong phiên bản hiện tại của bạn, trọng số n là một hằng số số học (ví dụ n = 2), 
#nhưng trong lý thuyết Weighted A\*, trọng số có thể là một hàm số hoặc biến động theo từng trạng thái, chứ không nhất thiết phải là một số cố định.