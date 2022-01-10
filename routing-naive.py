import sys
import json
import math

class Car:
    def __init__(self, board, x_start = 0, y_start = 0, riders = [], requests = []):
        self.y = y_start
        self.x = x_start
        self.riders = riders
        self.requests = requests
        self.max_dist = math.inf
        self.center = [math.floor(len(board) / 2), math.ceil(len(board[0]) / 2)]
    def pos(self):
        return [self.x, self.y]
    def move(self):
        if self.riders or self.requests:
            routes = get_routes(self.riders, self.requests)
            print(routes)
            shortest = shortest_route(self.pos(), routes, self.max_dist)
        else:
            shortest = [self.center]
        print('shortest:')
        print(shortest)
        dest = shortest
        print('next dest: ')
        print(dest)
        if self.x < dest[0]:
            move = [1, 0]
        elif self.x > dest[0]:
            move = [-1, 0]
        elif self.x == dest[0]:
            if self.y < dest[1]:
                move = [0, 1]
            elif self.y > dest[1]:
                move = [0, -1]
            elif self.y == dest[1]:
                print('ERROR')
                return
        self.x = self.x + move[0]
        self.y = self.y + move[1]
        return move
    def add_request(self, request):
        self.requests.append(request)
    def exchange(self):
        pickups, dropoffs = [], []
        remaining_riders, remaining_requests = [], []
        for request in self.requests:
            if request['start'] == self.pos():
                pickups.append(request['name'])
                self.riders.append(request)
            else:
                remaining_requests.append(request)
        self.requests = remaining_requests
        for rider in self.riders:
            if rider['end'] == self.pos():
                dropoffs.append(rider['name'])
            else: 
                remaining_riders.append(rider)
        self.riders = remaining_riders
        return {'pickups': pickups, 'dropoffs': dropoffs}
    def done(self, more_requests):
        return False if more_requests or self.requests or self.riders else True

def get_routes(riders, requests):
    destinations = []
    for rider in riders:
        destinations.append(rider['end'])
    for request in requests:
        destinations.append(request['start'])
    return destinations

def permute(stops):
    if len(stops) == 1:
        return [stops]
    permutations = []
    for i in range(len(stops)):
        first = stops[i]
        remaining = [*stops]
        del remaining[i]
        for permutation in permute(remaining):
            permutations.append([first] + permutation)
    return permutations

def shortest_route(start, routes, max):
    scores = []
    for route in routes:
        print('calcing distance for:')
        print(route)
        dist = calc_distance(start, route)
        scores.append({'route': route, 'distance': dist})
    shortest_distance = max + 1
    for route in scores:
        if route['distance'] < shortest_distance:
            shortest_distance = route['distance']
            best_route = route['route']
    return best_route

def calc_distance(a, b):
    print('calc distance:')
    print(a)
    print(b)
    dist_x = abs(a[0] - b[0])
    dist_y = abs(a[1] - b[1])
    return dist_x + dist_y

def tick(time, car, new_requests, more_requests):
    if new_requests != None:
        for i in range(len(new_requests)):
            car.add_request(new_requests[i])
    exchange = car.exchange()
    print('time: ', time)
    print('car: ', car.pos())
    print('riders: ', car.riders)
    print('requests: ')
    for request in car.requests:
        print(request)
    print('dropoffs: ', exchange['dropoffs'])
    print('pickups: ', exchange['pickups'])
    if car.done(more_requests):
        return 'DONE'
    print('-----------')
    car.move()
    print('====================================================')
    print('====================================================')
    return time + 1

def main(grid_y, grid_x, time_limit, req_list = None):
    grid = list([] for _ in range(grid_x))
    for x in range(grid_x):
        for y in range(grid_y):
            grid[x].append([x, y])
    time = 0
    car = Car(grid, 0, 5)
    for _ in range(time_limit):
        new_requests = req_list[time] if time in range(len(req_list)) else None
        more_requests = False if time > len(req_list) - 1 else True
        next = tick(time, car, new_requests, more_requests)
        if next == 'DONE':
            print('finished driving')
            return
        else:
            time = next

if __name__ == "__main__":
    file = open(sys.argv[4])
    data = json.load(file)
    requests = []
    for time in data:
        requests.append(data[time] or None)
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), requests)
