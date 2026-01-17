#include <stdio.h>
#include <stdint.h>

uint64_t approx_5_2_cmprs(uint64_t a){
  uint8_t approx_5_2_cmprs_out = 0;
  uint8_t fa_fa_xor0 = 0;
  uint8_t fa_fa_and0 = 0;
  uint8_t fa_fa_xor1 = 0;
  uint8_t fa_fa_and1 = 0;
  uint8_t fa_fa_or0 = 0;
  uint8_t ha1_ha_xor0 = 0;
  uint8_t ha1_ha_and0 = 0;
  uint8_t ha2_ha_xor0 = 0;
  uint8_t ha2_ha_and0 = 0;
  uint8_t xor_sum = 0;

  fa_fa_xor0 = ((a >> 4) & 0x01) ^ ((a >> 3) & 0x01);
  fa_fa_and0 = ((a >> 4) & 0x01) & ((a >> 3) & 0x01);
  fa_fa_xor1 = ((fa_fa_xor0 >> 0) & 0x01) ^ ((a >> 2) & 0x01);
  fa_fa_and1 = ((fa_fa_xor0 >> 0) & 0x01) & ((a >> 2) & 0x01);
  fa_fa_or0 = ((fa_fa_and0 >> 0) & 0x01) | ((fa_fa_and1 >> 0) & 0x01);
  ha1_ha_xor0 = ((a >> 1) & 0x01) ^ ((a >> 0) & 0x01);
  ha1_ha_and0 = ((a >> 1) & 0x01) & ((a >> 0) & 0x01);
  ha2_ha_xor0 = ((fa_fa_or0 >> 0) & 0x01) ^ ((ha1_ha_and0 >> 0) & 0x01);
  ha2_ha_and0 = ((fa_fa_or0 >> 0) & 0x01) & ((ha1_ha_and0 >> 0) & 0x01);
  xor_sum = ((fa_fa_xor1 >> 0) & 0x01) ^ ((ha1_ha_xor0 >> 0) & 0x01);

  approx_5_2_cmprs_out |= ((xor_sum >> 0) & 0x01ull) << 0;
  approx_5_2_cmprs_out |= ((ha2_ha_xor0 >> 0) & 0x01ull) << 1;
  approx_5_2_cmprs_out |= ((ha2_ha_and0 >> 0) & 0x01ull) << 2;
  return approx_5_2_cmprs_out;
}