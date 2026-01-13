#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "four_two_cmprs_gen.c"

#define MAX_INPUTS 32

int main() {
    for (uint64_t i = 0; i < MAX_INPUTS; ++i) {

        uint64_t a = (i >> 3) & 1;
        uint64_t b = (i >> 2) & 1;
        uint64_t c = (i >> 1) & 1;
        uint64_t d = (i >> 0) & 1;
        uint64_t cin = (i >> 4) & 1;
        
        uint64_t res = cmprss_4_2(i);

        /*
        Sum=x1​⊕x2​⊕x3​⊕x4​⊕Cin
        Cout​=(x1​⊕x2​)⋅x3​+¬(x1​⊕x2​)⋅x1​
        Carry=(x1​⊕x2​⊕x3​⊕x4​)⋅Cin​+¬(x1​⊕x2​⊕x3​⊕x4​)⋅x4
        */

        uint64_t sum = a ^ b ^ c ^ d ^ cin;
        uint64_t cout = ((a ^ b) & c) | (~(a ^ b) & a);
        uint64_t carry = ((a ^ b ^ c ^ d) & cin) | (~(a ^ b ^ c ^ d) & d);

/*         printf("%llu | %llu, %llu, %llu, %llu | %llu, %llu, %llu\n", 
              cin, a, b, c, d, cout, carry, sum); */
        assert(((res >> 0) & 1) == sum);
        assert(((res >> 1) & 1) == carry);
        assert(((res >> 2) & 1) == cout);
    }


    printf("C test for 4 - 2 compressor passed\n");
    return 0;
}
