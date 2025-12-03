import argparse
import os
import sys
import tracemalloc
from Task1_Parser.task1 import PetriNet
from Task2_Explicit.task2 import ExplicitTraverse
from Task3_BDD.task3 import BDD_Reachability


def benchmark_task2(petri_net, method="bfs", timeout=100.0):
    """Benchmark Task2 (Explicit) memory usage"""
    print("\n" + "=" * 60)
    print("TASK 2: EXPLICIT TRAVERSE - MEMORY BENCHMARK")
    print("=" * 60)
    
    tracemalloc.start()
    
    explicit = ExplicitTraverse(petri_net)
    states, elapsed_time = explicit.compute_reachable_markings(method=method, timeout=timeout)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Method: {method.upper()}")
    
    if states == -1:
        print(f"TIMEOUT: Exceeded {timeout} seconds")
        print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
        return {
            "method": f"Task2-{method.upper()}",
            "states": "TIMEOUT",
            "current_memory_mb": current / 1024 / 1024,
            "peak_memory_mb": peak / 1024 / 1024
        }
    
    print(f"Total states: {len(states)}")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
    
    return {
        "method": f"{method.upper()}",
        "states": len(states),
        "peak_memory_mb": peak / 1024 / 1024
    }


def benchmark_task3(petri_net):
    """Benchmark Task3 (BDD) memory usage"""
    print("\n" + "=" * 60)
    print("TASK 3: BDD REACHABILITY - MEMORY BENCHMARK")
    print("=" * 60)
    
    tracemalloc.start()
    
    bdd_reach = BDD_Reachability(petri_net)
    states_bdd, total_states, elapsed_time = bdd_reach.compute_reachable_states()
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Total states: {total_states}")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
    
    return {
        "method": "BDD",
        "states": total_states,
        "peak_memory_mb": peak / 1024 / 1024
    }

def print_comparison(results):
    """Print comparison table"""
    print("\n" + "=" * 60)
    print("MEMORY COMPARISON SUMMARY")
    print("=" * 60)
    
    print(f"\n{'Method':<15} {'States':<12} {'Peak Memory (MB)':<20}")
    print("-" * 50)
    
    for r in results:
        states_str = str(r['states']) if isinstance(r['states'], str) else str(r['states'])
        print(f"{r['method']:<15} {states_str:<12} {r['peak_memory_mb']:<20.2f}")
    
    print("\n" + "-" * 50)
    best_memory = min(results, key=lambda x: x['peak_memory_mb'])
    
    print(f"Lower memory: {best_memory['method']} ({best_memory['peak_memory_mb']:.2f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Benchmark memory usage for Task2 and Task3")
    parser.add_argument("--file", "-f", type=str, default="config1.pnml",
                        help="PNML file to test (default: config1.pnml)")
    parser.add_argument("--task", "-t", type=str, choices=["2", "3", "both"], default="both",
                        help="Which task to benchmark (default: both)")
    parser.add_argument("--method", "-m", type=str, choices=["bfs", "dfs"], default="bfs",
                        help="Method for Task2 (default: bfs)")
    parser.add_argument("--timeout", type=float, default=100.0,
                        help="Timeout for Task2 in seconds (default: 100.0)")
    
    args = parser.parse_args()
    
    pnml_file = args.file
    if not os.path.isabs(pnml_file) and not os.path.exists(pnml_file):
        candidate = os.path.join("Test_PNML_Files", pnml_file)
        if os.path.exists(candidate):
            pnml_file = candidate
        else:
            print(f"Error: PNML file not found: {pnml_file}")
            sys.exit(1)
    
    print("=" * 60)
    print("PETRI NET MEMORY BENCHMARK")
    print("=" * 60)
    print(f"File: {pnml_file}")
    
    print("\nLoading Petri Net...")
    petri_net = PetriNet(pnml_file)
    print(f"Places: {petri_net.num_places}")
    print(f"Transitions: {petri_net.num_transitions}")
    
    results = []
    
    if args.task in ["2", "both"]:
        try:
            result = benchmark_task2(petri_net, method=args.method, timeout=args.timeout)
            results.append(result)
        except Exception as e:
            print(f"Error in Task2: {e}")
    
    if args.task in ["3", "both"]:
        try:
            result = benchmark_task3(petri_net)
            results.append(result)
        except Exception as e:
            print(f"Error in Task3: {e}")
    
    if results:
        print_comparison(results)


if __name__ == "__main__":
    main()
