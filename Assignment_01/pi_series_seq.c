#include <math.h>

double pi_series(long num_terms, long num_threads)
{
	double sum = 0.0;

	for (unsigned long n = 0; n < num_terms; n++)
	{
		sum += powf((-1.0f),n) / ((double)(2 * n + 1));
	}

	return (4 * sum);
}

