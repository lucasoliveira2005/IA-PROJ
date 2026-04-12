import os
import random
import statistics
import time as run_time
import sys

#-------Definitions-------#
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



#-------MENU-------#
# Extract data from Input datase

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
filename = os.path.basename(name_input) # gets only the name of the file, removing the path
base, _ = os.path.splitext(filename) # removes the file extension
name_output = os.path.join("outputs", base + ".out") # creates the output file, with correct path and file extensio

# Opens and extracts file dat
fh = open(name_input, "r")
R, C, F, N, B, T = map(int, fh.readline().split())


# Large number of rides makes exhaustive or tree-based search (A*, Beam)
# computationally expensive or infeasible, so user should be warned.
# The limits are arbitrary, but these are relatively safe options
heavy_file = (N * F > 20000) or (N > 1500)

rides = []
for i in range(N):
    a, b, x, y, s, f = map(int, fh.readline().split())
    rides.append(Ride(i, a, b, x, y, s, f))
vehicles = [Vehicle(i) for i in range(F)]

fh.close()

# Choose which algorithm to run the dataset with

print("\nAlgorithm to use:")
print("1. Greedy Best-First-Search (Best ride per vehicle)")
print("2. Greedy Best-First-Search (Best vehicle per ride)")
print("3. Weighted A* search")
print("4. Beam search")

while True:
    try:
        alg = int(input("Choose algorithm to use: "))
        if heavy_file and alg == 3:
            print("\nWarning: This dataset is large.")
            print("A* Search may take a very long time or be infeasible.")          
            # give user choice to cancel operation
            confirm = input("Do you still want to continue? (y/n): ").lower()
            if confirm != 'y':
                print("Operation cancelled.")
                sys.exit()
            break
        elif heavy_file and alg == 4:
            print("\nWarning: This dataset is large.")
            print("Beam Search may take a very long time or be infeasible.")          
            # give user choice to cancel operation
            confirm = input("Do you still want to continue? (y/n): ").lower()
            if confirm != 'y':
                print("Operation cancelled.")
                sys.exit()
            break
        elif alg in [1, 2, 3, 4]:
            break
        else:
            print("Invalid choice.")
    except ValueError:
        print("Enter a number.")
alg_names = {
    1: "Greedy (best ride per vehicle)",
    2: "Greedy (best vehicle per ride)",
    3: "Weighted A*",
    4: "Beam Search"
}
print(f"\nAlgorithm used: {alg_names[alg]}")  

# User chooses weighted A* search
if alg == 3:
    while True:
        try:
            weight = int(input("Choose a weigth for the Weighted A* Search: "))
            if weight > 0:
                break
            else:
                print("Must be > 0.")
        except ValueError:
            print("Enter a number.")

# User chooses beam search
if alg == 4:
    while True:
        try:
            beam_width = int(input("Choose a width for the Beam Search: "))
            if beam_width > 0:
                break
            else:
                print("Must be > 0.")
        except ValueError:
            print("Enter a number.")

# Choose mode of execution (either a single run or analysis with multiple runs
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


#-------Operators-------#

# Applies a (vehicle, ride) assignment to the current state
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

    # updates vehicle state
    vehicle.row = ride.x
    vehicle.col = ride.y
    vehicle.time = finish_time
    vehicle.assigned_rides.append(ride.id)

    state.remaining_rides.remove(ride)
    state.score += earned

    return state


# Previous strategy: selects the globally best (vehicle, ride) pair.
# This tends to favour already active vehicles (since they are generally 
# closer to the ride start position), leading to poor distribution
# of rides and underutilization of the vehicles available.
def choose_best_vehicle_for_ride(state, bonus, T):  #choose best vehicle/ride pair for highest value
    best_op = None
    best_value = float('-inf')
    
    safe_replacement_op = None   # in case there is no Best operator, this one will be used instead

    for vehicle in state.vehicles:        # the for loops generate the operators (meaning the vehicle/ride pairs)
        for ride in state.remaining_rides:
            if vehicle.can_complete_ride(ride, T):
                
                if safe_replacement_op is None:     # save first feasible operator
                    safe_replacement_op = (vehicle.id, ride.id)
                
                dist_to_start = vehicle.distance_to_ride_start(ride)
                ride_dist = ride.distance()
                arrival = vehicle.time + dist_to_start
                wait_time = max(0, ride.s - arrival)
                
                value = ride_dist - dist_to_start - wait_time    # heuristic (from Scoring section + using wait_time to penalize waiting)
                if arrival <= ride.s:
                    value += bonus

                if value > best_value:
                    best_value = value
                    best_op = (vehicle.id, ride.id)
    
    if best_op is not None:
        return best_op

    return safe_replacement_op


