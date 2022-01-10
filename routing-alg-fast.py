import sys
import json
import math

worst = math.inf

class Car:
    def __init__(self, board, x_start = 0, y_start = 0, riders = [], requests = []):
        self.y = y_start
        self.x = x_start
        self.riders = riders
        self.requests = requests
        self.max_dist = math.inf
        self.center = [math.floor(len(board) / 2), math.ceil(len(board[0]) / 2)]
        self.dest = []
        self.change = True
    def pos(self):
        return [self.x, self.y]
    def move(self):
        if self.change:
            print('was a change, recalculating...')
            if self.riders or self.requests:
                routes = get_routes([self.pos()], self.riders, self.requests)
                shortest = shortest_route(self.pos(), routes, self.max_dist)
            else:
                shortest = [self.pos(), self.center]
            dest = shortest[1]
        else:
            dest = self.dest
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
        self.dest = dest
        self.change = False
        return move
    def add_request(self, request):
        self.requests.append(request)
        self.change = True
    def exchange(self):
        pickups, dropoffs = [], []
        remaining_riders, remaining_requests = [], []
        for request in self.requests:
            if request['start'] == self.pos():
                pickups.append(request['name'])
                self.change = True
                self.riders.append(request)
            else:
                remaining_requests.append(request)
        self.requests = remaining_requests
        for rider in self.riders:
            if rider['end'] == self.pos():
                dropoffs.append(rider['name'])
                self.change = True
            else: 
                remaining_riders.append(rider)
        self.riders = remaining_riders
        return {'pickups': pickups, 'dropoffs': dropoffs}
    def done(self, more_requests):
        return False if more_requests or self.requests or self.riders else True

def get_routes(start, riders, requests):
    destinations = []
    for rider in riders:
        destinations.append({'dest': rider['end']})
    for request in requests:
        destinations.append({'start': request['start'], 'end': request['end']})
    stop_count = 1
    for dest in destinations:
        if 'dest' in dest.keys():
            stop_count = stop_count + 1
        else:
            stop_count = stop_count + 2
    global worst
    worst = math.inf
    permutations = permute(start, destinations, stop_count)
    routes = []
    for route in permutations:
        route_list = []
        for dest in route:
            route_list.append(dest['dest'])
        routes.append(route_list)
    return routes

def permute(start, stops, stop_count):
    global worst
    if len(stops) == 1:
        if 'start' in stops[0].keys():
            result = [{'dest': stops[0]['start']}, {'dest': stops[0]['end']}]
            route = start + [result[0]['dest'] + result[1]['dest']]
        else:
            result = stops
            route = start + [result[0]['dest']]
        if (len(route) == stop_count):
            length = route_length(route)
            if length < worst:
                worst = length
        return [result]
    permutations = []
    for i in range(len(stops)):
        first = stops[i]
        remaining = stops[:i] + stops[i+1:]
        if 'start' in first.keys():
            remaining.append({'dest': first['end']})
            first = {'dest': first['start']}
        new_start = [*start]
        new_start.append(first['dest'])
        if route_length(new_start) > worst:
            continue
        permuted = permute(new_start, remaining, stop_count)
        for p in permuted:
            permutations.append([first] + p)
    return permutations

def route_length(route):
    distance = 0
    for i in range(len(route) - 1):
        distance = distance + calc_distance(route[i], route[i + 1])
    return distance

def shortest_route(start, routes, max):
    scores = []
    for route in routes:
        route.insert(0, start)
        dist = 0
        for i in range(len(route) - 1):
            dist = dist + calc_distance(route[i], route[i + 1])
        scores.append({'route': route, 'distance': dist})
    shortest_distance = max + 1
    best_route = None
    for route in scores:
        if route['distance'] < shortest_distance:
            shortest_distance = route['distance']
            best_route = route['route']
    return best_route

def calc_distance(a, b):
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
    if car.pos() not in visited:
        visited.append(car.pos())
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
    car = Car(grid, 0, 0)
    for _ in range(time_limit):
        new_requests = req_list[time] if time in range(len(req_list)) else None
        more_requests = False if time > len(req_list) - 1 else True
        next = tick(time, car, new_requests, more_requests)
        if next == 'DONE':
            print('finished driving in time t=', time)
            return
        else:
            time = next

visited = []

if __name__ == "__main__":
    file = open(sys.argv[4])
    data = json.load(file)
    requests = []
    for time in data:
        requests.append(data[time] or None)
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), requests)
