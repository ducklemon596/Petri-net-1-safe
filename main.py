from Task1_Parser.task1 import PetriNet
from Task2_Explicit.task2 import ExplicitTraverse
from Task3_BDD.task3 import BDD_Reachability
from Task4_Deadlock.task4 import ILP_BDD_Deadlock_Detection
from Task5_Optimization.task5 import Optimization


def main():
    print("=" * 60)
    print("PETRI NET ANALYSIS - MAIN TEST")
    print("=" * 60)

    # Test configuration
    pnml_file = "Test_PNML_Files/config1.pnml"

    # =====================================================================
    # TASK 1: PARSER - Read PNML file
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
    explicit.print_reachable_markings(method="bfs", timeout=10.0)

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
    print(f"Get Boolean expression from BDD:")
    expr = bdd_reach.get_expr_from_bdd(states_bdd)
    print(expr)

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

    weights = {p: 1 for p in petri_net.places}
    best_marking, score, opt_time = optimizer.optimize_reachable_marking(
        states_bdd, weights
    )

    print(f"Best marking: {best_marking}")
    print(f"Optimal score: {score}")
    print(f"Optimization time: {opt_time:.6f} seconds")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
