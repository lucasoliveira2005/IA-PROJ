# Optimization Problems - Self-Driving Rides

## Project Overview

This project implements and compares different search and heuristic algorithms for the Google Hash Code Self-Driving Rides problem.
The objective is to assign pre-booked rides to a defined fleet of self-driving vehicles in a simulated city in order to maximise the total score, considering distance, timing constraints, and bonus rewards.


## Problem Description

Each ride has:
- a start and end position, which are always different.
- an earliest start time.
- a latest finish time, by which the ride must be completed.

Each vehicle:
- starts at position (0, 0).
- is assigned rides such that they're completed before their deadlines.
- receives a bonus if the ride starts exactly at its earliest time.

The map is a rectangular grid of streets with R rows and C columns. There is no limit for how many vehicles can be in the same intersection at the same time.


## Algorithms Implemented

### Greedy (Best ride per vehicle):
Selects the best available ride for each vehicle based on a local heuristic.
This approach approximates a parallel scheduler and results in a better distribution of rides.

### Greedy (Best vehicle per ride)
Selects the globally best (vehicle, ride) pair.
This tends to favour vehicles that have already been assigned rides and leads to poorer results with underutilisation of the fleet.

### Weighted A* Search
Explores the search space more optimally, but is computationally expensive for large datasets.
######### COMPLETAR SE NECESSÁRIO #########

### Beam Search
Limits branching using a fixed beam width, trading optimality for performance.
######### COMPLETAR SE NECESSÁRIO #########


## Heuristic Design

The heuristic prioritises:
- longer rides (higher reward)
- shorter travel distance to the start location (efficiency)
- minimal waiting time

A bonus is added when the vehicle can arrive before the earliest start time, encouraging optimal timing and bonus acquisition.

To reduce ordering bias, vehicles are randomly shuffled at each iteration, allowing multiple runs to explore different solutions.

## Implementation Overview

### Classes:
- Ride: represents a ride with an id, start/end coordinates, time constraints, and distance calculation.
- Vehicle: represents a vehicle with an id, current positon, time, and assigned rides. Includes helper methods such as feasibility checks and distance calculation.
- HashCodeState: stores current state of the system, including vehicles, remaining rides, and total score.

### Key Functions:
- apply_operator(state, operator, bonus, T): assigns a ride to a vehicle and updates its state (position, time, and score).
- choose_best_ride_for_vehicle(state, vehicle, bonus, T): selects the best ride for a given vehicle based on the heuristic.
- choose_best_vehicle_for_ride(state, bonus, T): selects the globally best (vehicle, ride) pair, corresponding to the initial greedy strategy.
######### ADICIONAR HEURISTIC SELECTION USADAS PARA O A* #########
######### ADICIONAR HEURISTIC SELECTION PARA O BEAM SEARCH #########
- greedy_search(state, bonus, T): main greedy algorithm using local decisions (best ride per vehicle)
- old_greedy_search(state, bonus, T): baseline greedy approach used for comparison.
######### ADICIONAR SEARCH ALGORITHM FUNCTION USADAS PARA O A* #########
######### ADICIONAR SEARCH ALGORITHM FUNCTION USADAS PARA O BEAM SEARCH #########

### Execution Flow:
1. Load input dataset
2. Initialise vehicles and rides
3. Select algorithm and execution mode
4. Run the selected algorithm (single or multiple runs)
5. Output results to file
6. Collect and present performance metrics (score, normalised score, etc...)


## How to Run

1. Run the program in "project1_IA.py".
2. Select an input file from the menu.
3. Choose the algorithm to run.
4. If applicable, provide parameters (weight for A*, beam width for Beam Search).
5. Select execution mode (single or multiple runs).
6. If multiple runs are selected, specify the number of runs.
7. Results are displayed in the console, and the best solution is saved in the "outputs/" folder.

###################################################################
######### MUDAR PARA A MANEIRA DE UTILIZAÇÃO DO GUI FINAL #########
###################################################################

## Input and Output Structure

### Inputs
Input files are stored in the "inputs/" folder.
Users can add their own datasets following the same format.

### Outputs
Output files are written to the "outputs/" folder.
Each output corresponds to the selected input file and contains the assigned rides for each vehicle.

###################################################################
######### MUDAR PARA A MANEIRA DE UTILIZAÇÃO DO GUI FINAL #########
###################################################################

## Dataset Description

The "inputs/" folder already comes with datasets that were used to test the algorithms.
The following datasets were taken from the official Google Hash Code challenge repository:
- a_example.in : very few rides, used mainly for debugging.
- b_should_be_easy.in : main dataset used for testing with low complexity and a meaningful number of rides.
- c_no_hurry.in : very large number of rides, computationally expensive, making it unsuitable for A* or Beam Search.
- d_metropolis.in : large amount of rides with a big degree of complexity that attempt to create a realistic portrayal of transit in a real metropolis. It's computational expensive, making it unsuitable for A* or Beam Search, but works as the best test for the normal greedy algorithm.
- e_high_bonus.in : large amount of rides with focus on the impact of bonuses in the calculations of the heuristic. It's computational expensive, making it unsuitable for A* or Beam Search.


## Experimental Results

This section will present a comparison of the implemented algorithms across the available datasets.

Metrics considered:
- Total score
- Score per ride
- Normalised score
- Execution time

The goal is to analyse performance, scalability, and solution quality across different problem sizes.

##########################################################################
####### COMPLETAR COM A COMPARAÇÃO DOS DIFERENTES ALGORITMOS E DATSETS ###
##########################################################################


## Notes on Complexity and Limitations

Greedy algorithms scale well with large datasets, although the initial greedy strategy is less time efficient and produces worse results.
In contrast, A* and Beam Search suffer from exponential growth in the search space, making them infeasible for large inputs or real-life scenarios.

A warning mechanism is included to alert the user when attempting to run computationally expensive algorithms (such as A* or Beam Search) on large datasets.