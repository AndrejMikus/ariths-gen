from ariths_gen.wire_components import Bus, ConstantWireValue0, ConstantWireValue1
from ariths_gen.core.arithmetic_circuits import MultiplierCircuit
from ariths_gen.one_bit_circuits.one_bit_components import HalfAdder, FullAdder
from ariths_gen.multi_bit_circuits.approximative_compressors import GeneralApproxMtoNCompressor
from ariths_gen.multi_bit_circuits.adders.carry_lookahead_adder import UnsignedCarryLookaheadAdder
from ariths_gen.one_bit_circuits.logic_gates import AndGate, NandGate, XorGate
import math


def _variant_configuration(variant: str):
    """
    Sets mode from the instance argument.
    """

    # default mode for a multiplier
    use_truncation = False
    approx_stages = None

    if variant == "1StepFull":
        approx_stages = 1
    elif variant == "2StepsFull":
        approx_stages = 2
    elif variant == "1StepTrunc":
        use_truncation = True
        approx_stages = 1
    elif variant == "2StepsTrunc":
        use_truncation = True
        approx_stages = 2

    return use_truncation, approx_stages


class _ApproxCompressorBasedMultiplierBase(MultiplierCircuit):
    """
    Base class for approximate multipliers that use approximate compressors
    to reduce partial products in PPM columns.

    Both unsigned and signed versions inherit from this class. Defaults to the unsigned version.
    """

    # gates used for generating partial products in the unsigned version of the multiplier
    partial_product_gate_types = (AndGate,)

    def __init__(
        self,
        a: Bus,
        b: Bus,
        prefix: str = "",
        name: str = "u_apprx_cmpr",
        unsigned_adder_class_name=UnsignedCarryLookaheadAdder,
        variant: str = "",
        signed: bool = False,
        **kwargs,
    ):
        # the wider of input buses will be used
        self.N = max(a.N, b.N)
        self.variant = variant

        # default settings for reduction
        self.use_truncation = False
        self.use_dadda = False
        self.approx_stages = None
        self.h_max_next = (self.N + 1) // 2

        # base multiplier structure
        super().__init__(inputs=[a, b], prefix=prefix, name=name, signed=signed, out_N=self.N * 2, **kwargs)

        # build the partial product matrix
        self.extend_buses(a, b)
        self.columns = self.init_column_heights()
        self.prepare_columns()

        self.use_truncation, self.approx_stages = _variant_configuration(self.variant)

        # remove lower columns when trucation is set
        if self.use_truncation:
            for col_idx in range(self.N - 1):
                self.columns[col_idx] = [0]

        self.reduce_columns()
        self.finalize_output(unsigned_adder_class_name, kwargs)
        self.post_finalize()


    def extend_buses(self, a: Bus, b: Bus):
        """
        Extends the shorter of the input buses.
        """
        self.a.bus_extend(N=self.N, prefix=a.prefix)
        self.b.bus_extend(N=self.N, prefix=b.prefix)


    def prepare_columns(self):
        """
        Rearranges partial products so that every gate appears only once in the matrix.
        """

        self.prepare_extra_columns()

        for col_idx in range(len(self.columns)):
            new_column = [self.get_column_height(col_idx)]

            # replace gates with their outputs
            for obj in self.columns[col_idx][1:]:
                if isinstance(obj, self.partial_product_gate_types):
                    # avoid adding the same gate multiple times
                    if obj.prefix not in self._prefixes:
                        self.add_component(obj)
                    new_column.append(obj.out)
                else:
                    new_column.append(obj)

            self.columns[col_idx] = new_column


    def prepare_extra_columns(self):
        """
        Adds extra partial product columns needed by signed multipliers.
        """
        # only signed versions add this extra bit
        pass


    def post_finalize(self):
        """
        Fixes the final output for signed multipliers after the main adder is added.
        """
        # signed versions use an extra XOR gate to correct the last output bit
        pass


    def low_part_limit(self, num_columns: int):
        """
        Return the last column index that should use only approximate reduction.

        Defaults to input width (N), which represents the lower half of the PPM.
        """
        return self.N


    def reduce_columns(self):
        """
        Provide partial product reduction with respect to the multiplier variants and parameters.
        """
        stage = 0

        # reduce until every column has at most height of 2 (which will be completed by an adder)
        while not all(self.get_column_height(c) <= 2 for c in range(len(self.columns))):
            stage += 1

            # find the highest column in the currect stage
            current_max = max(self.get_column_height(c) for c in range(len(self.columns)))

            # after completing the configured number of reductions using approx. compressors,
            # continue the reduction using Dadda
            if self.approx_stages is not None and stage > self.approx_stages:
                self.use_dadda = True

            if self.use_dadda:
                _, self.h_max_next = self.get_maximum_height(current_max)
            else:
                self.h_max_next = math.ceil(current_max / 2)

            fa, ha, j, _, _, _ = self.allocate_compressors()
            use_approx = self.approx_stages is None or stage <= self.approx_stages

            for col_idx in range(len(self.columns)):
                self.connect_components(col_idx, fa[col_idx], ha[col_idx], j[col_idx], use_approx)


    def finalize_output(self, unsigned_adder_class_name, kwargs):
        """
        Provide summing up the remaining two bit rows.
        """
        if self.N > 1:
            adder_a_wires = []
            adder_b_wires = []

            for col in range(1, len(self.columns)):
                h = self.get_column_height(col)
                # resolve the cases for summing up columns of height less than 2
                adder_a_wires.append(self.add_column_wire(column=col, bit=0) if h > 0 else ConstantWireValue0())
                adder_b_wires.append(self.add_column_wire(column=col, bit=1) if h > 1 else ConstantWireValue0())

            adder_a = Bus(prefix=f"{self.prefix}_final_a", wires_list=adder_a_wires)
            adder_b = Bus(prefix=f"{self.prefix}_final_b", wires_list=adder_b_wires)

            # final adder defaults to Kogge-Stone but allow any other
            # variants of an unsigned adder to realize the summation
            final_adder = unsigned_adder_class_name(
                a=adder_a,
                b=adder_b,
                prefix=self.prefix,
                name="final_adder",
                inner_component=True,
                **kwargs,
            )
            self.add_component(final_adder)

            # connect the adder output to the multiplier output
            for i in range(final_adder.out.N):
                if (i + 1) < self.out.N:
                    self.out.connect(i + 1, final_adder.out.get_wire(i))
        else:
            # 1 bit multiplier -- second output is 0
            self.out.connect(1, ConstantWireValue0())

        if self.get_column_height(0) > 0:
            self.out.connect(0, self.add_column_wire(column=0, bit=0))

        # set the last m bits  of output to 0 if truncation is enabled
        if self.use_truncation:
            for i in range(self.N - 1):
                self.out.connect(i, ConstantWireValue0())

    def add_full_adder(self, column_idx: int, prefix_suffix: str = "fa"):
        """
        Adds a full adder to reduce 3 bits in one column.
        """
        fa = FullAdder(
            self.add_column_wire(column=column_idx, bit=0),
            self.add_column_wire(column=column_idx, bit=1),
            self.add_column_wire(column=column_idx, bit=2),
            prefix=f"{self.prefix}_{prefix_suffix}_{column_idx}_{self.get_instance_num(cls=FullAdder)}",
        )
        self.add_component(fa)

        # move the carry bit to the next column
        next_col = min(column_idx + 1, len(self.columns) - 1)

        self.update_column_heights(curr_column=column_idx, curr_height_change=-2, next_column=next_col, next_height_change=1)
        self.update_column_wires(curr_column=column_idx, next_column=next_col, adder=fa)

    def add_half_adder(self, column_idx: int):
        """
        Adds a half adder to reduce 2 bits in one column.
        """
        ha = HalfAdder(
            self.add_column_wire(column=column_idx, bit=0),
            self.add_column_wire(column=column_idx, bit=1),
            prefix=f"{self.prefix}_ha_{column_idx}_{self.get_instance_num(cls=HalfAdder)}",
        )
        self.add_component(ha)

        # move the carry bit to the next column
        next_col = min(column_idx + 1, len(self.columns) - 1)

        self.update_column_heights(curr_column=column_idx, curr_height_change=-1, next_column=next_col, next_height_change=1)
        self.update_column_wires(curr_column=column_idx, next_column=next_col, adder=ha)

    def allocate_compressors(self):
        """
        Allocates half adders, full adders and approximate compressors for each column.
        The design of the allocating algorithm origins from the article
        `Esposito, D., Napoli, E., Strollo A.G., De Caro, D.:
         Approximate Multipliers Based on New Approximate Compressors`.
        """
        num_columns = len(self.columns)
        fa = [0] * num_columns
        ha = [0] * num_columns
        j = [0] * num_columns
        C = [0] * num_columns
        h_next = [0] * num_columns

        h = [self.get_column_height(col) for col in range(num_columns)]

        low_part_limit = self.low_part_limit(num_columns)

        for col in range(low_part_limit):
            if h[col] <= 2:
                j[col] = 0
                h_next[col] = h[col]
            else:
                j[col] = h[col]
                h_next[col] = math.ceil(h[col] / 2)

        for col in range(low_part_limit, 2 * self.N - 3):
            C_prev = C[col - 1] if col > 0 else 0
            c_star = math.ceil((h[col] - self.h_max_next + C_prev) / 2)
            c_star = max(0, c_star)

            if col + 2 < num_columns:
                c_max = self.h_max_next - math.ceil(h[col + 2] / 3)
            else:
                c_max = self.h_max_next

            h_next[col] = h[col]
            c_double_star = 2 * c_max - h[col + 1] + self.h_max_next
            c_double_star = max(0, c_double_star)

            if c_double_star < c_star:
                C[col] = c_double_star
                fa[col] = c_double_star
                j[col] = 2 * (h[col] - self.h_max_next - 2 * fa[col] + C_prev)

                if (j[col] == 2) and (h[col] - 3 * fa[col] >= 3):
                    j[col] = 3

                ha[col] = C[col] - fa[col]
            else:
                C[col] = c_star
                if C[col] > 0:
                    fa[col] = math.ceil((h[col] - self.h_max_next + C_prev) / 2)
                    ha[col] = C[col] - fa[col]

            h_next[col] = h[col] - 2 * fa[col] - ha[col] - math.ceil(j[col] / 2) + C_prev

        return fa, ha, j, h, h_next, C

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        """
        Reduce one column using full adders, half adders, and approx. compressors (optionally)
        """

        # apply fa_count full adders
        for _ in range(fa_count):
            if self.get_column_height(column_idx) < 3:
                break
            self.add_full_adder(column_idx)
        
        # apply ha_count half adders
        for _ in range(ha_count):
            if self.get_column_height(column_idx) < 2:
                break
            self.add_half_adder(column_idx)

        current_height = self.get_column_height(column_idx)

        if use_approx:
            j = min(j, current_height)

            # prepare wires for compression
            wires_to_compress = [self.add_column_wire(column=column_idx, bit=i) for i in range(j)]
            compressor_in_bus = Bus(
                prefix=f"{self.prefix}_compr_in_{column_idx}_{self.get_instance_num(cls=GeneralApproxMtoNCompressor)}",
                wires_list=wires_to_compress,
            )

            compressor = GeneralApproxMtoNCompressor(
                a=compressor_in_bus,
                prefix=f"{self.prefix}_compr_{column_idx}_{self.get_instance_num(cls=GeneralApproxMtoNCompressor)}",
                inner_component=True,
            )
            self.add_component(compressor)

            self.update_column_heights(curr_column=column_idx, curr_height_change=-(j - compressor.out.N))

            # remove consumed input bits from the column
            for _ in range(j):
                self.columns[column_idx].pop(1)
            
            # append compressor output bits back to the same column
            for i in range(compressor.out.N):
                self.columns[column_idx].insert(len(self.columns[column_idx]), compressor.out.get_wire(i))
        else:
            # reduction using dadda rules
            while self.get_column_height(column_idx) > self.h_max_next:
                if self.get_column_height(column_idx) == self.h_max_next + 1:
                    self.add_half_adder(column_idx)
                else:
                    self.add_full_adder(column_idx, prefix_suffix="fa_exact")


