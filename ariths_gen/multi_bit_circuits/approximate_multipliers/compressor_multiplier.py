from ariths_gen.wire_components import Bus, ConstantWireValue0, ConstantWireValue1
from ariths_gen.core.arithmetic_circuits import MultiplierCircuit
from ariths_gen.one_bit_circuits.one_bit_components import HalfAdder, FullAdder
from ariths_gen.multi_bit_circuits.approximative_compressors import GeneralApproxMtoNCompressor
from ariths_gen.multi_bit_circuits.adders.carry_lookahead_adder import UnsignedCarryLookaheadAdder
from ariths_gen.one_bit_circuits.logic_gates import AndGate, NandGate, XorGate
import math


def _variant_configuration(variant: str):
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

        self.N = max(a.N, b.N)
        self.variant = variant
        self.use_truncation = False
        self.use_dadda = False
        self.approx_stages = None
        self.h_max_next = (self.N + 1) // 2

        super().__init__(inputs=[a, b], prefix=prefix, name=name, signed=signed, out_N=self.N * 2, **kwargs)

        self._extend_buses(a, b)
        self.columns = self.init_column_heights()
        self._prepare_columns()

        self.use_truncation, self.approx_stages = _variant_configuration(self.variant)

        if self.use_truncation:
            for col_idx in range(self.N - 1):
                self.columns[col_idx] = [0]

        self._reduce_columns()
        self._finalize_output(unsigned_adder_class_name, kwargs)
        self._post_finalize()

    def _extend_buses(self, a: Bus, b: Bus):
        self.a.bus_extend(N=self.N, prefix=a.prefix)
        self.b.bus_extend(N=self.N, prefix=b.prefix)

    def _prepare_columns(self):
        self._prepare_extra_columns()

        # Rearrange partial products so every gate appears only once in the matrix.
        for col_idx in range(len(self.columns)):
            new_column = [self.get_column_height(col_idx)]

            for obj in self.columns[col_idx][1:]:
                if isinstance(obj, self.partial_product_gate_types):
                    if obj.prefix not in self._prefixes:
                        self.add_component(obj)
                    new_column.append(obj.out)
                else:
                    new_column.append(obj)

            self.columns[col_idx] = new_column

    def _prepare_extra_columns(self):
        pass

    def _post_finalize(self):
        pass

    def _low_part_limit(self, num_columns: int):
        return self.N

    def _reduce_columns(self):
        stage = 0

        while not all(self.get_column_height(c) <= 2 for c in range(len(self.columns))):
            stage += 1
            current_max = max(self.get_column_height(c) for c in range(len(self.columns)))

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

    def _finalize_output(self, unsigned_adder_class_name, kwargs):
        if self.N > 1:
            adder_a_wires = []
            adder_b_wires = []

            for col in range(1, len(self.columns)):
                h = self.get_column_height(col)
                adder_a_wires.append(self.add_column_wire(column=col, bit=0) if h > 0 else ConstantWireValue0())
                adder_b_wires.append(self.add_column_wire(column=col, bit=1) if h > 1 else ConstantWireValue0())

            adder_a = Bus(prefix=f"{self.prefix}_final_a", wires_list=adder_a_wires)
            adder_b = Bus(prefix=f"{self.prefix}_final_b", wires_list=adder_b_wires)

            final_adder = unsigned_adder_class_name(
                a=adder_a,
                b=adder_b,
                prefix=self.prefix,
                name="final_adder",
                inner_component=True,
                **kwargs,
            )
            self.add_component(final_adder)

            for i in range(final_adder.out.N):
                if (i + 1) < self.out.N:
                    self.out.connect(i + 1, final_adder.out.get_wire(i))
        else:
            self.out.connect(1, ConstantWireValue0())

        if self.get_column_height(0) > 0:
            self.out.connect(0, self.add_column_wire(column=0, bit=0))

        if self.use_truncation:
            for i in range(self.N - 1):
                self.out.connect(i, ConstantWireValue0())

    def _add_full_adder(self, column_idx: int, prefix_suffix: str = "fa"):
        fa = FullAdder(
            self.add_column_wire(column=column_idx, bit=0),
            self.add_column_wire(column=column_idx, bit=1),
            self.add_column_wire(column=column_idx, bit=2),
            prefix=f"{self.prefix}_{prefix_suffix}_{column_idx}_{self.get_instance_num(cls=FullAdder)}",
        )
        self.add_component(fa)
        next_col = min(column_idx + 1, len(self.columns) - 1)
        self.update_column_heights(curr_column=column_idx, curr_height_change=-2, next_column=next_col, next_height_change=1)
        self.update_column_wires(curr_column=column_idx, next_column=next_col, adder=fa)

    def _add_half_adder(self, column_idx: int):
        ha = HalfAdder(
            self.add_column_wire(column=column_idx, bit=0),
            self.add_column_wire(column=column_idx, bit=1),
            prefix=f"{self.prefix}_ha_{column_idx}_{self.get_instance_num(cls=HalfAdder)}",
        )
        self.add_component(ha)
        next_col = min(column_idx + 1, len(self.columns) - 1)
        self.update_column_heights(curr_column=column_idx, curr_height_change=-1, next_column=next_col, next_height_change=1)
        self.update_column_wires(curr_column=column_idx, next_column=next_col, adder=ha)

    def allocate_compressors(self):
        num_columns = len(self.columns)
        fa = [0] * num_columns
        ha = [0] * num_columns
        j = [0] * num_columns
        C = [0] * num_columns
        h_next = [0] * num_columns

        h = [self.get_column_height(col) for col in range(num_columns)]

        low_part_limit = self._low_part_limit(num_columns)

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
        for _ in range(fa_count):
            if self.get_column_height(column_idx) < 3:
                break
            self._add_full_adder(column_idx)

        for _ in range(ha_count):
            if self.get_column_height(column_idx) < 2:
                break
            self._add_half_adder(column_idx)

        current_height = self.get_column_height(column_idx)

        if use_approx:
            j = min(j, current_height)

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

            for _ in range(j):
                self.columns[column_idx].pop(1)
            for i in range(compressor.out.N):
                self.columns[column_idx].insert(len(self.columns[column_idx]), compressor.out.get_wire(i))
        else:
            # reduction using dadda rules
            while self.get_column_height(column_idx) > self.h_max_next:
                if self.get_column_height(column_idx) == self.h_max_next + 1:
                    self._add_half_adder(column_idx)
                else:
                    self._add_full_adder(column_idx, prefix_suffix="fa_exact")


