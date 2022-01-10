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
        # if a change has occurred that could affect the best route, recalculate
        if self.change:
            # if there are riders or requests, get all possible routes, and find the shortest
            if self.riders or self.requests:
                routes = get_routes([self.pos()], self.riders, self.requests)
                shortest = shortest_route(self.pos(), routes, self.max_dist)
            # otherwise, go to the center of the board
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
    # if any riders' destinations or requests' starts are at the current location, exchange them
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
    # not done if any requests or riders remain (future requests checked in main())
    def done(self):
        return False if self.requests or self.riders else True

def get_routes(start, riders, requests):
    # create destinations list containing riders' destinations, as well as
    # start-end pairs for each pending request
    destinations = []
    for rider in riders:
        destinations.append({'dest': rider['end']})
    for request in requests:
        destinations.append({'start': request['start'], 'end': request['end']})
    # determine the total number of stops for the current riders and requests
    stop_count = 1
    for dest in destinations:
        if 'dest' in dest.keys():
            stop_count = stop_count + 1
        else:
            stop_count = stop_count + 2
    # reset worst to positive infinity before getting route permutations
    global worst
    worst = math.inf
    # get all permutations of the current riders' destinations & start-end pairs
    permutations = permute(start, destinations, stop_count)
    routes = []
    # convert route permutations into lists of [x, y] pairs
    for route in permutations:
        route_list = []
        for dest in route:
            route_list.append(dest['dest'])
        routes.append(route_list)
    return routes

# recursive permutation algorithm implementing decision tree pruning
def permute(start, stops, stop_count):
    global worst
    # base case
    if len(stops) == 1:
        # if the remaining stop is a start-end pair, convert it into two
        # corresponding destinations
        if 'start' in stops[0].keys():
            result = [{'dest': stops[0]['start']}, {'dest': stops[0]['end']}]
            route = start + [result[0]['dest'] + result[1]['dest']]
        else:
            result = stops
            route = start + [result[0]['dest']]
        # if the remaining stop constitutes the final stop of a permuted route, calculate
        # the route's length. If the length is less than the worst length encountered so far,
        # it becomes the new worst length
        if (len(route) == stop_count):
            length = route_length(route)
            if length < worst:
                worst = length
        return [result]
    permutations = []
    # for each stop in the route, remove it from the route, place it at the beginning,
    # and permute the remaining stops
    for i in range(len(stops)):
        first = stops[i]
        remaining = stops[:i] + stops[i+1:]
        # if the new 'start' is a start-end pair, convert the start & end to generic destinations,
        # and place the end destination in the array to be permuted. This ensures that every start destination always comes before its corresponding stop.
        if 'start' in first.keys():
            remaining.append({'dest': first['end']})
            first = {'dest': first['start']}
        new_start = [*start]
        new_start.append(first['dest'])
        # if the route comprised by the stops whose order has was determined earlier in this recursive branch is already longer than the worst full route encountered so far, prune the branch (no need for further recursion, we will definitely choose a different branch)
        if route_length(new_start) >= worst:
            continue
        # otherwise, contunue permuting
        permuted = permute(new_start, remaining, stop_count)
        for p in permuted:
            permutations.append([first] + p)
    return permutations

def route_length(route):
    distance = 0
    for i in range(len(route) - 1):
        distance = distance + calc_distance(route[i], route[i + 1])
    return distance

# function to choose the shortest route among several options, given a starting point
def shortest_route(start, routes, max):
    scores = []
    for route in routes:
        route.insert(0, start)
        dist = route_length(route)
        scores.append({'route': route, 'distance': dist})
    shortest_distance = max
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

# for each tick of time:
def tick(time, car, new_requests, more_requests):
    # tell the car about new requests arriving during this tick
    if new_requests != None:
        for i in range(len(new_requests)):
            car.add_request(new_requests[i])
    # if any requests start or rides end at the current location, exchange those passengers
    exchange = car.exchange()
    print('time: ', time)
    print('car: ', car.pos())
    print('riders: ', car.riders)
    print('requests: ')
    for request in car.requests:
        print(request)
    print('dropoffs: ', exchange['dropoffs'])
    print('pickups: ', exchange['pickups'])
    # if the car has no riders or pending requests, and no more requests will be added in the
    # future, the ride is done
    if car.done() and not more_requests:
        return 'DONE'
    print('-----------')
    # otherwise, move the car given its riders + pending requests + new requests
    car.move()
    print('====================================================')
    print('====================================================')
    return time + 1

def main(grid_y, grid_x, time_limit, req_list = None):
    # a grid is actually not necessary for my solution; it is only used by the car
    # Class to determine the center of the grid, which is the destination used if
    # it does not start with any riders or requests.
    grid = list([] for _ in range(grid_x))
    for x in range(grid_x):
        for y in range(grid_y):
            grid[x].append([x, y])
    time = 0
    car = Car(grid, 0, 0)
    for _ in range(time_limit):
        # for each tick, if there are new requests for that tick, given them to the car
        new_requests = req_list[time] if time in range(len(req_list)) else None
        # more_requests boolean used to determine if the simulation is over
        more_requests = False if time > len(req_list) - 1 else True
        next = tick(time, car, new_requests, more_requests)
        if next == 'DONE':
            print('finished driving in time t=', time)
            return
        else:
            time = next
    print('ran out of time...')
    return

# my solution reads requests from a JSON file, the path to which should be the 4th command line argument. The first three should be: grid length (x), grid length (y), time limit (in ticks)
if __name__ == "__main__":
    if len(sys.argv) != 5 or not sys.argv[1].isnumeric() or not sys.argv[2].isnumeric or not sys.argv[3].isnumeric():
        print('Usage:', sys.argv[0], ' <x length> <y length> <tick limit> <path to requests json>')
    else:
        file = open(sys.argv[4])
        data = json.load(file)
        requests = []
        for time in data:
            requests.append(data[time] or None)
        main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), requests)