class UnsignedApproxCompressorBasedMultiplier(_ApproxCompressorBasedMultiplierBase):
    """
    This class represents unsigned approximate compressor based multiplier.
    """
    def __init__(self, a: Bus, b: Bus, prefix: str = "", name: str = "u_apprx_cmpr",
                 unsigned_adder_class_name=UnsignedCarryLookaheadAdder, variant: str = "", **kwargs):
        super().__init__(
            a=a,
            b=b,
            prefix=prefix,
            name=name,
            unsigned_adder_class_name=unsigned_adder_class_name,
            variant=variant,
            signed=False,
            **kwargs,
        )


class SignedApproxCompressorBasedMultiplier(_ApproxCompressorBasedMultiplierBase):
    """
    This class represents signed approximate compressor based multiplier.
    """

    # gates used for generating partial products in the signed version of the multiplier
    partial_product_gate_types = (AndGate, NandGate)

    def __init__(self, a: Bus, b: Bus, prefix: str = "", name: str = "s_apprx_cmpr",
                 unsigned_adder_class_name=UnsignedCarryLookaheadAdder, variant: str = "", **kwargs):
        super().__init__(
            a=a,
            b=b,
            prefix=prefix,
            name=name,
            unsigned_adder_class_name=unsigned_adder_class_name,
            variant=variant,
            signed=True,
            **kwargs,
        )

    def extend_buses(self, a: Bus, b: Bus):
        """
        Extends both input buses to the same width using sign extension.
        """
        self.a.bus_extend(N=self.N, prefix=a.prefix, desired_extension_wire=self.a.get_wire(self.a.N - 1))
        self.b.bus_extend(N=self.N, prefix=b.prefix, desired_extension_wire=self.b.get_wire(self.b.N - 1))

    def prepare_extra_columns(self):
        """
        Adds extra correction bit to the start of the column like in Baugh-Wooley.
        """
        if self.N != 1:
            self.columns[self.N].insert(1, ConstantWireValue1())
            self.update_column_heights(curr_column=self.N, curr_height_change=1)

    def post_finalize(self):
        """
        Applies the final sign correction on the MSB.
        """
        obj_xor = XorGate(
            ConstantWireValue1(),
            self.out.get_wire(self.out.N - 1),
            prefix=self.prefix + "_xor" + str(self.get_instance_num(cls=XorGate)),
            parent_component=self,
        )
        self.add_component(obj_xor)
        self.out.connect(self.out.N - 1, obj_xor.out)


