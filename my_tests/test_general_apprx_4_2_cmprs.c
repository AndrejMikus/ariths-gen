#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "general_approx_4_2_cmprs_gen.c"

#define MAX_INPUTS 16

int main() {
    for (uint64_t i = 0; i < MAX_INPUTS; ++i) {

        uint64_t a = (i >> 3) & 1;
        uint64_t b = (i >> 2) & 1;
        uint64_t c = (i >> 1) & 1;
        uint64_t d = (i >> 0) & 1;
        
        uint64_t res = approx_M_N_cmprs(i);

        printf("%llu\t%llu\n", (res >> 0) & 1, (res >> 1) & 1);

    }


    printf("\nC test for 4 - 2 compressor passed\n");
    return 0;
}