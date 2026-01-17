#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "approx_4_2_cmprs_gen.c"

#define MAX_INPUTS 16

int main() {
    for (uint64_t i = 0; i < MAX_INPUTS; ++i) {

        uint64_t a = (i >> 3) & 1;
        uint64_t b = (i >> 2) & 1;
        uint64_t c = (i >> 1) & 1;
        uint64_t d = (i >> 0) & 1;
        
        uint64_t res = approx_4_2_cmprs(i);

        uint64_t carry = ((a | b) & (c | d) & 1);
        uint64_t sum = (~carry) & 1;


        assert(((res >> 0) & 1) == sum);
        assert(((res >> 1) & 1) == carry);

    }


    printf("C test for 4 - 2 compressor passed\n");
    return 0;
}