class UnsignedQuarterApproxCompressorMultiplier(UnsignedApproxCompressorBasedMultiplier):
    """
    Unsigned variant that applies approximate-only reduction
    to the lowest quarter of partial-product columns.
    """
    def low_part_limit(self, num_columns: int):
        # use only the first quarter of columns as the low approx. region
        return num_columns // 4

class SignedQuarterApproxCompressorMultiplier(SignedApproxCompressorBasedMultiplier):
    """
    Signed variant that applies approximate-only reduction
    to the lowest quarter of partial-product columns.
    """
    def low_part_limit(self, num_columns: int):
        # use only the first quarter of columns as the low approx. region
        return num_columns // 4

class UnsignedThresholdApproxCompressorMultiplier(UnsignedApproxCompressorBasedMultiplier):
    """
    Unsigned variant of approx. compressor  multiplier that uses column reduction using approx.
    compressors for columns that are higher than (threshold * (operand bitwidth)).
    """
    def __init__(self, *args, height_threshold=0.5, **kwargs):
        assert(0 <= height_threshold <= 1)
        self.height_threshold = height_threshold
        super().__init__(*args, **kwargs)

    def allocate_compressors(self):
        """
        Allocates half adders, full adders and approximate compressors for each column.
        The design of the allocating algorithm is inspired by the article
        `Esposito, D., Napoli, E., Strollo A.G., De Caro, D.:
         Approximate Multipliers Based on New Approximate Compressors`.
        Uses threshold to determine which columns have to be compressed by an approximate compressor.
        """
        num_columns = len(self.columns)
        fa = [0] * num_columns
        ha = [0] * num_columns
        j = [0] * num_columns
        C = [0] * num_columns
        h_next = [0] * num_columns

        h = [self.get_column_height(col) for col in range(num_columns)]
        

        threshold_height = 3 + self.height_threshold * (self.N - 2)

        low_part_limit = self.low_part_limit(num_columns)

        for col in range(low_part_limit):
            if h[col] < threshold_height:
                j[col] = 0
                h_next[col] = h[col]
            else:
                j[col] = h[col]
                h_next[col] = math.ceil(h[col] / 2)

        for col in range(low_part_limit, 2 * self.N - 3):
            C_prev = C[col - 1] if col > 0 else 0
            c_star = math.ceil((h[col] - self.h_max_next + C_prev) / 2)
            c_star = max(0, c_star)

            if col + 2 < num_columns:
                c_max = self.h_max_next - math.ceil(h[col + 2] / 3)
            else:
                c_max = self.h_max_next

            h_next[col] = h[col]
            c_double_star = 2 * c_max - h[col + 1] + self.h_max_next
            c_double_star = max(0, c_double_star)

            approx_compressors_width = 0

            if c_double_star < c_star:
                C[col] = c_double_star
                fa[col] = c_double_star
                approx_compressors_width = 2 * (h[col] - self.h_max_next - 2 * fa[col] + C_prev)

                if (approx_compressors_width == 2) and (h[col] - 3 * fa[col] >= 3):
                    approx_compressors_width = 3

                ha[col] = C[col] - fa[col]
            else:
                C[col] = c_star
                if C[col] > 0:
                    fa[col] = math.ceil((h[col] - self.h_max_next + C_prev) / 2)
                    ha[col] = C[col] - fa[col]

            approx_compressors_width = max(0, approx_compressors_width)

            if h[col] >= threshold_height:
                j[col] = min(approx_compressors_width, h[col])
            else:
                j[col] = 0

            h_next[col] = h[col] - 2 * fa[col] - ha[col] - math.floor(j[col] / 2) + C_prev

        return fa, ha, j, h, h_next, C
    
