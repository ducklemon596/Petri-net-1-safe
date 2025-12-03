import time
from Task3_BDD.task3 import BDD_Reachability


class Optimization:
    def __init__(self, petri_net, bdd_reach=None):
        # Reuse provided BDD_Reachability to keep a single BDD manager,
        # otherwise create a new one for this optimizer.
        if bdd_reach is not None:
            self.bdd_reachability = bdd_reach
        else:
            self.bdd_reachability = BDD_Reachability(petri_net)
        self.petri_net = petri_net
        self.bdd = self.bdd_reachability.bdd

    def optimize_reachable_marking(self, reachable_bdd, weights=None):
        start_time = time.time()

        # Determine weights: prefer petri_net.c if present, otherwise use provided weights or default
        if getattr(self.petri_net, "c", None) is not None:
            # petri_net.c is expected to be an array-like with same order as places
            try:
                weights = {
                    p: int(self.petri_net.c[i])
                    for i, p in enumerate(self.petri_net.places)
                }
            except Exception:
                # fallback to provided weights or defaults
                if weights is None:
                    weights = {p: 1 for p in self.petri_net.places}
        else:
            # Set default weights if not provided
            if weights is None:
                weights = {p: 1 for p in self.petri_net.places}

        # Build final weights dictionary
        final_weights = {}
        for p in self.petri_net.places:
            final_weights[p] = weights.get(p, 0)

        max_score = -float("inf")
        best_marking = None
        found_any = False

        # Iterate through all solutions of the BDD
        try:
            for state in self.bdd.pick_iter(reachable_bdd):
                found_any = True
                current_score = 0
                temp_marking = {}

                # Extract marking from BDD state
                for p in self.petri_net.places:
                    bdd_var = f"x_{p}"
                    has_token = 1 if state.get(bdd_var, False) else 0
                    temp_marking[p] = has_token
                    current_score += has_token * final_weights[p]

                # Update best marking if current score is better
                if current_score > max_score:
                    max_score = current_score
                    best_marking = temp_marking

        except Exception as e:
            print(f"Error during optimization: {e}")
            return None, None, time.time() - start_time

        end_time = time.time()
        duration = end_time - start_time

        if not found_any:
            print("No reachable states found in the BDD!")
            return None, None, duration

        return best_marking, max_score, duration

    def optimize_with_constraints(self, reachable_bdd, weights=None, constraints=None):
        start_time = time.time()

        # Determine weights: prefer petri_net.c if present, otherwise use provided weights or default
        if getattr(self.petri_net, "c", None) is not None:
            try:
                weights = {
                    p: int(self.petri_net.c[i])
                    for i, p in enumerate(self.petri_net.places)
                }
            except Exception:
                if weights is None:
                    weights = {p: 1 for p in self.petri_net.places}
        else:
            if weights is None:
                weights = {p: 1 for p in self.petri_net.places}

        if constraints is None:
            constraints = {}

        final_weights = {}
        for p in self.petri_net.places:
            final_weights[p] = weights.get(p, 0)

        max_score = -float("inf")
        best_marking = None
        found_any = False

        try:
            for state in self.bdd.pick_iter(reachable_bdd):
                temp_marking = {}
                valid = True

                # Extract marking
                for p in self.petri_net.places:
                    bdd_var = f"x_{p}"
                    has_token = 1 if state.get(bdd_var, False) else 0
                    temp_marking[p] = has_token

                    # Check constraints
                    if p in constraints:
                        min_val, max_val = constraints[p]
                        if not (min_val <= has_token <= max_val):
                            valid = False
                            break

                if not valid:
                    continue

                found_any = True
                current_score = sum(
                    temp_marking[p] * final_weights[p] for p in self.petri_net.places
                )

                if current_score > max_score:
                    max_score = current_score
                    best_marking = temp_marking

        except Exception as e:
            print(f"Error during constrained optimization: {e}")
            return None, None, time.time() - start_time

        end_time = time.time()
        duration = end_time - start_time

        if not found_any:
            print("No valid states found satisfying all constraints!")
            return None, None, duration

        return best_marking, max_score, duration
