#include <stdio.h>

#include "u_compr_mult_gen.c"

#define A (12)
#define B (14)

int main() {
    uint64_t a = A;
    uint64_t b = B;
    uint64_t result = u_apprx_cmpr(a, b);

    printf("%lu * %lu ~= %lu\n", a, b, result);
}