class SignedThresholdApproxCompressorMultiplier(SignedApproxCompressorBasedMultiplier):
    """
    Signed variant of approx. compressor  multiplier that uses column reduction using approx.
    compressors for columns that are higher than (threshold * (operand bitwidth)).
    """
    def __init__(self, *args, height_threshold=0.5, **kwargs):
        assert(0 <= height_threshold <= 1)
        self.height_threshold = height_threshold
        super().__init__(*args, **kwargs)

    def allocate_compressors(self):
        return UnsignedThresholdApproxCompressorMultiplier.allocate_compressors(self)

    
class UnsignedApproxGreedyPredefinedCompressorBWMultiplier(UnsignedApproxCompressorBasedMultiplier):
    """
    Unsigned multiplier that splits approximate compression into compressors
    with a limited maximum width given by a parameter.
    """
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        # set max compressor bandwidth
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)


    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        """
        Reduces one column using full adders, half adders and approx. compressors.
        Maximum width of compressor is given by a parameter.
        """
        # apply fa_count full adders
        for _ in range(fa_count):
            if self.get_column_height(column_idx) < 3:
                break
            self.add_full_adder(column_idx)

        # apply ha_count half adders
        for _ in range(ha_count):
            if self.get_column_height(column_idx) < 2:
                break
            self.add_half_adder(column_idx)

        current_height = self.get_column_height(column_idx)
        lowest_range_compr_bw = 3

        if use_approx:
            j = min(j, current_height)

            compressor_out_bits_total = 0
            bits_consumed_total = 0

            # split the column into blocks up to max_compressor_bw bits
            while j >= lowest_range_compr_bw:
                current_bw = min(j, self.max_compressor_bw)
                
                # prepare current_bw bits for compression
                wires_to_compress = [self.add_column_wire(column=column_idx, bit=i) for i in range(current_bw)]
                compressor_in_bus = Bus(
                    prefix=f"{self.prefix}_compr_in_{column_idx}_{self.get_instance_num(cls=GeneralApproxMtoNCompressor)}",
                    wires_list=wires_to_compress,
                )

                compressor = GeneralApproxMtoNCompressor(
                    a=compressor_in_bus,
                    prefix=f"{self.prefix}_compr_{column_idx}_{self.get_instance_num(cls=GeneralApproxMtoNCompressor)}",
                    inner_component=True,
                )
                self.add_component(compressor)
                
                # replace the used bits with compressor output bits
                for _ in range(current_bw):
                    self.columns[column_idx].pop(1)
                for i in range(compressor.out.N):
                    self.columns[column_idx].insert(len(self.columns[column_idx]), compressor.out.get_wire(i))

                bits_consumed_total += current_bw
                compressor_out_bits_total += compressor.out.N
                j -= current_bw

            self.update_column_heights(curr_column=column_idx, curr_height_change=-(bits_consumed_total - compressor_out_bits_total))

        else:
            # reduction using dadda rules
            while self.get_column_height(column_idx) > self.h_max_next:
                if self.get_column_height(column_idx) == self.h_max_next + 1:
                    self.add_half_adder(column_idx)
                else:
                    self.add_full_adder(column_idx, prefix_suffix="fa_exact")

