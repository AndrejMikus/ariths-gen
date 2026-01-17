#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "approx_5_2_cmprs_gen.c"

#define MAX_INPUTS 32

int main() {
    for (uint64_t i = 0; i < MAX_INPUTS; ++i) {

        uint64_t a1 = (i >> 4) & 1;
        uint64_t a2 = (i >> 3) & 1;
        uint64_t a3 = (i >> 2) & 1;
        uint64_t a4 = (i >> 1) & 1;
        uint64_t a5 = (i >> 0) & 1;
        
        uint64_t res = approx_5_2_cmprs(i);

        
        uint64_t sum = a1 ^ a2 ^ a3 ^ a4 ^ a5;
        uint64_t c1 = ((a1 & a2) | (a2 & a3) | (a1 & a3)) ^ (a4 & a5);
        uint64_t c2 = ((a1 & a2) | (a2 & a3) | (a1 & a3)) & (a4 & a5);

        assert(((res >> 0) & 1) == sum);
        assert(((res >> 1) & 1) == c1);
        assert(((res >> 2) & 1) == c2);
    }


    printf("C test for 4 - 2 compressor passed\n");
    return 0;
}