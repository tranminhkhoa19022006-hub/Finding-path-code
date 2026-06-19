import pygame 
import math
from queue import PriorityQueue 
import time
import random

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

#Hàm vẽ ngẫu nhiên vật cản theo tỷ lệ
def generate_random_barriers(grid, barrier_percent, start=None, end=None):
    """
    Sinh vật cản ngẫu nhiên chiếm barrier_percent % tổng số ô trên bản đồ.
    Tránh vị trí start và end.
    """
    total_rows = len(grid)
    total_cells = total_rows * total_rows
    barrier_count = int(total_cells * barrier_percent / 100)
    print(f"🎲 Đang tạo bản đồ ngẫu nhiên ({barrier_percent:.1f}% vật cản)...")

    # Reset toàn bộ map
    for row in grid:
        for spot in row:
            spot.reset()

    # Giữ lại start, end (nếu có)
    if start:
        start.make_start()
    if end:
        end.make_end()

    # Sinh ngẫu nhiên vị trí vật cản
    all_positions = [(r, c) for r in range(total_rows) for c in range(total_rows)]
    if start:
        all_positions.remove(start.get_pos())
    if end:
        all_positions.remove(end.get_pos())

    random.shuffle(all_positions)
    for i in range(min(barrier_count, len(all_positions))):
        r, c = all_positions[i]
        grid[r][c].make_barrier()

    print(f"✅ Đã tạo {barrier_count} ô vật cản ({barrier_percent:.1f}%).")


def ARA_star(draw, grid, start, end, epsilon_start=5, epsilon_step=1.0):
    """
    ARA* (Anytime Repairing A*)
    Cải thiện dần lời giải bằng cách giảm epsilon và tái sử dụng dữ liệu tìm kiếm.
    - Giữ nguyên khả năng chọn heuristic_type toàn cục
    - Mỗi epsilon vẽ đường khác màu
    - Hiển thị epsilon & heuristic trên màn hình
    - Cuối cùng in bảng tổng hợp kết quả (chi phí & thời gian mỗi epsilon)
    """

    import time
    global heuristic_type
    epsilon = epsilon_start
    count = 0
    open_set = PriorityQueue()
    came_from = {}
    incons = set()

    g_score = {spot: float("inf") for row in grid for spot in row}
    f_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score[start] = g_score[start] + epsilon * h(start.get_pos(), end.get_pos())
    open_set.put((f_score[start], count, start))
    open_set_hash = {start}

    best_path = None
    best_cost = float("inf")

    step_mode = True  # đi từng bước
    results = []  # lưu kết quả từng epsilon

    path_colors = [
        (200, 100, 255),  # tím nhạt
        (100, 200, 255),  # xanh lam nhạt
        (255, 255, 100),  # vàng
        (100, 255, 150),  # xanh lá nhạt
        (255, 150, 150)   # hồng nhạt
    ]
    color_index = 0

    pygame.font.init()
    font = pygame.font.SysFont("arial", 20)

    def draw_info():
        """Vẽ thông tin epsilon và heuristic hiện tại lên màn hình"""
        text_surface = font.render(
            f"Epsilon = {epsilon:.2f}    Heuristic = {heuristic_type.capitalize()}",
            True,
            (0, 102, 204)
        )
        WIN.blit(text_surface, (10, 10))

    def draw_path_with_color(came_from, current, color):
        """Tô đường đi bằng màu cụ thể"""
        while current in came_from:
            current = came_from[current]
            if not current.is_start():
                current.color = color
            draw()
            draw_info()
            pygame.display.update()

    # === Bắt đầu vòng lặp epsilon ===
    while epsilon >= 1.0:
        print(f"\n🔁 Đang chạy với epsilon = {epsilon:.2f}")
        closed = set()
        start_time = time.time()

        path_found = False
        while not open_set.empty():
            draw()
            draw_info()
            pygame.display.update()

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
            open_set_hash.remove(current)
            closed.add(current)

            if current == end:
                path_found = True
                color = path_colors[color_index % len(path_colors)]
                draw_path_with_color(came_from, end, color)
                end.make_end()
                best_path = came_from.copy()
                best_cost = g_score[end]
                elapsed = time.time() - start_time
                results.append((epsilon, best_cost, elapsed))
                color_index += 1
                break

            for neighbor in current.neighbors:
                r1, c1 = current.get_pos()
                r2, c2 = neighbor.get_pos()
                step_cost = math.sqrt(2) if (r1 != r2 and c1 != c2) else 1
                temp_g = g_score[current] + step_cost

                if temp_g < g_score[neighbor]:
                    g_score[neighbor] = temp_g
                    came_from[neighbor] = current
                    f_score[neighbor] = g_score[neighbor] + epsilon * h(neighbor.get_pos(), end.get_pos())

                    if neighbor not in closed:
                        if neighbor not in open_set_hash:
                            count += 1
                            open_set.put((f_score[neighbor], count, neighbor))
                            open_set_hash.add(neighbor)
                            neighbor.make_open()
                    else:
                        incons.add(neighbor)

            draw()
            draw_info()
            pygame.display.update()

            if current != start:
                current.make_closed()

        # Nếu không tìm thấy đường, vẫn giảm epsilon
        if not path_found:
            print(f"⚠️ Không tìm thấy đường cho ε={epsilon:.2f}")
            elapsed = time.time() - start_time
            results.append((epsilon, None, elapsed))

        if epsilon <= 1.0:
            break

        # Giảm epsilon
        epsilon = max(1.0, epsilon - epsilon_step)

        # Cập nhật OPEN từ incons
        for n in incons:
            f_score[n] = g_score[n] + epsilon * h(n.get_pos(), end.get_pos())
            if n not in open_set_hash:
                count += 1
                open_set.put((f_score[n], count, n))
                open_set_hash.add(n)
        incons.clear()

    # === In kết quả tổng hợp ===
    print("\n📊 KẾT QUẢ TỔNG HỢP:")
    for eps, cost, t in results:
        if cost is not None:
            print(f"Với ε = {eps:.2f}: Chi phí đường đi = {cost:.3f} | Thời gian = {t:.4f} giây")
        else:
            print(f"Với ε = {eps:.2f}: ❌ Không tìm thấy đường | Thời gian = {t:.4f} giây")

    if best_path:
        end.make_end()
        draw()
        draw_info()
        pygame.display.update()
        print("\n🏁 Hoàn tất ARA*.")
        return True

    print("\n❌ Không tìm thấy đường đi trong toàn bộ quá trình.")
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
                    ARA_star(lambda: draw(win, grid, ROWS, width), grid, start, end)
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
                
                # G: Tạo vật cản ngẫu nhiên
                if event.key == pygame.K_g:
                    try:
                        barrier_percent = float(input("Nhập tỷ lệ vật cản (ví dụ 20 cho 20%): "))
                        generate_random_barriers(grid, barrier_percent, start, end)
                    except ValueError:
                        print("⚠️ Giá trị không hợp lệ. Hãy nhập số (vd: 25).")


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