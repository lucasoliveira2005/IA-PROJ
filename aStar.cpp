#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <cmath>
#include <algorithm>
#include <queue>
#include <filesystem>

using namespace std;
namespace fs = std::filesystem;

struct Ride {
    int id;
    int a, b, x, y, s, f;
    int distance() const { return abs(a - x) + abs(b - y); }
};

struct Vehicle {
    int id;
    int row = 0, col = 0, time = 0;
    vector<int> assigned_rides;

    int dist_to_ride(const Ride& r) const { return abs(row - r.a) + abs(col - r.b); }
    bool can_complete(const Ride& r, int T) const {
        int arrival = time + dist_to_ride(r);
        int start = max(arrival, r.s);
        return (start + r.distance()) <= r.f && (start + r.distance()) <= T;
    }
};

struct State {
    vector<Vehicle> vehicles;
    vector<bool> used_rides;    //muito mais leve que ter um vector<Ride>
    int currentRide = 0;
    int currentVehicle = 0;
    int score = 0;
    int f_value = 0;
    bool operator<(const State& other) const { return f_value < other.f_value; }
};


int evaluate(int currentScore, const Vehicle& v, const Ride& r, int bonus, int weight) {
    int dist_to_start = v.dist_to_ride(r);
    int arrival = v.time + dist_to_start;
    int wait_time = max(0, r.s - arrival);
    int heuristic = r.distance() - dist_to_start - wait_time;
    if (arrival <= r.s) heuristic += bonus;
    return currentScore + (weight * heuristic);
}

void apply_operator(State& state, Vehicle& vehicle, const Ride& ride, const int bonus, const int T, const int rideIdx) {
    int dist_to_start = vehicle.dist_to_ride(ride);
    int start_time = max(vehicle.time + dist_to_start, ride.s);
    if (start_time == ride.s) state.score += bonus;
    state.score += ride.distance();
    vehicle.row = ride.x;
    vehicle.col = ride.y;
    vehicle.time = start_time + ride.distance();
    vehicle.assigned_rides.push_back(ride.id);
    state.used_rides[ride.id] = true;
    state.currentRide = rideIdx;
}

State greedy_search(vector<Vehicle> vels, const vector<Ride>& rds, int B, int T) {
    State s;
    s.vehicles = vels;
    s.used_rides.assign(rds.size(), false);
    
    return s;
}

State A_star(const vector<Vehicle>& init_v, const vector<Ride>& all_rides, int B, int T, int weight) {

    priority_queue<State> pq;
    State initial;
    initial.vehicles = init_v;
    initial.used_rides.assign(all_rides.size(), false);

    pq.push(initial);
    State best_node = initial;
    int nodes = 0;

    while (!pq.empty() && nodes < INT8_MAX) { // Limite de expansão para não estourar RAM

        State curr = pq.top();
        pq.pop();

        if (curr.score > best_node.score) {
            best_node = curr;
        }

        if (curr.currentRide >= (int)all_rides.size()) break;

        int tried_in_this_node = 0;     // Para efeitos de performance, limitamos quantas rides novas tentamos por nó

        Vehicle& currentVehicle = curr.vehicles[curr.currentVehicle];

        bool canCompleteAnyRide = false;

        State next_s = curr;

        for (size_t r = 0; r < all_rides.size(); r++) {

            if (!curr.used_rides[r]) {
                const Ride& ride = all_rides[r];

                if (currentVehicle.can_complete(ride, T)) {

                    canCompleteAnyRide = true;

                    next_s.f_value = evaluate(next_s.score, currentVehicle, ride, B, weight);
                    apply_operator(next_s, currentVehicle, ride, B, T, curr.currentRide);
                    nodes++;

                    if ((curr.currentVehicle % curr.vehicles.size()) == 0) {
                        next_s.currentVehicle = 0;
                    }

                    next_s.currentVehicle++;
                    pq.push(next_s);
                    tried_in_this_node++;
                }
            }
        }

        if (!canCompleteAnyRide) {
            State next_v = curr;

            if ((curr.currentVehicle % curr.vehicles.size()) == 0) {
                next_s.currentVehicle = 0;
            }

            next_s.currentVehicle++;
            pq.push(next_s);
        }
    }
    
    return best_node;
}

int main() {
    string input_folder = "inputs";
    vector<string> files;
    
    cout << "\nAvailable input files:" << endl;
    int count = 1;
    for (const auto& entry : fs::directory_iterator(input_folder)) {
        if (entry.is_regular_file()) {
            files.push_back(entry.path().string());
            cout << count++ << ". " << entry.path().filename().string() << endl;
        }
    }

    int choice;
    cout << "Select a file by number: ";
    cin >> choice;
    string name_input = files[choice - 1];

    cout << "\nAlgorithm\n1. Greedy\n2. Weighted A*\nChoose: ";
    int algo; cin >> algo;
    int weight = 1;
    if (algo == 2) {
        cout << "Choose weight (>=1): ";
        cin >> weight;
    }

    ifstream infile(name_input);
    int R, C, F, N, B, T;
    infile >> R >> C >> F >> N >> B >> T;

    vector<Ride> rides(N);
    for (int i = 0; i < N; ++i) {
        rides[i].id = i;
        infile >> rides[i].a >> rides[i].b >> rides[i].x >> rides[i].y >> rides[i].s >> rides[i].f;
    }

    sort(rides.begin(), rides.end(), [](const Ride& a, const Ride& b) {
        if (a.s != b.s) {
            return a.s < b.s;
        }
        return a.f < b.f;     // Desempate: quem termina mais cedo ganha prioridade
    });

    vector<Vehicle> vehicles(F);
    for (int i = 0; i < F; ++i) vehicles[i].id = i;

    State result;
    if (algo == 1) result = greedy_search(vehicles, rides, B, T);
    else result = A_star(vehicles, rides, B, T, weight);

    sort(result.vehicles.begin(), result.vehicles.end(), [](const Vehicle& a, const Vehicle& b) {
        return a.id < b.id;
    });

    string out_name = "outputs/" + fs::path(name_input).stem().string() + ".out";
    ofstream outfile(out_name);
    for (const auto& v : result.vehicles) {
        outfile << v.assigned_rides.size();
        for (int id : v.assigned_rides) outfile << " " << id;
        outfile << "\n";
    }

    cout << "\nOutput written to: " << out_name << endl;
    cout << "Final Score: " << result.score << endl;

    return 0;
}
