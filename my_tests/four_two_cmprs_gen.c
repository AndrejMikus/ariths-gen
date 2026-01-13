#include <stdio.h>
#include <stdint.h>

uint64_t cmprss_4_2(uint64_t a){
  uint8_t cmprss_4_2_out = 0;
  uint8_t _fa1_fa_xor0 = 0;
  uint8_t _fa1_fa_and0 = 0;
  uint8_t _fa1_fa_xor1 = 0;
  uint8_t _fa1_fa_and1 = 0;
  uint8_t _fa1_fa_or0 = 0;
  uint8_t fa_xor0 = 0;
  uint8_t fa_and0 = 0;
  uint8_t fa_xor1 = 0;
  uint8_t fa_and1 = 0;
  uint8_t fa_or0 = 0;

  _fa1_fa_xor0 = ((a >> 3) & 0x01) ^ ((a >> 2) & 0x01);
  _fa1_fa_and0 = ((a >> 3) & 0x01) & ((a >> 2) & 0x01);
  _fa1_fa_xor1 = ((_fa1_fa_xor0 >> 0) & 0x01) ^ ((a >> 1) & 0x01);
  _fa1_fa_and1 = ((_fa1_fa_xor0 >> 0) & 0x01) & ((a >> 1) & 0x01);
  _fa1_fa_or0 = ((_fa1_fa_and0 >> 0) & 0x01) | ((_fa1_fa_and1 >> 0) & 0x01);
  fa_xor0 = ((_fa1_fa_xor1 >> 0) & 0x01) ^ ((a >> 0) & 0x01);
  fa_and0 = ((_fa1_fa_xor1 >> 0) & 0x01) & ((a >> 0) & 0x01);
  fa_xor1 = ((fa_xor0 >> 0) & 0x01) ^ ((a >> 4) & 0x01);
  fa_and1 = ((fa_xor0 >> 0) & 0x01) & ((a >> 4) & 0x01);
  fa_or0 = ((fa_and0 >> 0) & 0x01) | ((fa_and1 >> 0) & 0x01);

  cmprss_4_2_out |= ((fa_xor1 >> 0) & 0x01ull) << 0;
  cmprss_4_2_out |= ((fa_or0 >> 0) & 0x01ull) << 1;
  cmprss_4_2_out |= ((_fa1_fa_or0 >> 0) & 0x01ull) << 2;
  return cmprss_4_2_out;
}