# Improved strategy: selects locally the best ride for each vehicle.
# This approximates a parallel scheduler and results in a more balanced
# distribution of rides across vehicles.
def choose_best_ride_for_vehicle(state, vehicle, bonus, T):
    best_ride = None
    best_value = float('-inf')

    for ride in state.remaining_rides:
        if vehicle.can_complete_ride(ride, T):

            dist_to_start = vehicle.distance_to_ride_start(ride)
            ride_dist = ride.distance()
            arrival = vehicle.time + dist_to_start
            wait_time = max(0, ride.s - arrival)

            value = ride_dist - dist_to_start - wait_time    # heuristic (from Scoring section + using wait_time to penalize waiting)

            if arrival <= ride.s:
                value += bonus

            if value > best_value:
                best_value = value
                best_ride = ride

    return best_ride

# Greedy heuristic: assigns rides iteratively using local best choices.
# Vehicles are shuffled to reduce ordering bias.
def greedy_search(state, bonus, T):

    while True:
        progress = False
        
        random.shuffle(state.vehicles) # shuffles vehicles each iteration

        for vehicle in state.vehicles:
            best_ride = choose_best_ride_for_vehicle(state, vehicle, bonus, T)

            if best_ride is not None:
                apply_operator(state, (vehicle.id, best_ride.id), bonus, T)
                progress = True

        if not progress:
            break

    return state

# Greedy variant using global best operator selection (our first attempt).
# Included for comparison purposes, as it produces inferior results.
def old_greedy_search(state, bonus, T):

    while True:
        random.shuffle(state.vehicles) # shuffles vehicles each iteration, however
                                       # randomness does not fix this approach's
                                       # structural bias
        
        op = choose_best_vehicle_for_ride(state, bonus, T)
        if op is None:  # in case there are no feasible operators
            break

        new_state = apply_operator(state, op, bonus, T)
        if new_state is None:
            break

        state = new_state

    return state



#Implementação do Beam Search 
# A cópia dos objetos é feita manualmente (inline) para máxima performance.
def beam_search(initial_state, beam_width, bonus, T):
   
    beam = [initial_state]
    best_overall_state = initial_state

    while len(beam) > 0:
        next_states = []
        
        for state in beam:
            if len(state.remaining_rides) == 0:
                continue
                
            # Find the vehicle that becomes available the earliest
            # This balances the timeline for all vehicles
            earliest_time = float('inf')
            target_vehicle = None
            
            for v in state.vehicles:
                if v.time < earliest_time:
                    earliest_time = v.time
                    target_vehicle = v
            
            # If no vehicle is found 
            if target_vehicle is None:
                continue
                
            valid_rides = []
            
            for ride in state.remaining_rides:
                if target_vehicle.can_complete_ride(ride, T):
                    
                    dist_to_start = target_vehicle.distance_to_ride_start(ride)
                    arrival = target_vehicle.time + dist_to_start
                    wait_time = max(0, ride.s - arrival)
                    
                    # Heuristic value 
                    value = ride.distance() - dist_to_start - wait_time
                    if arrival <= ride.s:
                        value += bonus
                    
                    # Save both value and ride object
                    valid_rides.append((value, ride.id, ride))

            
            if len(valid_rides) > 0:
                # Sort rides by best value first
                valid_rides.sort(key=lambda x: x[0], reverse=True)
                
                # Expand states, limited by beam_width
                limit = min(beam_width, len(valid_rides))
                for i in range(limit):
                    ride_to_assign = valid_rides[i][2]
                    
                    # --- STATE CLONE ---
                    new_vehicles = []
                    for v in state.vehicles:
                        new_v = Vehicle(v.id, v.row, v.col, v.time)
                        
                        new_v.assigned_rides = []
                        for assigned in v.assigned_rides:
                            new_v.assigned_rides.append(assigned)
                        new_vehicles.append(new_v)
                        
                    new_remaining_rides = []
                    for r in state.remaining_rides:
                        new_remaining_rides.append(r)
                    
                    new_state = HashCodeState(new_vehicles, new_remaining_rides, state.score)
                    

                    # Apply operator to the isolated new state
                    apply_operator(new_state, (target_vehicle.id, ride_to_assign.id), bonus, T)
                    next_states.append(new_state)

        if len(next_states) == 0:
            break 
            
       
        for i in range(len(next_states)):
            for j in range(i + 1, len(next_states)):
                if next_states[j].score > next_states[i].score:
                    # Swap
                    temp = next_states[i]
                    next_states[i] = next_states[j]
                    next_states[j] = temp
        
        # Keep only the best states
        beam = []
        limit = min(beam_width, len(next_states))
        for i in range(limit):
            beam.append(next_states[i])
        
        # Update global best state
        if beam[0].score > best_overall_state.score:
            best_overall_state = beam[0]

    return best_overall_state

