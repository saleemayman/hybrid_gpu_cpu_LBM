#include <math.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

struct pthread_args
{
	double in, out;
};

void * pi_sum(void *ptr)	{
	struct pthread_args *arg = ptr ;
	arg->out = powf((-1.0f),arg->in) / ((double)(2 * arg->in + 1));

	return NULL;
}

double pi_series(long num_terms, long num_threads)
{
	long int i, j;
	pthread_t *thread;
	thread = malloc(num_threads * sizeof (*thread));
	struct pthread_args *thread_arg;
	thread_arg = malloc(num_threads * sizeof (*thread_arg));

	double pi_val = 0.0;

	long int iter = num_terms/num_threads;
	long int rem = num_terms % num_threads;

	/* threads for most of the terms*/
	for (j = 0; j < iter; j++) {
		for (i = 0; i < num_threads; i++)
		{
			thread_arg[i].in = i + j * num_threads;
			pthread_create(&thread[i], 0, &pi_sum, &thread_arg[i]);
		}

		for (i = 0; i < num_threads; i++)
		{
			pthread_join(thread[i], NULL);
			pi_val += thread_arg[i].out;
		}
	}

	/* threads for the remaining terms*/
	for (i = 0; i < rem; i++)
	{
		thread_arg[i].in = i + j * num_threads;
		pthread_create(&thread[i], 0, &pi_sum, &thread_arg[i]);
	}

	for (i = 0; i < rem; i++)
	{
		pthread_join(thread[i], NULL);
		pi_val += thread_arg[i].out;
	}

    free(thread);
    free(thread_arg);

    return 4 * pi_val;
}



