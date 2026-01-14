#include <stdio.h>
#include <stdint.h>

uint64_t cmprss_5_2(uint64_t a){
  uint8_t cmprss_5_2_out = 0;
  uint8_t fa1_fa_xor0 = 0;
  uint8_t fa1_fa_and0 = 0;
  uint8_t fa1_fa_xor1 = 0;
  uint8_t fa1_fa_and1 = 0;
  uint8_t fa1_fa_or0 = 0;
  uint8_t fa2_fa_xor0 = 0;
  uint8_t fa2_fa_and0 = 0;
  uint8_t fa2_fa_xor1 = 0;
  uint8_t fa2_fa_and1 = 0;
  uint8_t fa2_fa_or0 = 0;
  uint8_t fa3_fa_xor0 = 0;
  uint8_t fa3_fa_and0 = 0;
  uint8_t fa3_fa_xor1 = 0;
  uint8_t fa3_fa_and1 = 0;
  uint8_t fa3_fa_or0 = 0;

  fa1_fa_xor0 = ((a >> 4) & 0x01) ^ ((a >> 3) & 0x01);
  fa1_fa_and0 = ((a >> 4) & 0x01) & ((a >> 3) & 0x01);
  fa1_fa_xor1 = ((fa1_fa_xor0 >> 0) & 0x01) ^ ((a >> 2) & 0x01);
  fa1_fa_and1 = ((fa1_fa_xor0 >> 0) & 0x01) & ((a >> 2) & 0x01);
  fa1_fa_or0 = ((fa1_fa_and0 >> 0) & 0x01) | ((fa1_fa_and1 >> 0) & 0x01);
  fa2_fa_xor0 = ((a >> 5) & 0x01) ^ ((fa1_fa_xor1 >> 0) & 0x01);
  fa2_fa_and0 = ((a >> 5) & 0x01) & ((fa1_fa_xor1 >> 0) & 0x01);
  fa2_fa_xor1 = ((fa2_fa_xor0 >> 0) & 0x01) ^ ((a >> 1) & 0x01);
  fa2_fa_and1 = ((fa2_fa_xor0 >> 0) & 0x01) & ((a >> 1) & 0x01);
  fa2_fa_or0 = ((fa2_fa_and0 >> 0) & 0x01) | ((fa2_fa_and1 >> 0) & 0x01);
  fa3_fa_xor0 = ((a >> 6) & 0x01) ^ ((fa2_fa_xor1 >> 0) & 0x01);
  fa3_fa_and0 = ((a >> 6) & 0x01) & ((fa2_fa_xor1 >> 0) & 0x01);
  fa3_fa_xor1 = ((fa3_fa_xor0 >> 0) & 0x01) ^ ((a >> 0) & 0x01);
  fa3_fa_and1 = ((fa3_fa_xor0 >> 0) & 0x01) & ((a >> 0) & 0x01);
  fa3_fa_or0 = ((fa3_fa_and0 >> 0) & 0x01) | ((fa3_fa_and1 >> 0) & 0x01);

  cmprss_5_2_out |= ((fa3_fa_xor1 >> 0) & 0x01ull) << 0;
  cmprss_5_2_out |= ((fa3_fa_or0 >> 0) & 0x01ull) << 1;
  cmprss_5_2_out |= ((fa1_fa_or0 >> 0) & 0x01ull) << 2;
  cmprss_5_2_out |= ((fa2_fa_or0 >> 0) & 0x01ull) << 3;
  return cmprss_5_2_out;
}