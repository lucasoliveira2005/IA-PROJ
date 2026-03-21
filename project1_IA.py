#definitions
class Ride:
    def __init__(self, ride_id, start_row, start_col, end_row, end_col, earliest_start, latest_finish):
        self.id = ride_id
        self.a = start_row
        self.b = start_col
        self.x = end_row
        self.y = end_col
        self.s = earliest_start
        self.f = latest_finish

    def distance(self):
        return abs(self.a - self.x) + abs(self.b - self.y)
    
    def __str__(self):
        return f"Ride({self.id}: [{self.a}, {self.b}] --> [{self.x}, {self.y}], start={self.s}, finish={self.f})"

class Vehicle:
    def __init__(self, vehicle_id, row=0, col=0, time=0):
        self.id = vehicle_id
        self.row = row
        self.col = col
        self.time = time
        self.assigned_rides = []
        
    def distance_to_ride_start(self, ride):
        return abs(self.row - ride.a) + abs(self.col - ride.b)

    def earliest_possible_start(self, ride):
        arrival_at_start = self.time + self.distance_to_ride_start(ride)
        return max(arrival_at_start, ride.s)

    def finish_time(self, ride):
        return self.earliest_possible_start(ride) + ride.distance()

    def can_complete_ride(self, ride, T):
        return self.finish_time(ride) <= ride.f and self.finish_time(ride) <= T


    def __str__(self):
        return f"Vehicle({self.id}, pos=({self.row}, {self.col}), time={self.time}, rides={self.assigned_rides})"

class HashCodeState:
    def __init__(self, vehicles, remaining_rides, score=0):
        self.vehicles = vehicles
        self.remaining_rides = remaining_rides
        self.score = score

    def __str__(self):
        vehicles_str = "\n".join(str(v) for v in self.vehicles)
        rides_str = ", ".join(str(r.id) for r in self.remaining_rides)
        return f"Score: {self.score}\nVehicles:\n{vehicles_str}\nRemaining rides: [{rides_str}]"



#extract data from Input data set
name_input = str(input("Filename of Input data set (with file extension, for example: .txt): "))
name_output = str(input("Filename of Submission file (with file extension, for example: .txt): "))

fh = open(name_input, "r")
R, C, F, N, B, T = map(int, fh.readline().split())

rides = []
for i in range(N):
    a, b, x, y, s, f = map(int, fh.readline().split())
    rides.append(Ride(i, a, b, x, y, s, f))

vehicles = [Vehicle(i) for i in range(F)]
initial_state = HashCodeState(vehicles, rides)

fh.close()




#operators
def apply_operator(state, operator, bonus, T):
    vehicle_id, ride_id = operator

    vehicle = next(v for v in state.vehicles if v.id == vehicle_id)
    ride = next(r for r in state.remaining_rides if r.id == ride_id)

    start_time = vehicle.earliest_possible_start(ride)
    finish_time = vehicle.finish_time(ride)

    if finish_time > ride.f or finish_time > T:
        return None

    earned = ride.distance()
    if start_time == ride.s:
        earned += bonus

    vehicle.row = ride.x
    vehicle.col = ride.y
    vehicle.time = finish_time
    vehicle.assigned_rides.append(ride.id)

    state.remaining_rides.remove(ride)
    state.score += earned

    return state

"""
def choose_best_operator(state, bonus, T):  #choose best vehicule/ride pair for highest value
    best_op = None
    best_value = float('-inf')
    
    safe_replacement_op = None   # in case there is no Best operator, this one will be used instead

    for vehicle in state.vehicles:        #the for loops generate the operators (meaning the vehicule/ride pairs)
        for ride in state.remaining_rides:
            if vehicle.can_complete_ride(ride, T):
                
                if safe_replacement_op is None:     # save first feasible operator
                    safe_replacement_op = (vehicle.id, ride.id)
                
                dist_to_start = vehicle.distance_to_ride_start(ride)
                ride_dist = ride.distance()
                arrival = vehicle.time + dist_to_start
                wait_time = max(0, ride.s - arrival)
                
                value = ride_dist - dist_to_start - wait_time    #heuristic (from Scoring section + using wait_time to penalize waiting)
                if arrival <= ride.s:
                    value += bonus

                if value > best_value:
                    best_value = value
                    best_op = (vehicle.id, ride.id)
    
    if best_op is not None:
        return best_op

    return safe_replacement_op
"""

"""
#greedy
def greedy_search(initial_state, bonus, T):
    state = initial_state

    while True:
        op = choose_best_operator(state, bonus, T)
        if op is None:  # in case there are no feasible operators
            break

        new_state = apply_operator(state, op, bonus, T)
        if new_state is None:
            break

        state = new_state

    return state
"""

# Intead of choosing globally the best ride, which would favour vehicules 
# already used, since they would technically be closer to the ride start most times,
# it chooses locally the best ride for each vehicule, being closer to
# a parallel scheduler and more efficient overall
def choose_best_ride_for_vehicle(state, vehicle, bonus, T):
    best_ride = None
    best_value = float('-inf')

    for ride in state.remaining_rides:
        if vehicle.can_complete_ride(ride, T):

            dist_to_start = vehicle.distance_to_ride_start(ride)
            ride_dist = ride.distance()
            arrival = vehicle.time + dist_to_start
            wait_time = max(0, ride.s - arrival)

            value = ride_dist - dist_to_start - wait_time    #heuristic (from Scoring section + using wait_time to penalize waiting)

            if arrival <= ride.s:
                value += bonus

            if value > best_value:
                best_value = value
                best_ride = ride

    return best_ride

#greedy
def greedy_search(initial_state, bonus, T):
    state = initial_state

    while True:
        progress = False

        for vehicle in state.vehicles:
            best_ride = choose_best_ride_for_vehicle(state, vehicle, bonus, T)

            if best_ride is not None:
                apply_operator(state, (vehicle.id, best_ride.id), bonus, T)
                progress = True

        if not progress:
            break

    return state


#solve problem
final_state = greedy_search(initial_state, B, T)


#output data
fh = open(name_output, "w")
for v in final_state.vehicles:
    v_rides = " ".join(str(r) for r in v.assigned_rides)
    fh.write(f"{len(v.assigned_rides)} {v_rides}\n")

fh.close()




#If we need/want to use BFS/DFS/A*
"""
#definition of Tree Node for states
class TreeNode:

    def __init__(self, state, parent=None, operator=None, cost=0, depth=0):
        self.state = state
        self.parent = parent
        self.operator = operator
        self.cost = cost
        self.depth = depth

    def path(self):
        node = self
        result = []

        while node.parent is not None: #go up the tree to each parent from goal node
            result.append(node.operator)
            node = node.parent

        result.reverse() #order from root to goal node
        return result
    
    
#goal definition
def goal_state_func(state):
    return len(state.remaining_rides) == 0

"""


