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
    vector<Ride> remaining_rides;
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

void apply_operator(State& state, int vehicle_idx, int ride_idx, int bonus, int T) {
    Vehicle& v = state.vehicles[vehicle_idx];
    const Ride& r = state.remaining_rides[ride_idx];
    int dist_to_start = v.dist_to_ride(r);
    int start_time = max(v.time + dist_to_start, r.s);
    if (start_time == r.s) state.score += bonus;
    state.score += r.distance();
    v.row = r.x; v.col = r.y;
    v.time = start_time + r.distance();
    v.assigned_rides.push_back(r.id);
    state.remaining_rides.erase(state.remaining_rides.begin() + ride_idx);
}

// Implementação simples do Greedy em C++
State greedy_search(vector<Vehicle> vels, vector<Ride> rds, int B, int T) {
    State s; s.vehicles = vels; s.remaining_rides = rds;
    bool progress = true;
    while (progress) {
        progress = false;
        for (auto& v : s.vehicles) {
            int best_ride_idx = -1;
            int best_val = -2e9;
            for (size_t i = 0; i < s.remaining_rides.size(); ++i) {
                if (v.can_complete(s.remaining_rides[i], T)) {
                    int val = evaluate(0, v, s.remaining_rides[i], B, 1);
                    if (val > best_val) {
                        best_val = val;
                        best_ride_idx = (int)i;
                    }
                }
            }
            if (best_ride_idx != -1) {
                apply_operator(s, (int)(&v - &s.vehicles[0]), best_ride_idx, B, T);
                progress = true;
            }
        }
    }
    return s;
}

State A_star(const vector<Vehicle>& init_v, const vector<Ride>& init_r, int B, int T, int weight) {
    priority_queue<State> pq;
    State initial; initial.vehicles = init_v; initial.remaining_rides = init_r;
    pq.push(initial);
    State best_node = initial;
    int nodes = 0;
    while (!pq.empty() && nodes < 10000000) { // Limite de expansão para não estourar RAM
        State curr = pq.top(); pq.pop();
        if (curr.score > best_node.score) best_node = curr;
        if (curr.remaining_rides.empty()) break;
        nodes++;
        for (size_t i = 0; i < min(curr.remaining_rides.size(), (size_t)15); ++i) {
            for (size_t j = 0; j < curr.vehicles.size(); ++j) {
                if (curr.vehicles[j].can_complete(curr.remaining_rides[i], T)) {
                    State next_s = curr;
                    next_s.f_value = evaluate(next_s.score, next_s.vehicles[j], next_s.remaining_rides[i], B, weight);
                    apply_operator(next_s, (int)j, (int)i, B, T);
                    pq.push(next_s);
                    break; 
                }
            }
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
