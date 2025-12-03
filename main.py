import argparse
import os
import sys
import logging
from datetime import datetime
from Task1_Parser.task1 import PetriNet
from Task2_Explicit.task2 import ExplicitTraverse
from Task3_BDD.task3 import BDD_Reachability
from Task4_Deadlock.task4 import ILP_BDD_Deadlock_Detection
from Task5_Optimization.task5 import Optimization


class DualOutput:
    """Write to both console and file simultaneously"""

    def __init__(self, file_handle, console):
        self.file = file_handle
        self.console = console

    def write(self, message):
        self.console.write(message)
        self.file.write(message)
        self.file.flush()

    def flush(self):
        self.console.flush()
        self.file.flush()


def setup_logging(pnml_file):
    """Setup logging to file and console"""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Generate log filename with timestamp and PNML name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pnml_basename = os.path.splitext(os.path.basename(pnml_file))[0]
    log_filename = f"logs/{pnml_basename}_{timestamp}.log"

    return log_filename


def main(pnml_file=None):
    if pnml_file is None:
        pnml_file = "Test_PNML_Files/config1.pnml"
    else:
        # If the user passed only a filename (e.g. "config1.pnml"), try the
        # project `Test_PNML_Files/` directory when the path doesn't exist.
        if not os.path.isabs(pnml_file) and not os.path.exists(pnml_file):
            candidate = os.path.join("Test_PNML_Files", pnml_file)
            if os.path.exists(candidate):
                pnml_file = candidate
            else:
                print(f"PNML file not found: {pnml_file}")
                print(f"Tried: {pnml_file} and {candidate}")
                sys.exit(1)

    # Setup logging to file
    log_filename = setup_logging(pnml_file)
    log_file = open(log_filename, "w", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = DualOutput(log_file, original_stdout)

    # =====================================================================
    print("=" * 60)
    print("PETRI NET ANALYSIS - MAIN TEST")
    print("=" * 60)
    print(f"Log file: {log_filename}")

    # =====================================================================
    # TASK 1: PARSER
    # =====================================================================
    print("\n[TASK 1] PARSER - Reading PNML file")
    print("-" * 60)

    petri_net = PetriNet(pnml_file)

    print(f"Places: {petri_net.places}")
    print(f"Transitions: {petri_net.transitions}")
    print(f"Number of places: {petri_net.num_places}")
    print(f"Number of transitions: {petri_net.num_transitions}")
    print(f"Initial marking: {petri_net.initial_marking}")
    print(f"Pre-matrix shape: {petri_net.pre_matrix.shape}")
    print(f"Post-matrix shape: {petri_net.post_matrix.shape}")

    # =====================================================================
    # TASK 2: EXPLICIT TRAVERSE
    # =====================================================================
    print("\n[TASK 2] EXPLICIT TRAVERSE")
    print("-" * 60)

    explicit = ExplicitTraverse(petri_net)
    explicit.print_reachable_markings(method="bfs", timeout=30.0)

    # =====================================================================
    # TASK 3: BDD REACHABILITY
    # =====================================================================
    print("\n[TASK 3] BDD REACHABILITY")
    print("-" * 60)

    bdd_reach = BDD_Reachability(petri_net)
    print("Computing reachable states using BDD...")

    states_bdd, total_states, elapsed_time = bdd_reach.compute_reachable_states()

    print(f"Total reachable states (BDD): {total_states}")
    print(f"Execution time: {elapsed_time:.6f} seconds")

    # =====================================================================
    # TASK 4: DEADLOCK DETECTION
    # =====================================================================
    print("\n[TASK 4] DEADLOCK DETECTION")
    print("-" * 60)

    # Pass existing BDD manager and reachable count to avoid creating a different BDD
    deadlock_detector = ILP_BDD_Deadlock_Detection(
        petri_net, bdd_reach=bdd_reach, reachable_marking_nums=total_states
    )
    print("Detecting deadlock states...")

    deadlock_marking, deadlock_time = deadlock_detector.find_deadlock(states_bdd)

    if deadlock_marking:
        print(f"Deadlock found at marking: {deadlock_marking}")
    else:
        print("No deadlock found in reachable states")
    print(f"Deadlock detection time: {deadlock_time:.6f} seconds")

    # =====================================================================
    # TASK 5: OPTIMIZATION
    # =====================================================================
    print("\n[TASK 5] OPTIMIZATION")
    print("-" * 60)

    # Pass the BDD reachability object so optimizer reuses same BDD manager
    optimizer = Optimization(petri_net, bdd_reach=bdd_reach)
    best_marking, score, opt_time = optimizer.optimize_reachable_marking(states_bdd)

    print(f"Best marking: {best_marking}")
    print(f"Optimal score: {score}")
    print(f"Optimization time: {opt_time:.6f} seconds")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

    # Close log file and restore stdout
    log_file.close()
    sys.stdout = original_stdout
    print(f"\n✓ Log saved to: {log_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Petri net analysis on a PNML file (default: Test_PNML_Files/config2.pnml)"
    )
    parser.add_argument(
        "pnml_file",
        nargs="?",
        default=None,
        help="Path to PNML file to analyze (optional)",
    )
    args = parser.parse_args()
    main(args.pnml_file)
