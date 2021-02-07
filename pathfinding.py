import copy
import heapq

class Maze:
    fileName = ''
    map = []  # 2차원 int 배열
    start = []
    dest = []
    key = []
    num = 0
    height = 0
    width = 0
    visited = []  # 노드 방문 확인
    isfrom = []  # 부모 노드 위치 (backtracking 시 사용)
    dx, dy = [1, 0, 0, -1], [0, 1, -1, 0]  # 하 우 좌 상
    route = []
    time = 0
    isFound = False  # ids용

    def __init__(self, fileName):
        self.fileName = fileName
        f = open(fileName + ".txt", 'r')
        line = f.readline()
        self.num, self.height, self.width = map(int, line.split(' '))
        while True:
            line = f.readline().split()  # str list로 되어있음
            if not line:
                break
            line = list(map(int, list(line[0])))  # str만 추출 후 개개 chr로 분리, int 변환 mapping 후 다시 list로
            self.map.append(line)
            for i in range(0, len(line)):
                if line[i] == 3:  # starting point
                    self.start = [len(self.map) - 1, i]
                if line[i] == 4:  # destination point
                    self.dest = [len(self.map) - 1, i]
                if line[i] == 6:  # key point >= 0
                    self.key += [[len(self.map) - 1, i], ]

        self.visited = [[0 for x in range(self.width)] for y in range(self.height)]
        self.isfrom = [[[-1, -1] for x in range(self.width)] for y in range(self.height)]

    def mazeEscape(self, methodName):
        maze = copy.deepcopy(self.map)
        self.time = 0
        srcDes = [self.start] + self.key + [self.dest]

        if methodName == 'BFS':
            escapeFunc = self.bfs
        elif methodName == 'IDS':
            escapeFunc = self.ids
        elif methodName == 'GBFS':
            escapeFunc = self.gbfs
        elif methodName == 'A_star':
            escapeFunc = self.a_star

        for x in range(len(srcDes) - 1):
            escapeFunc(maze, self.time, srcDes[x], srcDes[x + 1])
            self.setRoute(maze, srcDes[x], srcDes[x + 1])
            self.visited = [[0 for x in range(self.width)] for y in
                            range(self.height)]  # s -> key1, key1 -> key2 ... 매번 초기화

        for x in range(len(self.route)):
            maze[self.route[x][0]][self.route[x][1]] = 5

        self.writeAnswer(maze, self.time, len(self.route), methodName)
        self.route = []  # route 초기화, 꼭 해주어야함

    def bfs(self, maze=0, time=0, startPt=0, endPt=0):
        queue = [startPt]
        self.visited[startPt[0]][startPt[1]] = 1

        while queue:
            x, y = queue.pop(0)

            for i in range(4):
                nx = x + self.dx[i]
                ny = y + self.dy[i]
                if 0 <= nx < self.height and 0 <= ny < self.width:
                    if self.visited[nx][ny] == 0 and maze[nx][ny] != 1 and maze[nx][ny] != 3:
                        self.time += 1
                        if self.isfrom[nx][ny] == [-1, -1]:  # 처음만 변경 가능, 추후에 변경 불가
                            self.isfrom[nx][ny] = [x, y]
                        self.visited[nx][ny] = 1
                        if [nx, ny] == endPt:
                            return
                        queue.append([nx, ny])

    def ids(self, maze, time, startPt, endPt):
        maxDepth = 1
        depth = 0
        self.isFound = False
        while True:
            self.visited = [[0 for x in range(self.width)] for y in range(self.height)]
            self.isfrom = [[[-1, -1] for x in range(self.width)] for y in range(self.height)]
            self.idsEx(maze, time, startPt, endPt, maxDepth)
            if self.isFound:
                break
            maxDepth += 1  # +1 is too slow, for fast search please change it to " *= 2 "

    def idsEx(self, maze, time, startPt, endPt, maxDepth):
        stack = [startPt]
        self.visited[startPt[0]][startPt[1]] = 1

        while stack:
            x, y = stack.pop()  # top의 원소 제거

            for i in range(4):
                nx = x + self.dx[i]
                ny = y + self.dy[i]
                if 0 <= nx < self.height and 0 <= ny < self.width:
                    if self.visited[nx][ny] == 0 and maze[nx][ny] != 1 and maze[nx][ny] != 3:
                        self.time += 1
                        if self.isfrom[nx][ny] == [-1, -1]:  # 처음만 변경 가능, 추후에 변경 불가
                            self.isfrom[nx][ny] = [x, y]
                        self.visited[nx][ny] = self.visited[x][y] + 1
                        if [nx, ny] == endPt:
                            self.isFound = True
                            return
                        if self.visited[nx][ny] < maxDepth:
                            stack.append([nx, ny])
            '''
            # There are used for debugging, please install and import pprint
            print(maxDepth)
            pprint.pprint(self.visited)
            print("")
            '''

    def gbfs(self, maze, time, startPt, endPt):
        queue = [(self.getHx(startPt, endPt), startPt)]
        self.visited[startPt[0]][startPt[1]] = 1

        while queue:
            x, y = (heapq.heappop(queue))[1]  # (hx, [x, y]) 형태

            for i in range(4):
                nx = x + self.dx[i]
                ny = y + self.dy[i]
                if 0 <= nx < self.height and 0 <= ny < self.width:
                    if self.visited[nx][ny] == 0 and maze[nx][ny] != 1 and maze[nx][ny] != 3:
                        self.time += 1
                        if self.isfrom[nx][ny] == [-1, -1]:  # 처음만 변경 가능, 추후에 변경 불가
                            self.isfrom[nx][ny] = [x, y]
                        self.visited[nx][ny] = 1
                        if [nx, ny] == endPt:
                            return
                        heapq.heappush(queue, (self.getHx([nx, ny], endPt), [nx, ny]))

    def a_star(self, maze, time, startPt, endPt):
        queue = [(self.getFx(startPt, endPt), startPt)]
        self.visited[startPt[0]][startPt[1]] = 1

        while queue:
            x, y = (heapq.heappop(queue))[1]  # (fx, [x, y]) 형태

            for i in range(4):
                nx = x + self.dx[i]
                ny = y + self.dy[i]
                if 0 <= nx < self.height and 0 <= ny < self.width:
                    if self.visited[nx][ny] == 0 and maze[nx][ny] != 1 and maze[nx][ny] != 3:
                        self.time += 1
                        if self.isfrom[nx][ny] == [-1, -1]:  # 처음만 변경 가능, 추후에 변경 불가
                            self.isfrom[nx][ny] = [x, y]
                        self.visited[nx][ny] = self.visited[x][y] + 1
                        if [nx, ny] == endPt:
                            return
                        heapq.heappush(queue, (self.getFx([nx, ny], endPt), [nx, ny]))

    def setRoute(self, maze, startPt, endPt):  # 이동한 최소 경로
        x, y = self.isfrom[endPt[0]][endPt[1]]
        while True:
            self.route += [[x, y]]
            x, y = self.isfrom[x][y]
            if [x, y] == startPt:
                if maze[x][y] == 6:  # key를 먹고서, 다시 출발하는 경우에는 key를 새지 않음 (pdf와 다름)
                    self.route += [[x, y]]
                    break
                else:
                    break

        self.isfrom = [[[-1, -1] for x in range(self.width)] for y in range(self.height)]  # 다음 사용을 위해 초기화

    def getHx(self, pointA, pointB):  # return the Manhattan distance (heuristic)
        return abs(pointA[0] - pointB[0]) + abs(pointA[1] - pointB[1])

    def getFx(self, pointA, pointB): # return f(x) for A star ( f = g + h )
        return self.visited[pointA[0]][pointA[1]] + self.getHx(pointA, pointB)

    def writeAnswer(self, maze, time, length, algo):
        f = open(self.fileName + "_" + algo + "_output.txt", 'w')
        for x in range(self.height):
            f.write("".join(map(str, maze[x])) + '\n')
        f.write('---\n')
        f.write('length=' + str(length) + '\n')
        f.write('time=' + str(time) + '\n')


if __name__ == "__main__":
    mazeInput = input("Name of maze file: ")
    mz = Maze(mazeInput)
    mz.mazeEscape("BFS")
    mz.mazeEscape("GBFS")
    mz.mazeEscape("A_star")
    mz.mazeEscape("IDS")
    print("finished")
