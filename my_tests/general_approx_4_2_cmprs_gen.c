#include <stdio.h>
#include <stdint.h>

uint8_t and_gate(uint8_t a, uint8_t b){
  return ((a >> 0) & 0x01) & ((b >> 0) & 0x01);
}

uint8_t or_gate(uint8_t a, uint8_t b){
  return ((a >> 0) & 0x01) | ((b >> 0) & 0x01);
}

uint64_t approx_cmprs_4_2(uint64_t a){
  uint8_t approx_cmprs_4_2_out = 0;
  uint8_t approx_cmprs_4_2_and_0 = 0;
  uint8_t approx_cmprs_4_2_or_0 = 0;
  uint8_t approx_cmprs_4_2_and_1 = 0;
  uint8_t approx_cmprs_4_2_or_1 = 0;
  uint8_t approx_cmprs_4_2_out_0 = 0;
  uint8_t approx_cmprs_4_2_out_1 = 0;

  approx_cmprs_4_2_and_0 = and_gate(((a >> 0) & 0x01), ((a >> 1) & 0x01));
  approx_cmprs_4_2_or_0 = or_gate(((a >> 0) & 0x01), ((a >> 1) & 0x01));
  approx_cmprs_4_2_and_1 = and_gate(((a >> 2) & 0x01), ((a >> 3) & 0x01));
  approx_cmprs_4_2_or_1 = or_gate(((a >> 2) & 0x01), ((a >> 3) & 0x01));
  approx_cmprs_4_2_out_0 = or_gate(((approx_cmprs_4_2_and_0 >> 0) & 0x01), ((approx_cmprs_4_2_or_1 >> 0) & 0x01));
  approx_cmprs_4_2_out_1 = or_gate(((approx_cmprs_4_2_and_1 >> 0) & 0x01), ((approx_cmprs_4_2_or_0 >> 0) & 0x01));

  approx_cmprs_4_2_out |= ((approx_cmprs_4_2_out_0 >> 0) & 0x01ull) << 0;
  approx_cmprs_4_2_out |= ((approx_cmprs_4_2_out_1 >> 0) & 0x01ull) << 1;
  return approx_cmprs_4_2_out;
}

uint64_t general_approx_cmprs_8_4(uint64_t a){
  uint8_t general_approx_cmprs_8_4_out = 0;
  uint64_t general_approx_cmprs_8_4_grp0 = 0;
  uint64_t general_approx_cmprs_8_4_0_approx_cmprs_4_2_out = 0;
  uint64_t general_approx_cmprs_8_4_grp1_4 = 0;
  uint64_t general_approx_cmprs_8_4_1_approx_cmprs_4_2_out = 0;

  general_approx_cmprs_8_4_grp0 |= ((a >> 0) & 0x01ull) << 0;
  general_approx_cmprs_8_4_grp0 |= ((a >> 1) & 0x01ull) << 1;
  general_approx_cmprs_8_4_grp0 |= ((a >> 2) & 0x01ull) << 2;
  general_approx_cmprs_8_4_grp0 |= ((a >> 3) & 0x01ull) << 3;
  general_approx_cmprs_8_4_0_approx_cmprs_4_2_out = approx_cmprs4(general_approx_cmprs_8_4_grp0);
  general_approx_cmprs_8_4_grp1_4 |= ((a >> 4) & 0x01ull) << 0;
  general_approx_cmprs_8_4_grp1_4 |= ((a >> 5) & 0x01ull) << 1;
  general_approx_cmprs_8_4_grp1_4 |= ((a >> 6) & 0x01ull) << 2;
  general_approx_cmprs_8_4_grp1_4 |= ((a >> 7) & 0x01ull) << 3;
  general_approx_cmprs_8_4_1_approx_cmprs_4_2_out = approx_cmprs4(general_approx_cmprs_8_4_grp1_4);

  general_approx_cmprs_8_4_out |= ((general_approx_cmprs_8_4_0_approx_cmprs_4_2_out >> 0) & 0x01ull) << 0;
  general_approx_cmprs_8_4_out |= ((general_approx_cmprs_8_4_0_approx_cmprs_4_2_out >> 1) & 0x01ull) << 1;
  general_approx_cmprs_8_4_out |= ((general_approx_cmprs_8_4_1_approx_cmprs_4_2_out >> 0) & 0x01ull) << 2;
  general_approx_cmprs_8_4_out |= ((general_approx_cmprs_8_4_1_approx_cmprs_4_2_out >> 1) & 0x01ull) << 3;
  return general_approx_cmprs_8_4_out;
}