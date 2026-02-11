from ariths_gen.one_bit_circuits.logic_gates import (
    NorGate,
    XnorGate,
    NotGate,
    OrGate,
    AndGate,
)

from ariths_gen.wire_components import Bus

from ariths_gen.core.arithmetic_circuits import GeneralCircuit

class LowerOrderApproxMtoNCompressor(GeneralCircuit):
    def __init__(self, a: Bus, prefix="", name="approx_cmprs", order=0, **kwargs):
        """
        Implements M-to-⌈M/2⌉ lower-order approximate compressor.

        For example, 3/2, 4/2, 5/3, and 6/3 approx. compressors.

        ```

            ┌─────────────┐    
        ───►│             ├───►
        ───►│             │    
        ───►│  M : ⌈M/2⌉  ├───►
        ───►│             │    
        ───►│             ├───►
            └─────────────┘
          .                 .   
          .                 .   
          .                 .   

        ```
        Args:
            a (Bus): Input bus.
            prefix (str): Naming prefix.
            name (str): Component name.
            order (int): Compressor order.
            **kwargs: Additional arguments.
        """
        self.N = a.N
        self.M = (self.N + 1) // 2 # ceil(N/2)

        super().__init__(
            inputs=[a],
            name=f"approx_cmprs_{self.N}_{self.M}",
            prefix=prefix,
            out_N=self.M,
            order=order,
            **kwargs
        )

        self.create_compressor()
        
        
    def pair_p_products(self):
        """
        Pairwise partial product in order.
        Returns:
            List of groups of two pp.
            If the number of pps is odd, the last pp remains unpaired.
        
        :param self: compressor itself
        """
        pairs = []
        for i in range(0, self.N, 2):
            wire0 = self.a.get_wire(i)
            wire1 = self.a.get_wire(i + 1) if (i + 1 < self.N) else None
            pairs.append((wire0, wire1))

        return pairs
    

    def create_and_or_pairs(self, pairs):
        """
        Creates AND and OR pairs from each partial product pair.
        
        :param self: compressor itself
        :param pairs: list of partial product pairs
        """
        and_outputs_list =  []
        or_outputs_list = []

        for i, (w0, w1) in enumerate(pairs):
            if w1 is None:
                # append partial product alone (will not be recoded)
                or_outputs_list.append(w0)
            else:
                # create lists of ANDs and ORs from each pair
                and_gate = AndGate(w0, w1, prefix=f"{self.prefix}_and_{i}")
                or_gate = OrGate(w0, w1, prefix=f"{self.prefix}_or_{i}")

                self.add_component(and_gate)
                self.add_component(or_gate)

                and_outputs_list.append(and_gate.out)
                or_outputs_list.append(or_gate.out)

        return and_outputs_list, or_outputs_list
    
    def recode_and_or(self, and_list, or_list):
        """
        Provides AND-OR recoding for each partial product pair 
        using previously created AND and OR lists.
        
        :param self: compressor itself
        :param and_list: list of AND gates
        :param or_list: list of OR gates

        Returns:
            Recoded partial products in form of a list
        """
        outputs = []

        or_count = len(or_list)

        for i in range(or_count):
            a_i = and_list[i] if i < len(and_list) else None
            next_or_gate = or_list[(i + 1) % or_count]

            if a_i is None:
                # unpaired partial product
                outputs.append(next_or_gate)
            else:
                or_gate = OrGate(a_i, next_or_gate, prefix=f"{self.prefix}_out_{i}")
                self.add_component(or_gate)
                outputs.append(or_gate.out)

        return outputs
        
    def create_compressor(self):
        """
        Creates lower-order (3/2, 4/2, 5/3 or 6/3) approximate compressor.
        Connects outputs of recoded pairs to the output of entire (higher-order) compressor.
        
        :param self: compressor
        """
        pairs = self.pair_p_products()
        and_list, or_list = self.create_and_or_pairs(pairs)
        outs = self.recode_and_or(and_list, or_list)

        for out_pin, wire_out in enumerate(outs):
            self.out.connect(out_pin, wire_out)



