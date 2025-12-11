import numpy as np
from collections import deque
import time
from Task1_Parser.task1 import PetriNet


class ExplicitTraverse:
    def __init__(self, petri_net: PetriNet):
        self.petri_net = petri_net

    def compute_reachable_markings(self, method="bfs", timeout=20.0):
        try:
            start_time = time.time()

            if method.lower() not in ["bfs", "dfs"]:
                raise ValueError("Invalid method. Use 'bfs' or 'dfs'")

            dq = deque([self.petri_net.initial_marking])
            visited = {tuple(self.petri_net.initial_marking)}

            marking_states = [self.petri_net.initial_marking]

            while dq:
                if time.time() - start_time > timeout:
                    return -1, time.time() - start_time

                if method.lower() == "bfs":
                    m = dq.popleft()
                else:
                    m = dq.pop()

                enabled_t = [
                    t
                    for t in range(self.petri_net.num_transitions)
                    if np.all(m >= self.petri_net.pre_matrix[:, t])
                ]

                for t in enabled_t:
                    m_new = (
                        m
                        - self.petri_net.pre_matrix[:, t]
                        + self.petri_net.post_matrix[:, t]
                    )
                    m_new_tuple = tuple(m_new)

                    if m_new_tuple not in visited:
                        visited.add(m_new_tuple)
                        dq.append(m_new)
                        marking_states.append(m_new)

            elapsed_time = time.time() - start_time
            return marking_states, elapsed_time

        except Exception as e:
            print(f"[Error] {e}")
            return [], 0

    def print_reachable_markings(self, method="bfs", timeout=20.0):
        states, elapsed_time = self.compute_reachable_markings(method, timeout)

        if states == -1:
            print(f"Time out (exceeded {timeout} seconds)")
            return

        print(f"Total states found: {len(states)}")
        print(f"Execution time: {elapsed_time:.6f} seconds")
        print("-" * 40)

        print("Reachable marking states:")
        print("-" * 40)

        for state in states:
            marking = {
                self.petri_net.places[i]: int(state[i])
                for i in range(self.petri_net.num_places)
            }
            print(marking)

        print("-" * 40)
