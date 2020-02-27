"""
the code for geometric median is adapted from https://github.com/mrwojo/geometric_median/blob/master/geometric_median/geometric_median.py
"""

import numpy as np
from scipy.optimize import minimize
from scipy.spatial.distance import cdist


def geometric_median(points):
    """
    Calculates the geometric median of an array of points.
    Weiszfeld's algorithm as described on Wikipedia.
    """
    points = np.asarray(points)

    def distance_func(x):
        return cdist([x], points)

    # initial guess: centroid
    guess = points.mean(axis=0)

    iters = 0

    while iters < 1000:
        distances = distance_func(guess).T
        distances = np.where(distances == 0, 1, distances)
        guess_next = (points/distances).sum(axis=0) / (1./distances).sum(axis=0)
        guess_movement = np.sqrt(((guess - guess_next)**2).sum())
        guess = guess_next
        if guess_movement <= 1e-5:
            break

        iters += 1

    return guess