if __name__ == "__main__":
    raise SystemExit("Este ficheiro é uma biblioteca. Corre server.py ou usa o GUI.")


#-------solve problem-------#

def solve():
    best_state = None
    best_score = -1
    scores = []
    print()

    run_start = run_time.time() # starts timer to track program run time

    for i in range(n_runs):
        print(f"Run {i+1}/{n_runs}", end="\r") # track progress
        # recreate vehicles and state each run (necessary since they're modified with each run of the algorithm)
        vehicles = [Vehicle(i) for i in range(F)]
        state = HashCodeState(vehicles, list(rides))

        if alg == 1: # normal greedy search (best ride for vehicle)
            result = greedy_search(state, B, T)

        elif alg == 2: # old greedy search (best vehicle for ride)
            result = old_greedy_search(state, B, T)

        elif alg == 3: # weighted A* search
            ##### insert here call for weighted A* search #####
            print("\nWeighted A* not implemented yet.")
            continue

        elif alg == 4: # beam search
            ##### insert here call for beam search #####
            result = beam_search(state, beam_width, B, T)
            continue

        scores.append(result.score)

        if result.score > best_score:
            best_score = result.score
            best_state = result

    final_state = best_state
        
    run_end = run_time.time() # stops timer to track program run time
    print()
    output(final_state, scores, run_start, run_end)


def output(final_state, scores, run_start, run_end):

    # Output data
    fh = open(name_output, "w")
    for v in final_state.vehicles:
        v_rides = " ".join(str(r) for r in v.assigned_rides)
        fh.write(f"{len(v.assigned_rides)} {v_rides}\n")

    fh.close()
    print(f"\nOutput written to: {name_output}")

    # Theoretical maximum score assuming:
    # - every ride is possible to complete
    # - every bonus is achievable for each ride
    # it isn't a true optimal/possibly achievable scenario in practice, but serves as an upper bound for normalisation
    theoretical_max_possible = sum(r.distance() + B for r in rides)

    # Analysis of the results or score for the run
    if n_runs > 1:
        avg = sum(scores) / len(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
        min_score = min(scores)
        max_score = max(scores)
        # Raw metrics
        print(f"\nAverage score: {avg:.2f}")
        print(f"Std deviation: {std_dev:.2f}")
        print(f"Min score: {min_score}")
        print(f"Max score: {max_score}")
  
        # Normalised metrics (better for comparisons of algorithms between datasets)
        print(f"\nAverage score per ride: {avg / N:.2f}")
        print(f"Average normalised score: {avg / theoretical_max_possible:.4f}") # The closer to 1 the better

        print(f"\nTime: {run_end - run_start:.2f}s")

    else:
        score = final_state.score
        # Raw metrics
        print(f"\nScore for this run: {score}")

        # Normalised metrics (better for comparisons of algorithms between datasets)
        print(f"Score per ride: {score / N:.2f}")
        print(f"Normalised score: {score / theoretical_max_possible:.4f}") # The closer to 1 the better

        print(f"\nTime: {run_end - run_start:.2f}s")