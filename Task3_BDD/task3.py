import time
import numpy as np
from dd import autoref as bdd
import sys
import re
from Task1_Parser.task1 import PetriNet

sys.setrecursionlimit(10000)

class BDD_Reachability:
    def __init__(self, petri_net: PetriNet):
        self.petri_net = petri_net
        self.bdd = bdd.BDD()
        self._initialize_bdd_variables()
    
    def _sanitize_name(self, name):
        sanitized = re.sub(r'[^a-zA-Z0-9]', '_', name)
        if sanitized and sanitized[0].isdigit():
            sanitized = f'p_{sanitized}'
        return sanitized
    
    def _initialize_bdd_variables(self):
        for p in self.petri_net.places:
            safe_p = self._sanitize_name(p)
            self.bdd.declare(f"{safe_p}")
            self.bdd.declare(f"y_{safe_p}")

        self.rename_map = {
            f'y_{self._sanitize_name(p)}': f'{self._sanitize_name(p)}'
            for p in self.petri_net.places
        }
        self.reverse_name_map = {}
        for p in self.petri_net.places:
            safe_p = self._sanitize_name(p)
            self.reverse_name_map[f'{safe_p}'] = f'{p}'
            self.reverse_name_map[f'y_{safe_p}'] = f'y_{p}'
        self._reachable_bdd = None

    def build_initial_state_bdd(self):
        expr = []
        for i, p in enumerate(self.petri_net.places):
            safe_p = self._sanitize_name(p)
            if self.petri_net.initial_marking[i] > 0:
                expr.append(f"{safe_p}")
            else:
                expr.append(f"~{safe_p}")
        return self.bdd.add_expr(" & ".join(expr))

    def build_transition(self):
        R_total = self.bdd.false

        for t_idx in range(self.petri_net.num_transitions):
            t_id = self.petri_net.transitions[t_idx]

            input_places = np.where(self.petri_net.pre_matrix[:, t_idx] == 1)[0]
            output_places = np.where(self.petri_net.post_matrix[:, t_idx] == 1)[0]

            input_ids = [self.petri_net.places[i] for i in input_places]
            output_ids = [self.petri_net.places[i] for i in output_places]

            involved_places = set(input_ids) | set(output_ids)

            enable_expr = []
            for p in input_ids:
                safe_p = self._sanitize_name(p)
                enable_expr.append(f"{safe_p}")
            for p in output_ids:
                if p not in input_ids:
                    safe_p = self._sanitize_name(p)
                    enable_expr.append(f"~{safe_p}")

            update_expr = []
            for p in input_ids:
                if p not in output_ids:
                    safe_p = self._sanitize_name(p)
                    update_expr.append(f"~y_{safe_p}")

            for p in output_ids:
                safe_p = self._sanitize_name(p)
                update_expr.append(f"y_{safe_p}")

            frame_expr = []
            for p in self.petri_net.places:
                if p not in involved_places:
                    safe_p = self._sanitize_name(p)
                    frame_expr.append(f"(y_{safe_p} <-> {safe_p})")

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

            exist_vars = [f'{self._sanitize_name(p)}' for p in self.petri_net.places]
            next_states_vars = self.bdd.exist(exist_vars, transitions)
            next_states = self.bdd.let(self.rename_map, next_states_vars)
            new_states = next_states & ~current_states

            if new_states == self.bdd.false:
                break

            current_states = current_states | new_states

        end = time.time()
        total_states = self.bdd.count(current_states)

        return current_states, total_states, end - start

    def print_reachable_states_list(self, states_bdd):
        it = self.bdd.pick_iter(states_bdd)
        for state in it:
            marking = {}
            for p in self.petri_net.places:
                safe_p = self._sanitize_name(p)
                marking[p] = int(state[f"{safe_p}"])
            print(marking)

    def get_expr_from_bdd(self, bdd_node):
        if bdd_node is None:
            return "None"

        return self.bdd.to_expr(bdd_node)
    
    def dump_bdd(self, filename, roots):
        self.bdd.dump(filename, roots=roots)
        
        with open(filename, 'r') as f:
            content = f.read()
        
        for sanitized, original in self.reverse_name_map.items():
            pattern = re.escape(sanitized) + r'(?=[-"])'
            content = re.sub(pattern, original, content)
        

        content = re.sub(r'(label="[^"]+)-\d+"', r'\1"', content)
        
        with open(filename, 'w') as f:
            f.write(content)
    
    def dot_to_png(self, dot_filename, png_filename):
        try:
            import graphviz
            with open(dot_filename, 'r') as f:
                dot_content = f.read()
            graph = graphviz.Source(dot_content)
            graph.format = 'png'
            graph.render(filename=png_filename, cleanup=True)
        except ImportError:
            print(f"Warning: graphviz not installed. Skipping PNG generation.")
        except Exception as e:
            error_msg = str(e).lower()
            if 'stack' in error_msg or 'recursion' in error_msg:
                print(f"Warning: BDD too large for PNG visualization (stack overflow). DOT file saved successfully.")
            else:
                print(f"Warning: Could not generate PNG: {e}")
            pass