class GeneralApproxMtoNCompressor(GeneralCircuit):
    """
    Implements a linear connection of approximate compressors.

    Depending on the input bus length:
        - Uses higher-order compressors if length > 6.
        - Uses lower-order compressors if length <= 6.
    """
    def __init__(self, a: Bus, prefix="", name="general_approx_cmprs", **kwargs):
        """
        Construct a hierarchical M-to-⌈M/2⌉ approximate compressor.
        ```

            ┌─────────┐
        ───►│         ├───►
        ───►│         │
        ───►│ M:⌈M/2⌉ ├───►
        ───►│         │
        ───►│         ├───►
            └─────────┘

            ┌─────────┐
        ───►│         ├───►
        ───►│         │
        ───►│         ├───►
        ───►│         │
        ───►│ M:⌈M/2⌉ ├───►
        ───►│         │
        ───►│         ├───►
        ───►│         │
        ───►│         ├───►
            └─────────┘
                .
                .
                .
        ```

        The block connects multiple lower-order approximate
        compressors to form a higher-order approximate compressor.

        Args:
            a (Bus): Input bus.
            prefix (str): Naming prefix.
            name (str): Component name.
            **kwargs: Additional arguments.
        """
        self.N = a.N
        self.M = (self.N + 1) // 2 # ceil(N/2)

        super().__init__(
            inputs=[a],
            name=f"{name}_{self.N}_{self.M}",
            prefix=prefix,
            out_N=self.M,
            **kwargs
        )

        self.create()


    def split_inputs(self):
        """
        Split input wires according to the following table:

                       +------------------------------+
                       |       COMPRESSOR TYPE        |
            +----------+-----+------------+-----+-----+
            |  n mod 4 | 3/2 |    4/2     | 5/3 | 6/3 |
            +----------+-----+------------+-----+-----+
            |     0    |  -  |    n/4     |  -  |  -  |
            +----------+-----+------------+-----+-----+
            |     1    |  -  |  ⌊n/4⌋ - 1 |  1  |  -  |
            +----------+-----+------------+-----+-----+
            |     2    |  -  |  ⌊n/4⌋ - 1 |  -  |  1  |
            +----------+-----+------------+-----+-----+
            |     3    |  1  |   ⌊n/4⌋    |  -  |  -  |
            +----------+-----+------------+-----+-----+
        
        Returns:
            Higher-order approx. compressor input wires split into
            partial lower-order approx. compressor inputs.
        """
        groups = []
        N = self.N
        i = 0
        gid = 0  # ID of group of wires belonging to each compressor input

        remain = N % 4

        # compute first compressor input size (ranges from 3 to 6)
        first = remain + 4 if remain < 3 else remain

        # create a group for the first lower-order compressor
        if N >= first:
            sub = Bus(prefix=f"{self.prefix}_grp{gid}", N=first)
            for j in range(first):
                sub.connect(j, self.a.get_wire(i + j))
            groups.append(sub)
            i += first
            N -= first
            gid += 1

        # create a group for each 4/2 compressor remaining
        while N > 0:
            sub = Bus(prefix=f"{self.prefix}_grp{gid}_4", N=4)
            for j in range(4):
                sub.connect(j, self.a.get_wire(i + j))
            groups.append(sub)
            i += 4
            N -= 4
            gid += 1

        return groups


    def create(self):
        groups = self.split_inputs()
        out_idx = 0
        order = 0 # order of each subcomponent (lower-order compressor) in the component

        for _, g in enumerate(groups):
            block = LowerOrderApproxMtoNCompressor(
                g,
                prefix=f"{self.prefix}_{order}",
                order=order
            )
            order += 1
            self.add_component(block)

            # connect output wires of subcomponents to main component output
            for j, w in enumerate(block.out.bus):
                self.out.connect(out_idx, w, inserted_wire_desired_index=j)
                out_idx += 1
