import os
import random
import statistics
import heapq
from collections import deque
from copy import deepcopy

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
    def __init__(self, vehicles, remaining_rides, accScore=0, parent=None):
        self.vehicles = vehicles
        self.remaining_rides = remaining_rides
        self.score = accScore
        self.parent = parent

    def __str__(self):
        vehicles_str = "\n".join(str(v) for v in self.vehicles)
        rides_str = ", ".join(str(r.id) for r in self.remaining_rides)
        return f"Score: {self.score}\nVehicles:\n{vehicles_str}\nRemaining rides: [{rides_str}]"
    
    def path(self):
        node = self
        result = []
        while node.parent is not None:
            result.append(node.parent)
            node = node.parent
        result.reverse()
        return result
    

#---------MENU---------#
# Extract data from Input data set

input_folder = "inputs"

# Get all files in the folder (checks if the path file contains the folder)
files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

# Show menu
print("\nAvailable input files:")
for i, file in enumerate(files):
    print(f"{i + 1}. {file}")

# Choose file (also verifies if input is a number in the correct range)
while True:
    try:
        choice = int(input("Select a file by number: ")) - 1
        if 0 <= choice < len(files):
            break
        else:
            print("Invalid number, try again.")
    except ValueError:
        print("Please enter a number.")

# Get full path
name_input = os.path.join(input_folder, files[choice])

print(f"\nSelected: {name_input}")

print("\nAlgorithm")
print("1. Best First Search (Greedy)")
print("2. Weighted A* (default weight is 1)")

while True:
    try:
        algorithm = int(input("Choose algorithm: "))
        if algorithm == 1:
            break
        if algorithm == 2:
            weight = int(input("Choose a weight for the A*: "))

            while (weight < 1):
                weight = int(input("Weight shoud be >= 1*: "))
            break
        else:
            print("Invalid choice.")
    except ValueError:
        print("Enter a number.")



# Choose mode of execution (either a single run or analysis with multiple runs)

print("\nExecution mode:")
print("1. Single run")
print("2. Multiple runs (analysis)")

while True:
    try:
        mode = int(input("Choose mode: "))
        if mode in [1, 2]:
            break
        else:
            print("Invalid choice.")
    except ValueError:
        print("Enter a number.")

n_runs = 1
if mode == 2:
    while True:
        try:
            n_runs = int(input("Number of runs: "))
            if n_runs > 0:
                break
            else:
                print("Must be > 0.")
        except ValueError:
            print("Enter a number.")

filename = os.path.basename(name_input) # gets only the name of the file, removing the path
base, _ = os.path.splitext(filename) # removes the file extension
name_output = os.path.join("outputs", base + ".out") #creates the output file, with correct path and file extension

fh = open(name_input, "r")
R, C, F, N, B, T = map(int, fh.readline().split())

rides = []
for i in range(N):
    a, b, x, y, s, f = map(int, fh.readline().split())
    rides.append(Ride(i, a, b, x, y, s, f))

vehicles = [Vehicle(i) for i in range(F)]

fh.close()




#-------Operators---------#

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


# Intead of choosing globally the best ride, which would favour vehicles 
# already used, since they would technically be closer to the ride start most times,
# it chooses locally the best ride for each vehicle, being closer to
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
def greedy_search(state, bonus, T):

    while True:
        progress = False
        
        random.shuffle(state.vehicles) #shuffles vehicles each iteration

        for vehicle in state.vehicles:
            best_ride = choose_best_ride_for_vehicle(state, vehicle, bonus, T)

            if best_ride is not None:
                apply_operator(state, (vehicle.id, best_ride.id), bonus, T)
                progress = True

        if not progress:
            break

    return state


#A*
def A_star(initialstate, bonus, T, weight=1):
    rides_heap = []
    counter = 0

    #heapq.heappush(queue, (-f_value, counter, new_state))
    heapq.heappush(rides_heap, (0, counter, initialstate))
    counter += 1

    best_node = initialstate

    while (len(rides_heap) > 0):
        f, _, currentState = heapq.heappop(rides_heap)  # retira o melhor estado

        if currentState.score > best_node.score:
            best_node = currentState
        
        if not currentState.remaining_rides:            # goal atingido
            break

        vehicle_queue = deque(currentState.vehicles)

        # Fazer a expansão do nível seguinte
        for ride in currentState.remaining_rides:
            
            found = False
            for _ in range(len(vehicle_queue)):
                currentVehicle = vehicle_queue[0]
                vehicle_queue.rotate(-1)
                if currentVehicle.can_complete_ride(ride, T):
                    found = True
                    break
                vehicle_queue.append(currentVehicle)

            if not found:
                continue

            new_state = deepcopy(currentState) #copia o estado atua
            new_vehicle = next(v for v in new_state.vehicles if v.id == currentVehicle.id)
            apply_operator(new_state, (new_vehicle.id, ride.id), bonus, T)
            f_new = - (evaluate(new_state.score, new_vehicle, ride, weight))
            heapq.heappush(rides_heap, (f_new, counter, new_state))
            counter += 1

    return best_node



def evaluate(score, vehicle, ride, weight):
    dist_to_start = vehicle.distance_to_ride_start(ride)
    ride_dist = ride.distance()
    arrival = vehicle.time + dist_to_start
    wait_time = max(0, ride.s - arrival)
    heuristic = ride_dist - dist_to_start - wait_time    #heuristic (from Scoring section + using wait_time to penalize waiting)
    result = score + weight*heuristic

    return result



#-----solve problem------#

best_state = None
best_score = -1
scores = []

print()

for i in range(n_runs):
    print(f"Run {i+1}/{n_runs}", end="\r") # track progress
    # recreate vehicles and state each run (necessary since they're modified with each run of the algorithm)
    vehicles = [Vehicle(i) for i in range(F)]
    state = HashCodeState(vehicles, list(rides))

    if (algorithm == 1):
        result = greedy_search(state, B, T)
    elif (algorithm == 2):
        result = A_star(state, B, T, weight)
        print("Melhor score:", result.score)
        print("Caminho de operadores:", result.path())

    scores.append(result.score)

    if result.score > best_score:
        best_score = result.score
        best_state = result
        
print()

final_state = best_state


#output data
fh = open(name_output, "w")
for v in final_state.vehicles:
    v_rides = " ".join(str(r) for r in v.assigned_rides)
    fh.write(f"{len(v.assigned_rides)} {v_rides}\n")

fh.close()

print(f"\nOutput written to: {name_output}")



# Analysis of the results or score for the run
if n_runs > 1:
    avg = sum(scores) / len(scores)
    std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
    min_score = min(scores)
    max_score = max(scores)

    print(f"\nAverage score: {avg:.2f}")
    print(f"Std deviation: {std_dev:.2f}")
    print(f"Min score: {min_score}")
    print(f"Max score: {max_score}")
    
else:
    print(f"\nScore for this run: {final_state.score}")






# Old stratagy of choosing best vehicle for ride (resulted in same set of vehicles getting all the rides)
"""
def choose_best_operator(state, bonus, T):  #choose best vehicle/ride pair for highest value
    best_op = None
    best_value = float('-inf')
    
    safe_replacement_op = None   # in case there is no Best operator, this one will be used instead

    for vehicle in state.vehicles:        #the for loops generate the operators (meaning the vehicle/ride pairs)
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



#greedy
def greedy_search(state, bonus, T):

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
 
#goal definition
def goal_state_func(state):
    return len(state.remaining_rides) == 0