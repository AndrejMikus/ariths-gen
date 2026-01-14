#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "five_two_cmprs_gen.c"

#define MAX_INPUTS 128

int main() {
    for (uint64_t i = 0; i < MAX_INPUTS; ++i) {

        uint64_t a = (i >> 2) & 1;
        uint64_t b = (i >> 3) & 1;
        uint64_t c = (i >> 4) & 1;
        uint64_t d = (i >> 5) & 1;
        uint64_t e = (i >> 6) & 1;
        uint64_t cin1 = (i >> 1) & 1;
        uint64_t cin2 = (i >> 0) & 1;
        
        uint64_t res = cmprss_5_2(i);

        /* Equations from: https://userpages.cs.umbc.edu/phatak/645/supl/5:2compressor.pdf
        */


        uint64_t s1 = a ^ b ^ c;
        uint64_t cout1 = ((a ^ b) & c) | ((~(a ^ b)) & a);

        uint64_t s2 = s1 ^ d ^ cin1;
        uint64_t cout2 = ((d ^ s1) & cin1) + ((~(d ^ s1)) & d);

        uint64_t sum = s2 ^ e ^ cin2;
        uint64_t carry = ((e ^ s2) & cin2) | ((~(e ^ s2)) & e);

            
        assert(sum   == ((res >> 0) & 1));
        assert(carry == ((res >> 1) & 1));
        assert(cout1 == ((res >> 2) & 1));
        assert(cout2 == ((res >> 3) & 1));

        assert(a + b + c + d + e + cin1 + cin2 == sum + 2 * (carry + cout1 + cout2));

    }

    printf("C test for 5 - 2 compressor passed\n");
    return 0;
}