#include <stdio.h>
#include <stdint.h>

uint64_t approx_M_N_cmprs(uint64_t a){
  uint8_t approx_M_N_cmprs_out = 0;
  uint8_t and_0 = 0;
  uint8_t or_0 = 0;
  uint8_t and_1 = 0;
  uint8_t or_1 = 0;
  uint8_t out_0 = 0;
  uint8_t out_1 = 0;

  and_0 = ((a >> 0) & 0x01) & ((a >> 1) & 0x01);
  or_0 = ((a >> 0) & 0x01) | ((a >> 1) & 0x01);
  and_1 = ((a >> 2) & 0x01) & ((a >> 3) & 0x01);
  or_1 = ((a >> 2) & 0x01) | ((a >> 3) & 0x01);
  out_0 = ((and_0 >> 0) & 0x01) | ((or_1 >> 0) & 0x01);
  out_1 = ((and_1 >> 0) & 0x01) | ((or_0 >> 0) & 0x01);

  approx_M_N_cmprs_out |= ((out_0 >> 0) & 0x01ull) << 0;
  approx_M_N_cmprs_out |= ((out_1 >> 0) & 0x01ull) << 1;
  return approx_M_N_cmprs_out;
}