class SignedApproxGreedyPredefinedCompressorBWMultiplier(SignedApproxCompressorBasedMultiplier):
    """
    Signed multiplier that splits approximate compression into compressors
    with a limited maximum width given by a parameter.
    """
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        # set max compressor bandwidth
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        return UnsignedApproxGreedyPredefinedCompressorBWMultiplier.connect_components(self, column_idx, fa_count, ha_count, j, use_approx)


class UnsignedThresholdGreedyPredefinedBWApproxCompressorMultiplier(UnsignedThresholdApproxCompressorMultiplier):
    """
    Combines reduction approach from threshold multiplier and the multiplier
    with the maximum input width of compressors. Unsigned version.
    """
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        # set max compressor bandwidth
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        return UnsignedApproxGreedyPredefinedCompressorBWMultiplier.connect_components(self, column_idx, fa_count, ha_count, j, use_approx)
    
class SignedThresholdGreedyPredefinedBWApproxCompressorMultiplier(SignedThresholdApproxCompressorMultiplier):
    """
    Combines reduction approach from threshold multiplier and the multiplier
    with the maximum input width of compressors. Signed version.
    """
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        # set max compressor bandwidth
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        return UnsignedApproxGreedyPredefinedCompressorBWMultiplier.connect_components(self, column_idx, fa_count, ha_count, j, use_approx)


