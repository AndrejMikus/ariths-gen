#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "u_rca_gen.c"

int main() {
    const int N = 4;
    const int MAX = 1 << N; // 2^N possible outputs

    for (int a = 0; a < MAX; a++) {
        for (int b = 0; b < MAX; b++) {
            uint64_t res = u_rca(a,b);
            uint64_t expected = a + b;

            if (res != expected) {
                printf("ERROR: %d + %d = %lu (expected %lu)\n", a, b, res, expected);
            }
            assert(res == expected);
        }
    }

    printf("C unsinged RCA tests passed\n");
    return 0;
}