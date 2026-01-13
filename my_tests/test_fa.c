#include <stdio.h>
#include <stdint.h>
#include <assert.h>

#include "fa_gen.c"

int main(void) {
    for (int a = 0; a < 2; a++) {
        for (int b = 0; b < 2; b++) {
            for (int c = 0; c < 2; c++) {
                uint8_t res = fa_(a, b, c);

                int sum = c ^ (a ^ b);
                int carry = (a & b) | (b & c)| (a & c);

                assert(((res >> 0) & 1) == sum);
                assert(((res >> 1) & 1) == carry);
            }
        }
    }

    printf("C full adder test passed\n");
    return 0;
}