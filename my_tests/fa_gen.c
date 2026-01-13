#include <stdio.h>
#include <stdint.h>

uint8_t fa_(uint8_t a, uint8_t b, uint8_t c){
  uint8_t fa__out = 0;
  uint8_t fa__xor1 = 0;
  uint8_t fa__and1 = 0;
  uint8_t fa__xor2 = 0;
  uint8_t fa__and2 = 0;
  uint8_t fa__or = 0;

  fa__xor1 = ((a >> 0) & 0x01) ^ ((b >> 0) & 0x01);
  fa__and1 = ((a >> 0) & 0x01) & ((b >> 0) & 0x01);
  fa__xor2 = ((fa__xor1 >> 0) & 0x01) ^ ((c >> 0) & 0x01);
  fa__and2 = ((c >> 0) & 0x01) & ((fa__xor1 >> 0) & 0x01);
  fa__or = ((fa__and1 >> 0) & 0x01) | ((fa__and2 >> 0) & 0x01);

  fa__out |= ((fa__xor2 >> 0) & 0x01ull) << 0;
  fa__out |= ((fa__or >> 0) & 0x01ull) << 1;
  return fa__out;
}