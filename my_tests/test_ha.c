#include <stdio.h>
#include <stdint.h>
#include <assert.h>

#include "ha_gen.c"

int main(void) {
    for (int a = 0; a < 2; a++) {
        for (int b = 0; b < 2; b++) {
            uint8_t res = ha_(a, b);

            int sum = a ^ b;
            int carry = a & b;

            assert(((res >> 0) & 1) == sum);
            assert(((res >> 1) & 1) == carry);
        }
    }

    printf("C half adder test passed\n");
    return 0;
}