from ariths_gen.one_bit_circuits.logic_gates import (
    OrGate,
    AndGate,
)

from ariths_gen.wire_components import Bus

from ariths_gen.core.arithmetic_circuits import GeneralCircuit

class LowerOrderApproxMtoNCompressor(GeneralCircuit):
    def __init__(self, a: Bus, prefix="", name="approx_cmprs", order=0, **kwargs):
        """
        Implements N-to-⌈N/2⌉ lower-order approximate compressor.

        For example, 3/2, 4/2, 5/3, and 6/3 approx. compressors.

        ```

            ┌─────────────┐    
        ───►│             ├───►
        ───►│             │    
        ───►│  N : ⌈N/2⌉  ├───►
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


        # reversed list of inputs
        inputs = [self.a.get_wire(self.N - 1 - i) for i in range(self.N)]
        
        num_pairs = self.N // 2

        # outputs of AND and OR gates
        Ands = []
        Ors = []
        
        for i in range(num_pairs):
            w0 = inputs[2*i]
            w1 = inputs[2*i+1]
            
            and_gate = AndGate(w0, w1, prefix=f"{self.prefix}_and_{i}")
            or_gate = OrGate(w0, w1, prefix=f"{self.prefix}_or_{i}")
            
            self.add_component(and_gate)
            self.add_component(or_gate)
            
            Ands.append(and_gate.out)
            Ors.append(or_gate.out)
            
        outputs = []
        
        if self.N % 2 == 0:
            for i in range(num_pairs):
                next_idx = (i + 1) % num_pairs
                or_gate = OrGate(Ands[i], Ors[next_idx], prefix=f"{self.prefix}_out_{i}")
                self.add_component(or_gate)
                outputs.append(or_gate.out)
        else:
            
            unpaired = inputs[-1]
            
            for i in range(num_pairs - 1):
                or_gate = OrGate(Ands[i], Ors[i+1], prefix=f"{self.prefix}_out_{i}")
                self.add_component(or_gate)
                outputs.append(or_gate.out)
            
            outputs.append(Ors[0])
            
            last_or = OrGate(Ands[num_pairs-1], unpaired, prefix=f"{self.prefix}_out_{num_pairs}")
            self.add_component(last_or)
            outputs.append(last_or.out)

        for out_pin, wire_out in enumerate(outputs):
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
        ───►│ N:⌈N/2⌉ ├───►
        ───►│         │
        ───►│         ├───►
            └─────────┘

            ┌─────────┐
        ───►│         ├───►
        ───►│         │
        ───►│         ├───►
        ───►│         │
        ───►│ N:⌈N/2⌉ ├───►
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

        if first > N:
            first = N

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
                order=order,
                inner_component=True
            )
            order += 1
            self.add_component(block)

            # connect output wires of subcomponents to main component output
            for j, w in enumerate(block.out.bus):
                self.out.connect(out_idx, w, inserted_wire_desired_index=j)
                out_idx += 1
