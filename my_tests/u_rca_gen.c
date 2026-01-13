#include <stdio.h>
#include <stdint.h>

uint64_t u_rca(uint64_t a,uint64_t b){
  uint8_t u_rca_out = 0;
  uint8_t u_rca_ha_ha_xor0 = 0;
  uint8_t u_rca_ha_ha_and0 = 0;
  uint8_t u_rca_fa1_fa_xor0 = 0;
  uint8_t u_rca_fa1_fa_and0 = 0;
  uint8_t u_rca_fa1_fa_xor1 = 0;
  uint8_t u_rca_fa1_fa_and1 = 0;
  uint8_t u_rca_fa1_fa_or0 = 0;
  uint8_t u_rca_fa2_fa_xor0 = 0;
  uint8_t u_rca_fa2_fa_and0 = 0;
  uint8_t u_rca_fa2_fa_xor1 = 0;
  uint8_t u_rca_fa2_fa_and1 = 0;
  uint8_t u_rca_fa2_fa_or0 = 0;
  uint8_t u_rca_fa3_fa_xor0 = 0;
  uint8_t u_rca_fa3_fa_and0 = 0;
  uint8_t u_rca_fa3_fa_xor1 = 0;
  uint8_t u_rca_fa3_fa_and1 = 0;
  uint8_t u_rca_fa3_fa_or0 = 0;

  u_rca_ha_ha_xor0 = ((a >> 0) & 0x01) ^ ((b >> 0) & 0x01);
  u_rca_ha_ha_and0 = ((a >> 0) & 0x01) & ((b >> 0) & 0x01);
  u_rca_fa1_fa_xor0 = ((a >> 1) & 0x01) ^ ((b >> 1) & 0x01);
  u_rca_fa1_fa_and0 = ((a >> 1) & 0x01) & ((b >> 1) & 0x01);
  u_rca_fa1_fa_xor1 = ((u_rca_fa1_fa_xor0 >> 0) & 0x01) ^ ((u_rca_ha_ha_and0 >> 0) & 0x01);
  u_rca_fa1_fa_and1 = ((u_rca_fa1_fa_xor0 >> 0) & 0x01) & ((u_rca_ha_ha_and0 >> 0) & 0x01);
  u_rca_fa1_fa_or0 = ((u_rca_fa1_fa_and0 >> 0) & 0x01) | ((u_rca_fa1_fa_and1 >> 0) & 0x01);
  u_rca_fa2_fa_xor0 = ((a >> 2) & 0x01) ^ ((b >> 2) & 0x01);
  u_rca_fa2_fa_and0 = ((a >> 2) & 0x01) & ((b >> 2) & 0x01);
  u_rca_fa2_fa_xor1 = ((u_rca_fa2_fa_xor0 >> 0) & 0x01) ^ ((u_rca_fa1_fa_or0 >> 0) & 0x01);
  u_rca_fa2_fa_and1 = ((u_rca_fa2_fa_xor0 >> 0) & 0x01) & ((u_rca_fa1_fa_or0 >> 0) & 0x01);
  u_rca_fa2_fa_or0 = ((u_rca_fa2_fa_and0 >> 0) & 0x01) | ((u_rca_fa2_fa_and1 >> 0) & 0x01);
  u_rca_fa3_fa_xor0 = ((a >> 3) & 0x01) ^ ((b >> 3) & 0x01);
  u_rca_fa3_fa_and0 = ((a >> 3) & 0x01) & ((b >> 3) & 0x01);
  u_rca_fa3_fa_xor1 = ((u_rca_fa3_fa_xor0 >> 0) & 0x01) ^ ((u_rca_fa2_fa_or0 >> 0) & 0x01);
  u_rca_fa3_fa_and1 = ((u_rca_fa3_fa_xor0 >> 0) & 0x01) & ((u_rca_fa2_fa_or0 >> 0) & 0x01);
  u_rca_fa3_fa_or0 = ((u_rca_fa3_fa_and0 >> 0) & 0x01) | ((u_rca_fa3_fa_and1 >> 0) & 0x01);

  u_rca_out |= ((u_rca_ha_ha_xor0 >> 0) & 0x01ull) << 0;
  u_rca_out |= ((u_rca_fa1_fa_xor1 >> 0) & 0x01ull) << 1;
  u_rca_out |= ((u_rca_fa2_fa_xor1 >> 0) & 0x01ull) << 2;
  u_rca_out |= ((u_rca_fa3_fa_xor1 >> 0) & 0x01ull) << 3;
  u_rca_out |= ((u_rca_fa3_fa_or0 >> 0) & 0x01ull) << 4;
  return u_rca_out;
}