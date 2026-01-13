#include <stdio.h>
#include <stdint.h>

uint8_t ha_(uint8_t a,uint8_t b){
  uint8_t ha__out = 0;
  uint8_t ha__xor = 0;
  uint8_t ha__and = 0;

  ha__xor = ((a >> 0) & 0x01) ^ ((b >> 0) & 0x01);
  ha__and = ((a >> 0) & 0x01) & ((b >> 0) & 0x01);

  ha__out |= ((ha__xor >> 0) & 0x01ull) << 0;
  ha__out |= ((ha__and >> 0) & 0x01ull) << 1;
  return ha__out;
}