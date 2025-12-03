import time
import numpy as np
from dd import autoref as bdd
import sys
from Task1_Parser.task1 import PetriNet

sys.setrecursionlimit(10000)


class BDD_Reachability:
    def __init__(self, petri_net: PetriNet):
        self.petri_net = petri_net
        self.bdd = bdd.BDD()

        # Initialize BDD variables for each place
        for p in self.petri_net.places:
            safe_p = p.replace("-", "_")
            self.bdd.declare(f"x_{safe_p}")
            self.bdd.declare(f"y_{safe_p}")

        # Rename map
        self.rename_map = {
            f'y_{p.replace("-", "_")}': f'x_{p.replace("-", "_")}'
            for p in self.petri_net.places
        }
        # Cache for reachable BDD (computed on demand)
        self._reachable_bdd = None

    def build_initial_state_bdd(self):
        expr = []
        for i, p in enumerate(self.petri_net.places):
            safe_p = p.replace("-", "_")
            if self.petri_net.initial_marking[i] > 0:
                expr.append(f"x_{safe_p}")
            else:
                expr.append(f"~x_{safe_p}")
        return self.bdd.add_expr(" & ".join(expr))

    def build_transition(self):
        R_total = self.bdd.false  # Start with empty BDD

        # Iterate over all transitions (every column in pre/post matrices)
        for t_idx in range(self.petri_net.num_transitions):
            t_id = self.petri_net.transitions[t_idx]

            # Get input and output places for the transition
            input_places = np.where(self.petri_net.pre_matrix[:, t_idx] == 1)[0]
            output_places = np.where(self.petri_net.post_matrix[:, t_idx] == 1)[0]

            # Convert to place IDs
            input_ids = [self.petri_net.places[i] for i in input_places]
            output_ids = [self.petri_net.places[i] for i in output_places]

            # Get all places involved in the transition
            involved_places = set(input_ids) | set(output_ids)

            # Enable
            enable_expr = []
            for p in input_ids:
                safe_p = p.replace("-", "_")
                enable_expr.append(f"x_{safe_p}")
            for p in output_ids:
                if p not in input_ids:
                    safe_p = p.replace("-", "_")
                    enable_expr.append(f"~x_{safe_p}")

            # Update
            update_expr = []
            for p in input_ids:
                if p not in output_ids:
                    safe_p = p.replace("-", "_")
                    update_expr.append(f"~y_{safe_p}")

            for p in output_ids:
                safe_p = p.replace("-", "_")
                update_expr.append(f"y_{safe_p}")

            # Frame Axiom
            frame_expr = []
            for p in self.petri_net.places:
                if p not in involved_places:
                    safe_p = p.replace("-", "_")
                    frame_expr.append(f"(y_{safe_p} <-> x_{safe_p})")

            # Combine all parts of the transition relation
            full_expr = enable_expr + update_expr + frame_expr
            try:
                R_t = self.bdd.add_expr(" & ".join(full_expr))
            except Exception as e:
                print(f"Error building BDD for transition {t_id}: {e}")
                continue
            R_total = R_total | R_t
        return R_total

    def compute_reachable_states(self):
        start = time.time()

        R = self.build_transition()

        current_states = self.build_initial_state_bdd()
        new_states = current_states

        while True:

            transitions = new_states & R

            # Remove current states to get only new states
            exist_vars = [f'x_{p.replace("-", "_")}' for p in self.petri_net.places]
            next_states_vars = self.bdd.exist(exist_vars, transitions)

            # Rename next state vars to current state vars
            next_states = self.bdd.let(self.rename_map, next_states_vars)

            # New states are those not already in the set of reachable states
            new_states = next_states & ~current_states

            if new_states == self.bdd.false:
                break

            # Update current states
            current_states = current_states | new_states

        end = time.time()
        total_states = self.bdd.count(current_states)

        return current_states, total_states, end - start

    def print_reachable_states_list(self, states_bdd):
        it = self.bdd.pick_iter(states_bdd)
        for state in it:
            marking = {}
            for p in self.petri_net.places:
                marking[p] = int(state[f"x_{p}"])
            print(marking)

    def get_expr_from_bdd(self, bdd_node):
        if bdd_node is None:
            return "None"

        return self.bdd.to_expr(bdd_node)
