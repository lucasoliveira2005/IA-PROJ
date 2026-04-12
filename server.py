"""
server.py — GUI backend para project1_IA.py
Corre: python server.py
Abre: http://localhost:5000
"""

import os
import statistics
import time as run_time
import subprocess
from flask import Flask, request, jsonify, send_from_directory

from project1_IA import (
    Ride, Vehicle, HashCodeState,
    greedy_search,
    old_greedy_search,
    beam_search,
)

app = Flask(__name__, static_folder=".")


# ── Serialização ──────────────────────────────────────────────────────────────

def state_to_json(state, rides_map):
    vehicles_out = []
    for v in state.vehicles:
        rides_out = []
        for rid in v.assigned_rides:
            r = rides_map[rid]
            rides_out.append({
                "id": r.id,
                "a": r.a, "b": r.b,
                "x": r.x, "y": r.y,
                "s": r.s, "f": r.f,
                "dist": r.distance(),
            })
        vehicles_out.append({
            "id": v.id,
            "rides": rides_out,
            "n_rides": len(rides_out),
        })

    return {
        "score": state.score,
        "vehicles": vehicles_out,
        "assigned": sum(len(v["rides"]) for v in vehicles_out),
    }

def load_cpp_best(out_path, score):
    vehicles = []
    ass = 0

    with open(out_path) as f:
        lines = f.read().strip().splitlines()

    for i, line in enumerate(lines):
        if not line.strip():
            continue

        parts = list(map(int, line.split()))
        ride_ids = parts[1:] if len(parts) > 1 else []

        ass += parts[0]

        v = {
                "id": i,
                "rides": ride_ids,
                "n_rides": parts[0]
            }
        
        vehicles.append(v)

    return {
        "score": score,
        "vehicles": vehicles,
        "assigned": ass,
    }


# ── Rotas ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    base = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base, "gui.html")


@app.route("/run", methods=["POST"])
def run():
    import traceback
    try:
        data = request.get_json()
        file_content = data.get("content", "")
        n_runs     = max(1, int(data.get("n_runs", 1)))
        algorithm  = int(data.get("algorithm", 1))   # 1, 2, 3 ou 4
        weight     = max(1, int(data.get("weight", 1)))
        beam_width = max(1, int(data.get("beam_width", 3)))
        filename = data.get("filename", "")

        # Parse ficheiro
        lines = file_content.strip().splitlines()
        R, C, F, N, B, T = map(int, lines[0].split())
        rides = []
        for i in range(1, N + 1):
            a, b, x, y, s, f = map(int, lines[i].split())
            rides.append(Ride(i - 1, a, b, x, y, s, f))
        rides_map = {r.id: r for r in rides}
        theoretical_max = sum(r.distance() + B for r in rides)

        t_start = run_time.time()

        if (algorithm == 3):
            subprocess.run(["g++", "-O3", "-Wall", "aStar.cpp", "-o", "aStar"], capture_output=True)
            cpp_result = subprocess.run(["./aStar", filename, str(weight)], capture_output=True, text=True, check=True)
            elapsed = run_time.time() - t_start

            lines = [l.strip() for l in cpp_result.stdout.splitlines() if l.strip()]
            file_path = lines[0]
            score = int(lines[1])

            return jsonify({
                "params": {"R": R, "C": C, "F": F, "N": N, "B": B, "T": T},
                "best": load_cpp_best(file_path, score),
                "scores": [score],
                "avg": score,
                "std": 0,
                "min": score,
                "max": score,
                "time": round(elapsed, 4),
                "theoretical_max": theoretical_max,
            })
        
        else:
            best_state = None
            best_score = -1
            scores = []

            for _ in range(n_runs):
                vehicles = [Vehicle(i) for i in range(F)]
                state = HashCodeState(vehicles, list(rides))

                if algorithm == 1:
                    result = greedy_search(state, B, T)
                elif algorithm == 2:
                    result = old_greedy_search(state, B, T)
                elif algorithm == 4:
                    result = beam_search(state, beam_width, B, T)
                else:
                    return jsonify({"error": f"Algoritmo {algorithm} desconhecido"}), 400

                scores.append(result.score)
                if result.score > best_score:
                    best_score = result.score
                    best_state = result

            elapsed = run_time.time() - t_start

            # Guardar .out
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
            os.makedirs(output_dir, exist_ok=True)

            return jsonify({
                "params": {"R": R, "C": C, "F": F, "N": N, "B": B, "T": T},
                "best": state_to_json(best_state, rides_map),
                "scores": scores,
                "avg": sum(scores) / len(scores),
                "std": statistics.stdev(scores) if len(scores) > 1 else 0,
                "min": min(scores),
                "max": max(scores),
                "time": round(elapsed, 4),
                "theoretical_max": theoretical_max,
            })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/inputs")
def list_inputs():
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs")
    os.makedirs(folder, exist_ok=True)
    files = [f for f in os.listdir(folder) if f.endswith(".in")]
    return jsonify(sorted(files))


@app.route("/inputs/<filename>")
def get_input(filename):
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs")
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Ficheiro não encontrado"}), 404
    with open(path) as f:
        return f.read(), 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    print("\n  Ride Scheduler — servidor a correr")
    print("  Abre no browser: http://localhost:5000\n")
    app.run(debug=False, port=5000)