if __name__ == "__main__":    
    import os, sys
    sys.path.append(os.getcwd())
    # print(os.getcwd(), sys.path)

   

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from math import trunc, exp, log

import random

def uniform_int(minval, maxval):
    "Create a function that draws ints uniformly from {minval, ..., maxval}"
    def _draw():
        return random.randint(minval, maxval)
    return _draw

def uniform(minval, maxval):
    "Create a function that draws floats uniformly from [minval, maxval]"
    def _draw():
        return random.uniform(minval, maxval)
    return _draw

def log_uniform(minval, maxval):
    "Create a function that draws floats log-uniformly from [minval, maxval]"
    def _draw():
        return exp(random.uniform(log(minval), log(maxval))) 
    return _draw

def log_uniform_int(minval, maxval):
    "Create a function that draws ints log-uniformly from {minval, ..., maxval}"
    draw_float = log_uniform(minval, maxval + 1)
    def _draw():
        val = int(draw_float())
        val = max(minval, val)
        val = min(maxval, val)
        return val
    return _draw

def bimodal(minval, maxval, p):
    def _draw():
        toss = random.choice((1, 2))
        mid = (maxval-minval)/2        
        if toss == 1:            
            return random.triangular(minval, mid, p)
        else :
            return random.triangular(mid, maxval, 1-p)
    return _draw

def uniform_choice(choices):
    "Create a function that draws uniformly elements from choices"
    selector = uniform_int(0, len(choices) - 1)
    # s = selector()
    # print("uniform choice = ", s, choices[s].__repr__)
    # print(choices[selector()] )
    # def _draw():
    #     return choices[selector()]
    # print (_draw)
    return choices[selector()]
    # return choices[s]

def truncate(minval, maxval):
    def _limit(fun):
        def _f(*args, **kargs):
            val = fun(*args, **kargs)
            return min(maxval, max(minval, val))
        return _f
    return _limit

def redraw(minval, maxval):
    def _redraw(dist):
        def _f(*args, **kargs):
            in_range = False
            while not in_range:
                val = dist(*args, **kargs)
                in_range = minval <= val <= maxval
            return val
        return _f
    return _redraw

def exponential(minval, maxval, mean, limiter=redraw):
    """Create a function that draws floats from an exponential
    distribution with expected value 'mean'. If a drawn value is less
    than minval or greater than maxval, then either another value is
    drawn (if limiter=redraw) or the drawn value is set to minval or
    maxval (if limiter=truncate)."""
    def _draw():
        return random.expovariate(1.0 / mean)
    return limiter(minval, maxval)(_draw)


def periods_loguniform(min_, max_, Tg=1, round_to_int=True):

    # [31] Maximizing Contention-Free Executions in Multiprocessor Scheduling.pdf, eq.  3,4 
    # Tg=1
    """
    Generate a list of `nsets` sets containing each `n` random periods using a
    loguniform distribution.

    Args:
        - `n`: The number of tasks in a task set.
        - `nsets`: Number of sets to generate.
        - `min_`: Period min.
        - `max_`: Period max.
    """
    ri = np.random.uniform(low=np.log(min_), high=np.log(max_))
    if Tg == 1:
        periods = np.exp(ri)
    else:
        periods = floor(np.exp(ri/Tg))*Tg
    
    if round_to_int:
        return np.rint(periods).tolist()
    else:
        return periods.tolist()


def periods_uniform( min_, max_, round_to_int=False):
    """
    Generate a list of `nsets` sets containing each `n` random periods using a
    uniform distribution.

    Args:
        - `min_`: Period min.
        - `max_`: Period max.
    """
    periods = np.random.uniform(low=min_, high=max_) #, size=(nsets, n))

    if round_to_int:
        return np.rint(periods).tolist()
    else:
        return periods.tolist()


if __name__ == "__main__":
    print("Testing")
    utilization_distribution_choices = [
            bimodal(0,1, 0.1),
            bimodal(0,1, 0.3),
            bimodal(0,1, 0.5),
            bimodal(0,1, 0.7),
            bimodal(0,1, 0.9),
            exponential(0,1, 0.1),
            exponential(0,1, 0.3),
            exponential(0,1, 0.5),
            exponential(0,1, 0.7),
            exponential(0,1, 0.9)
        ]

    # a = [periods_loguniform(10, 1000) for i in range(1,10)]
    # a = [bimodal(0,1, 0.3)()*100 for i in range(1,1000)]
    # a = [exponential(0,1, 0.7)()*100 for i in range(1,1000)]

    # plt.hist(a, bins=[i for i in range(1,800)])
    # plt.show()