class UnsignedApproxBalancedPredefinedBWCompressorMultiplier(UnsignedApproxCompressorBasedMultiplier):
    """
    Reduces one column using full adders, half adders and approx. compressors.
    Uses balanced partitioning. Unsigned variant.
    """
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        # set max compressor bandwidth
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        """
        Reduces one column using full adders, half adders and approx. compressors.
        Uses balanced partitioning of bits to approximate between compressors.
        """
        # apply fa_count full adders
        for _ in range(fa_count):
            if self.get_column_height(column_idx) < 3:
                break
            self.add_full_adder(column_idx)

        # apply ha_count half adders
        for _ in range(ha_count):
            if self.get_column_height(column_idx) < 2:
                break
            self.add_half_adder(column_idx)

        current_height = self.get_column_height(column_idx)
        lowest_range_compr_bw = 3
        
        if use_approx:
            j = min(j, current_height)

            # total number of compressors in a column
            compr_count = math.ceil(j / self.max_compressor_bw)

            # each compressor must have at least minimum width
            while compr_count > 0 and compr_count * lowest_range_compr_bw > j:
                compr_count -= 1

            if compr_count > 0:
                compr_base_bw = j // compr_count
                # number of wider compressors
                r = j % compr_count
                compressor_widths = [compr_base_bw + 1] * r + [compr_base_bw] * (compr_count - r)
            else:
                compressor_widths = []

            
            bits_consumed_total = 0
            compressor_out_bits_total = 0

            for current_bw in compressor_widths:
                # prepare current_bw bits for compression
                wires_to_compress = [self.add_column_wire(column=column_idx, bit=i) for i in range(current_bw)]
                compressor_in_bus = Bus(
                    prefix=f"{self.prefix}_compr_in_{column_idx}_{self.get_instance_num(cls=GeneralApproxMtoNCompressor)}",
                    wires_list=wires_to_compress,
                )
                compressor = GeneralApproxMtoNCompressor(
                    a=compressor_in_bus,
                    prefix=f"{self.prefix}_compr_{column_idx}_{self.get_instance_num(cls=GeneralApproxMtoNCompressor)}",
                    inner_component=True,
                )
                self.add_component(compressor)

                # replace the used bits with compressor output bits
                for _ in range(current_bw):
                    self.columns[column_idx].pop(1)
                for i in range(compressor.out.N):
                    self.columns[column_idx].insert(len(self.columns[column_idx]), compressor.out.get_wire(i))

                bits_consumed_total += current_bw
                compressor_out_bits_total += compressor.out.N

            self.update_column_heights(curr_column=column_idx, curr_height_change=-(bits_consumed_total - compressor_out_bits_total))

        else:
            # use dadda-like reduction
            while self.get_column_height(column_idx) > self.h_max_next:
                if self.get_column_height(column_idx) == self.h_max_next + 1:
                    self.add_half_adder(column_idx)
                else:
                    self.add_full_adder(column_idx, prefix_suffix="fa_exact")

