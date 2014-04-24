#include <math.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>


void * pi_sum(void *ptr)	{
	double *sum = malloc(sizeof(*sum));
	*sum = powf((-1.0f),(*(int*)ptr)) / ((double)(2 * (*(int*)ptr) + 1));

	return sum;
}

double pi_series(long num_terms, long num_threads)
{
	int i;
	pthread_t *thread;
	thread = malloc(num_threads * sizeof (*thread));
	int *in = malloc(num_threads * sizeof (*in));

	double pi_val = 0.0;

    for (i = 0; i < num_threads; i++)
    {
    	in[i] = i;
        pthread_create(thread + i, 0, &pi_sum, in + i);
    }

    for (i = 0; i < num_threads; i++)
    {
    	double *sum;
        pthread_join(thread[i], &sum);
        pi_val += *sum;
        printf("Sum of terms is %f, pi is %f \n", *sum, pi_val);
        free(sum);
    }

    pi_val = 4 * pi_val;
    printf("pi is %f \n", pi_val);
    free(thread);

    return pi_val;
}

int main() {
    long num_threads = 10;
    long num_terms = 10;
    double pi;

    pi = pi_series(num_terms, num_threads);

    return 0;
}
