import pulp
import time
import numpy as np
from Task1_Parser.task1 import PetriNet
from Task3_BDD.task3 import BDD_Reachability


class ILP_BDD_Deadlock_Detection:
    def __init__(
        self,
        petri_net: PetriNet,
        bdd_reach: BDD_Reachability = None,
        reachable_marking_nums: int = None,
        marking_limit: int = 64,
        place_limit: int = 16,
        transition_limit: int = 12,
    ):

        self.petri_net = petri_net
        # Use provided BDD_Reachability if given, otherwise create one
        if bdd_reach is None:
            self.bdd_reach = BDD_Reachability(petri_net)
        else:
            self.bdd_reach = bdd_reach
        self.bdd = self.bdd_reach.bdd
        self.reachable_marking_nums = reachable_marking_nums
        self.marking_limit = marking_limit
        self.place_limit = place_limit
        self.transition_limit = transition_limit
        self.place_nums = len(petri_net.places)
        self.transition_nums = len(petri_net.transitions)

        # input_places for every transition
        self.input_places = []
        for t_idx, t in enumerate(self.petri_net.transitions):
            idxs = np.where(self.petri_net.pre_matrix[:, t_idx] == 1)[0]
            self.input_places.append([self.petri_net.places[i] for i in idxs])
        # output_places for every transition
        self.output_places = []
        for t_idx, t in enumerate(self.petri_net.transitions):
            idxs = np.where(self.petri_net.post_matrix[:, t_idx] == 1)[0]
            self.output_places.append([self.petri_net.places[i] for i in idxs])

        # Build ILP model
        self.ilp_model = pulp.LpProblem("Deadlock_ILP", pulp.LpMaximize)
        self.enabled_vars = {
            t: pulp.LpVariable(f"e_{t}", 0, 1, cat="Binary")
            for t in self.petri_net.transitions
        }

        self.t_constraints = {}
        for t in self.petri_net.transitions:
            e = self.enabled_vars[t]
            cons = pulp.LpConstraint(
                e, sense=pulp.LpConstraintLE, rhs=1, name=f"cons_{t}"
            )
            self.ilp_model.addConstraint(cons)
            self.t_constraints[t] = cons

        self.ilp_model += pulp.lpSum(self.enabled_vars.values())
        self.solver = pulp.PULP_CBC_CMD(msg=False)

        # If reachable_marking_nums not provided, compute it (may be expensive)
        if self.reachable_marking_nums is None:
            try:
                _, total_states, _ = self.bdd_reach.compute_reachable_states()
                self.reachable_marking_nums = total_states
            except Exception:
                self.reachable_marking_nums = 0

    def _state_to_marking(self, state):
        return {
            p: int(bool(state.get(f"x_{p.replace('-', '_')}", 0)))
            for p in self.petri_net.places
        }

    def _is_deadlock_ilp(self, marking):
        all_zero = True

        # Compute rhs per transition and update constraint RHS
        for t_idx, t in enumerate(self.petri_net.transitions):
            inputs = self.input_places[t_idx]
            if not inputs:
                # transition with empty pre -> always enabled -> rhs = 1
                rhs = 1
            else:
                # rhs = 1 only if every input place has token 1
                rhs = 1
                for p in inputs:
                    if marking.get(p, 0) == 0:
                        rhs = 0
                        break

            # update the corresponding constraint
            self.t_constraints[t].changeRHS(rhs)
            if rhs == 1:
                all_zero = False

        # Early decision: if all rhs are 0 => no transition can be enabled
        if all_zero:
            return True

        # Solve ILP
        self.ilp_model.solve(self.solver)
        enabled_total = 0
        for v in self.enabled_vars.values():
            val = v.varValue
            enabled_total += int(round(val)) if val is not None else 0

        return enabled_total == 0

    def _build_dead_bdd(self):
        # Build 'enabled_any' then dead_bdd = ~enabled_any
        enabled_any = self.bdd.false
        for t_idx, t in enumerate(self.petri_net.transitions):
            inputs = self.input_places[t_idx]
            outputs = self.output_places[t_idx]
            # ignore transition dummy (no input and no output)
            if not inputs and not outputs:
                continue
            if not inputs:
                t_enabled = self.bdd.true
            else:
                t_enabled = self.bdd.true
                for p in inputs:
                    safe_p = p.replace("-", "_")
                    t_enabled &= self.bdd.var(f"x_{safe_p}")
            enabled_any |= t_enabled

        dead_bdd = ~enabled_any
        return dead_bdd

    def find_deadlock(self, states_bdd):
        start = time.time()
        # small net: solve ILP on every reachable marking
        if (
            self.reachable_marking_nums <= self.marking_limit
            and self.place_nums <= self.place_limit
            and self.transition_nums <= self.transition_limit
        ):
            for state in self.bdd.pick_iter(states_bdd):
                marking = self._state_to_marking(state)
                if self._is_deadlock_ilp(marking):
                    return marking, time.time() - start
            return None, time.time() - start

        # medium net: encoding constraints ILP into BDD to filter candidates, then verify again with ILP
        dead_bdd = self._build_dead_bdd()
        candidate_bdd = states_bdd & dead_bdd

        # No possible dead marking
        if candidate_bdd == self.bdd.false:
            return None, time.time() - start

        # Pick one candidate marking from BDD to verify
        example = self.bdd.pick(candidate_bdd)
        marking = self._state_to_marking(example)
        if self._is_deadlock_ilp(marking):
            return marking, time.time() - start

        # If BDD said dead but ILP says not dead => sample a few more candidates (rare)
        for i, state in enumerate(self.bdd.pick_iter(candidate_bdd)):
            if i >= 100:  # verify more candidate if ILP says not dead
                break
            m = self._state_to_marking(state)
            if self._is_deadlock_ilp(m):
                return m, time.time() - start

        return None, time.time() - start

    def print_deadlock(self, deadlock):
        if deadlock is not None:
            print(deadlock)
