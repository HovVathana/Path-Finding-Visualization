import sys
import pygame
import queue
import heapq
import threading
from tkinter import *
from tkinter import messagebox
from pygame.locals import *

white = (250, 250, 250)
black = (47, 24, 22)
l_blue = (84, 181, 253)
d_blue = (33, 13, 241)
purple = (153, 17, 205)
yellow = (255, 241, 27)
size = 14


class Grid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def initGrid(self):
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill(black)
        pygame.display.set_caption('PATHFINDING DEMO')
        self.drawGrid()

    def drawGrid(self):
        x = 0
        y = 0
        w = self.width // size 
        for l in range(w):
            pygame.draw.aaline(self.screen, white, (0, y), (self.width, y))
            pygame.draw.aaline(self.screen, white, (x, 0), (x, self.height))
            x += size
            y += size

    def fillSquare(self, row, col, color):
        row_actual = row * size
        col_actual = col * size
        rec = pygame.Rect(col_actual, row_actual, size-1, size-1)
        pygame.draw.rect(self.screen, color, rec)

    def getCell(self, x, y):
        x -= (x % size)
        y -= (y % size)
        coord = (x, y)
        return coord

class Node(object):
    color = 'B'
    parent = (0, 0)
    g = sys.maxsize
    h = 0
    f = 0

class Search(object):
    def __init__(self, object, rows, cols, start, goal):
        self.gridQ = object
        self.goalFound = False
        self.rows = rows
        self.cols = cols
        self.start = start
        self.goal = goal
        self.matrix = [[Node() for i in range(rows)] for j in range(cols)]

    def setCell(self, x, y, color):
        self.matrix[x][y].g = sys.maxsize
        self.matrix[x][y].color = color

    def in_bounds(self, cur):
        i, j = cur
        if 0 <= i < self.rows and 0 <= j < self.cols:
            return True
        else:
            return False

    def get_neighbors(self, cur, directions):
        i, j = cur
        if directions == 8:
            adj = [(i-1, j), (i-1, j+1), (i, j + 1), (i + 1, j + 1), (i+1, j), (i+1, j-1), (i, j-1), (i-1, j-1),]
        elif directions == 4:
            adj = [(i, j + 1), (i + 1, j), (i, j - 1), (i - 1, j)]

        adj = filter(self.in_bounds, adj)
        return adj

    def bfs(self):
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                self.matrix[i][j].parent = (i, j)

        bfsQ = queue.Queue()
        bfsQ.put(self.start)
        self.goalFound = False

        self.matrix[self.start[0]][self.start[1]].g = 0

        while not bfsQ.empty():
            cur = bfsQ.get()

            if cur == self.goal:
                break

            for v in self.get_neighbors(cur, 4):
                i, j = v

                if self.matrix[i][j].color == 'W':
                    continue

                if self.matrix[i][j].g == sys.maxsize:
                    bfsQ.put(v)
                    self.matrix[i][j].g = self.matrix[cur[0]][cur[1]].g + 1
                    self.matrix[i][j].parent = cur
                    self.gridQ.put((v[0], v[1], d_blue))
                else:
                    self.gridQ.put((v[0], v[1], l_blue))

        self.backtrack(self.goal)

    def get_cost(self, cur, to):
        """Returns cost from one cell to another. Different values for diagonal or straight movement"""
        i1, j1 = cur
        i2, j2 = to
        if abs(i1 - i2) + (j1 - j2) == 1:
            return 1
        else:
            return 1.414

    def heuristic(self, cur, goal):
        # Heuristic for 8-directional diagonal movements
        non_diag = 1
        diag = 1.414
        dx = abs(cur[0] - goal[0])
        dy = abs(cur[1] - goal[1])
        return min(dx, dy) * diag + abs(dx - dy)

    def a_star(self):
        # New priority queue will be used as open list for A* search. Add start node to queue and declare
        # empty dic for closed list
        priQ = []
        heapq.heapify(priQ)
        heapq.heappush(priQ, (0, self.start))
        closed = {}

        s_i, s_j = self.start
        self.matrix[s_i][s_j].g = 0

        # While the priority queue still has elements to process
        while not len(priQ) == 0:

            # Get the value with the lowest 'f' value and add it to the closed list
            i, j = heapq.heappop(priQ)[1]
            closed[(i, j)] = True

            # Add this node to be colored in on pygame grid
            self.gridQ.put((i, j, l_blue))

            # Exit if goal node found
            if (i, j) == self.goal:
                self.goalFound = True
                break

            # Visit 8-directions from current cell (within boundaries)
            for v in self.get_neighbors((i, j), 8):
                row = v[0]
                col = v[1]

                # Skip cell if already processed in closed list or marked as wall
                if (row, col) in closed or self.matrix[row][col].color == 'W':
                    continue

                # Calculate the new cost from current cell to next
                n_cost = self.matrix[i][j].g + self.get_cost((i, j), v)
                cur_cost = self.matrix[row][col].g

                # Calculate h and f if not visited yet or new cost is less then the current cost
                if cur_cost == sys.maxsize or n_cost < cur_cost:

                    # Update cost of current cell and calculate h and f
                    self.matrix[row][col].g = n_cost
                    h = self.heuristic((row, col), self.goal)
                    f = n_cost + h

                    # Push this cell onto the priority queue with f as its priority and set parent
                    heapq.heappush(priQ, (f, (row, col)))
                    self.matrix[row][col].parent = (i, j)

                    # Color in cell as being processed
                    self.gridQ.put((row, col, d_blue))

        # After A* algorithm has completed, backtrack to the start to highlight the path taken
        self.backtrack(self.goal)

    def backtrack(self, cur):
        self.gridQ.put((cur[0], cur[1], yellow))
        while cur != self.start:
            cur = self.matrix[cur[0]][cur[1]].parent
            self.gridQ.put((cur[0], cur[1], purple))
        self.gridQ.put((cur[0], cur[1], yellow))