class UnsignedApproxCompressorBasedMultiplier(_ApproxCompressorBasedMultiplierBase):
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

    def _extend_buses(self, a: Bus, b: Bus):
        self.a.bus_extend(N=self.N, prefix=a.prefix, desired_extension_wire=self.a.get_wire(self.a.N - 1))
        self.b.bus_extend(N=self.N, prefix=b.prefix, desired_extension_wire=self.b.get_wire(self.b.N - 1))

    def _prepare_extra_columns(self):
        if self.N != 1:
            self.columns[self.N].insert(1, ConstantWireValue1())
            self.update_column_heights(curr_column=self.N, curr_height_change=1)

    def _post_finalize(self):
        obj_xor = XorGate(
            ConstantWireValue1(),
            self.out.get_wire(self.out.N - 1),
            prefix=self.prefix + "_xor" + str(self.get_instance_num(cls=XorGate)),
            parent_component=self,
        )
        self.add_component(obj_xor)
        self.out.connect(self.out.N - 1, obj_xor.out)


class UnsignedQuarterApproxCompressorMultiplier(UnsignedApproxCompressorBasedMultiplier):
    def _low_part_limit(self, num_columns: int):
        return num_columns // 4

class SignedQuarterApproxCompressorMultiplier(SignedApproxCompressorBasedMultiplier):
    def _low_part_limit(self, num_columns: int):
        return num_columns // 4

class UnsignedThresholdApproxCompressorMultiplier(UnsignedApproxCompressorBasedMultiplier):
    def __init__(self, *args, height_threshold=0.5, **kwargs):
        assert(0 <= height_threshold <= 1)
        self.height_threshold = height_threshold
        super().__init__(*args, **kwargs)

    def allocate_compressors(self):
        num_columns = len(self.columns)
        fa = [0] * num_columns
        ha = [0] * num_columns
        j = [0] * num_columns
        C = [0] * num_columns
        h_next = [0] * num_columns

        h = [self.get_column_height(col) for col in range(num_columns)]
        

        threshold_height = 3 + self.height_threshold * (self.N - 2)

        low_part_limit = self._low_part_limit(num_columns)

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
    def __init__(self, *args, height_threshold=0.5, **kwargs):
        assert(0 <= height_threshold <= 1)
        self.height_threshold = height_threshold
        super().__init__(*args, **kwargs)

    def allocate_compressors(self):
        return UnsignedThresholdApproxCompressorMultiplier.allocate_compressors(self)

    
class UnsignedApproxPredefinedCompressorBWMultiplier(UnsignedApproxCompressorBasedMultiplier):
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        # set max compressor bandwidth
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)


    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        for _ in range(fa_count):
            if self.get_column_height(column_idx) < 3:
                break
            self._add_full_adder(column_idx)

        for _ in range(ha_count):
            if self.get_column_height(column_idx) < 2:
                break
            self._add_half_adder(column_idx)

        current_height = self.get_column_height(column_idx)
        lowest_range_compr_bw = 3

        if use_approx:
            j = min(j, current_height)

            compressor_out_bits_total = 0
            bits_consumed_total = 0

            while j >= lowest_range_compr_bw:
                current_bw = min(j, self.max_compressor_bw)
                
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
                    self._add_half_adder(column_idx)
                else:
                    self._add_full_adder(column_idx, prefix_suffix="fa_exact")

class SignedApproxPredefinedCompressorBWMultiplier(SignedApproxCompressorBasedMultiplier):
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        # set max compressor bandwidth
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        return UnsignedApproxPredefinedCompressorBWMultiplier.connect_components(self, column_idx, fa_count, ha_count, j, use_approx)


class UnsignedThresholdPredefinedBWApproxCompressorMultiplier(UnsignedThresholdApproxCompressorMultiplier):
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        return UnsignedApproxPredefinedCompressorBWMultiplier.connect_components(self, column_idx, fa_count, ha_count, j, use_approx)
    
class SignedThresholdPredefinedBWApproxCompressorMultiplier(SignedThresholdApproxCompressorMultiplier):
    def __init__(self, *args, max_compressor_bw=3, **kwargs):
        assert(max_compressor_bw >= 3)
        self.max_compressor_bw = max_compressor_bw
        super().__init__(*args, **kwargs)

    def connect_components(self, column_idx, fa_count, ha_count, j, use_approx):
        return UnsignedApproxPredefinedCompressorBWMultiplier.connect_components(self, column_idx, fa_count, ha_count, j, use_approx)
