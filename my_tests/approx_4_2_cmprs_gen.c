#include <stdio.h>
#include <stdint.h>

uint64_t approx_4_2_cmprs(uint64_t a){
  uint8_t approx_4_2_cmprs_out = 0;
  uint8_t upper_or = 0;
  uint8_t lower_or = 0;
  uint8_t carry_and = 0;
  uint8_t sum_not = 0;

  upper_or = ((a >> 0) & 0x01) | ((a >> 1) & 0x01);
  lower_or = ((a >> 2) & 0x01) | ((a >> 3) & 0x01);
  carry_and = ((upper_or >> 0) & 0x01) & ((lower_or >> 0) & 0x01);
  sum_not = ~(((carry_and >> 0) & 0x01)) & 0x01;

  approx_4_2_cmprs_out |= ((sum_not >> 0) & 0x01ull) << 0;
  approx_4_2_cmprs_out |= ((carry_and >> 0) & 0x01ull) << 1;
  return approx_4_2_cmprs_out;
}