class SignedApproxBalancedPredefinedBWCompressorMultiplier(SignedApproxCompressorBasedMultiplier):
    """
    Reduces one column using full adders, half adders and approx. compressors.
    Uses balanced partitioning. Signed variant.
    """
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        # set max compressor bandwidth
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        return UnsignedApproxBalancedPredefinedBWCompressorMultiplier.connect_components(self, column_idx, fa_count, ha_count, j, use_approx)
    

class UnsignedThresholdBalancedPredefinedBWApproxCompressorMultiplier(UnsignedThresholdApproxCompressorMultiplier):
    """
    Combines reduction approach from threshold multiplier and the multiplier
    with the maximum input width of compressors. Unsigned version.
    """
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        # set max compressor bandwidth
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        return UnsignedApproxBalancedPredefinedBWCompressorMultiplier.connect_components(self, column_idx, fa_count, ha_count, j, use_approx)
    

class SignedThresholdBalancedPredefinedBWApproxCompressorMultiplier(SignedThresholdApproxCompressorMultiplier):
    """
    Combines reduction approach from threshold multiplier and the multiplier
    with the maximum input width of compressors. Signed version.
    """
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        # set max compressor bandwidth
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        return UnsignedApproxBalancedPredefinedBWCompressorMultiplier.connect_components(self, column_idx, fa_count, ha_count, j, use_approx)