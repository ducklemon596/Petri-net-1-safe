import xml.etree.ElementTree as et
import numpy as np


class PetriNet:
    def __init__(self, pnml_file_path):
        self.places = []                # List of Place IDs(string)
        self.transitions = []           # List of Transition IDs(string)
        self.initial_marking = None     # Initial marking vector (NumPy array)
        self.pre_matrix = None          # Input matrix (NumPy matrix)
        self.post_matrix = None         # Output matrix (NumPy matrix)

        self.place_to_index = {}        # Map: Place ID -> index
        self.transition_to_index = {}   # Map: Transition ID -> index

        # Weight of places (NumPy array) for TASK 5
        self.c = None

        self.num_places = 0
        self.num_transitions = 0

        self.read_pnml_file(pnml_file_path)

    # =====================================================================
    #  PARSE PNML FILE
    # =====================================================================
    def read_pnml_file(self, file_path: str):
        try:
            try:
                tree = et.parse(file_path)
                root = tree.getroot()
            except FileNotFoundError:
                print(f"[Error] File not found at path: {file_path}")
                return
            except et.ParseError as e:
                print(f"[Error] PNML file has invalid XML structure: {e}")
                return

            # Locate the <net> node
            net = root.find(".//{*}net")
            if net is None:
                raise ValueError("PNML file does not contain a <net> element.")

            M0 = []

            # Extract places
            for place in net.iter():
                if 'place' in place.tag:
                    pid = place.attrib.get("id")
                    if not pid:
                        continue

                    self.places.append(pid)

                    # Read initial marking
                    marking = 0
                    for child in place:
                        if 'initialMarking' in child.tag:
                            text_node = child.find("{*}text")
                            if text_node is not None and text_node.text:
                                marking = int(text_node.text.strip())
                            break
                    if marking > 1 or marking < 0:
                        raise ValueError("Invalid initial marking")
                    M0.append(marking)

            # Extract transitions
            for trans in net.iter():
                if 'transition' in trans.tag:
                    tid = trans.attrib.get("id")
                    if not tid:
                        continue
                    self.transitions.append(tid)

            # Build indexes
            self.num_places = len(self.places)
            self.num_transitions = len(self.transitions)
            self.place_to_index = {p: i for i, p in enumerate(self.places)}
            self.transition_to_index = {
                t: i for i, t in enumerate(self.transitions)}

            self.initial_marking = np.array(M0)
            self.pre_matrix = np.zeros(
                (self.num_places, self.num_transitions), dtype=int)
            self.post_matrix = np.zeros(
                (self.num_places, self.num_transitions), dtype=int)

            if self.num_places == 0:
                raise ValueError("No Places found in the file.")

            # Parse arcs
            for arc in net.iter():
                if 'arc' in arc.tag:
                    source = arc.attrib.get("source")
                    target = arc.attrib.get("target")

                    if source in self.place_to_index and target in self.transition_to_index:
                        # Place -> Transition (Pre-matrix)
                        p_idx = self.place_to_index[source]
                        t_idx = self.transition_to_index[target]
                        self.pre_matrix[p_idx, t_idx] = 1

                    elif source in self.transition_to_index and target in self.place_to_index:
                        # Transition -> Place (Post-matrix)
                        t_idx = self.transition_to_index[source]
                        p_idx = self.place_to_index[target]
                        self.post_matrix[p_idx, t_idx] = 1
                    else:
                        raise ValueError("Invalid arc")
        except ValueError as ve:
            print(f"[Data Error] {ve}")
        except Exception as e:
            print(f"[Unexpected Error] An unexpected error occurred: {e}")

    def read_weight(self, weight_file_path):
        try:
            with open(weight_file_path, 'r') as f:
                # Read all content and split based on whitespace/newlines
                content = f.read().split()

                # Convert list of strings to list of integers
                weights = [int(x) for x in content]

            # Verify if the number of weights matches the number of Places
            if len(weights) != self.num_places:
                raise ValueError(
                    f"Size Error: Weight file has {len(weights)} values, "
                    f"but Petri Net has {self.num_places} places."
                )

            # Assign to self.c
            self.c = np.array(weights)

        except FileNotFoundError:
            print(f"Error: File not found at {weight_file_path}")
        except ValueError as e:
            print(f"Data Error: {e}")