gridQ = queue.Queue()

row = (700, 50)
col = (700, 50)

s_r, s_c = 20, 20
g_r, g_c = 49, 49
algo = 'BFS'


def submit():
    global s_r, s_c, g_r, g_c, algo
    s_r = st_var1.get()
    s_c = st_var2.get()
    g_r = ed_var1.get()
    g_c = ed_var2.get()
    algo = opt_var.get()
    root.quit()
    root.destroy()


def on_closing():
    if messagebox.askokcancel('Quit', 'Do you want to quit?'):
        pygame.quit()
        sys.exit()
    
# tkinter part

root = Tk()
root.title('SETUP')

st_pos1 = list(range(50))
st_pos2 = list(range(50))
ed_pos1 = list(range(50))
ed_pos2 = list(range(50))

choice = ['BFS', 'A-STAR']

st_var1 = IntVar(root)
st_var1.set(st_pos1[0])

st_var2 = IntVar(root)
st_var2.set(st_pos2[0])

ed_var1 = IntVar(root)
ed_var1.set(ed_pos1[-1])

ed_var2 = IntVar(root)
ed_var2.set(ed_pos2[-1])

opt_var = StringVar(root)
opt_var.set(choice[0])


st_label = Label(root, text='Start (row, col): ')
ed_label = Label(root, text='End (row, col): ')
select = Label(root, text='Algorithm: ')
st_row = OptionMenu(root, st_var1, *st_pos1)
st_col = OptionMenu(root, st_var2, *st_pos2)
ed_row = OptionMenu(root, ed_var1, *ed_pos1)
ed_col = OptionMenu(root, ed_var2, *ed_pos2)
opt = OptionMenu(root, opt_var, *choice)
submit = Button(root, text='OK', command=submit)

select.grid(row=0, column=0, pady=0.5)
opt.grid(row=0, column=1, pady=0.5)
st_label.grid(row=1, pady=0.5)
st_row.grid(row=1, column=1, pady=0.5)
st_col.grid(row=1, column=2, pady=0.5)
ed_label.grid(row=2, pady=0.5)
ed_row.grid(row=2, column=1, pady=0.5)
ed_col.grid(row=2, column=2, pady=0.5)
submit.grid(row=3, columnspan=3, pady=0.5)
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()


myGrid = Grid(row[0], col[0])
myMatrix = Search(gridQ, row[1], col[1], (s_r, s_c), (g_r, g_c))

pygame.init()
myGrid.initGrid()

myGrid.fillSquare(s_r, s_c, yellow)
myGrid.fillSquare(g_r, g_c, yellow)

pos_x = 0
pos_y = 0
getWalls = True
fillCells = False

while getWalls:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
                pygame.quit()
            if event.key == pygame.K_SPACE:
                getWalls = False
        elif event.type == MOUSEBUTTONDOWN:
            fillCells = True
        elif event.type == MOUSEBUTTONUP:
            fillCells = False

        if fillCells:
            try:
                pos_x, pos_y = event.pos
                pos_x, pos_y = myGrid.getCell(pos_x, pos_y)
                rec = pygame.Rect(pos_x, pos_y, size, size)
                pygame.draw.rect(myGrid.screen, white, rec)
                myMatrix.setCell(pos_y // size, pos_x // size, 'W')
                pygame.display.update()
            except:
                pass
    pygame.display.flip()

if algo == 'BFS':
    t1 = threading.Thread(target=myMatrix.bfs())
elif algo == 'A-STAR':
    t1 = threading.Thread(target=myMatrix.a_star())

t1.start()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if not gridQ.empty():
        x, y, color = gridQ.get()

        myGrid.fillSquare(x, y, color)
        pygame.display.update()




