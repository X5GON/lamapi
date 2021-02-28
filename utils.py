#!/usr/bin/env python3
import time
import sklearn.manifold as manifold
import numpy as np
from sklearn.decomposition import PCA, TruncatedSVD, SparsePCA
from argparse import ArgumentParser
import configparser


# a wrapper function for execution time measurement
def time_usage(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        retval = func(*args, **kwargs)
        end = time.perf_counter()
        print("elapsed time: (%s) %f ms" % (func.__name__, 1000*(end - start)))
        return retval
    return wrapper


def deprecated(func):
    def wrapper(*args, **kwargs):
        print("Warning deprecated function:", func.__name__)
        return func(args, kwargs)
    return wrapper


def dimension_reduction(reduction_type, n_neighbors):
    if reduction_type == "PCA":
        reductor = PCA(n_components=2, svd_solver='full')
    elif reduction_type == "LLE":
        reductor = manifold.LocallyLinearEmbedding(n_neighbors=n_neighbors,
                                                   n_components=min(2, n_neighbors),
                                                   method="modified",
                                                   n_jobs=-1)
    elif reduction_type == "TruncatedSVD":
        reductor = TruncatedSVD(n_components=2)
    elif reduction_type == "SparsePCA":
        reductor = SparsePCA(n_components=2, n_jobs=-1)

    return reductor


def filter_knn(matrix, vectors, dists, neigh_ids):
    mask = np.zeros_like(matrix)
    mask[np.triu_indices_from(mask)] = np.Inf
    indices = set(np.argwhere((matrix + mask) < 1e-4)[:, 0])
    good_ind = list(set(range(matrix.shape[0])) - indices)
    matrix = matrix[good_ind, :]
    matrix = matrix[:, good_ind]
    if hasattr(vectors, 'tocsr'):
        vectors = vectors.tocsr()[good_ind, :].tocoo()
    else:
        vectors = [v for i, v in enumerate(vectors) if i in good_ind]
    neig_before = neigh_ids
    neigh_ids, dists = zip(*((d, v) for i, (d, v) in enumerate(zip(neigh_ids, dists)) if i in good_ind))
    neigh_ids, dists = list(neigh_ids), list(dists)
    return matrix, vectors, dists, neigh_ids


def get_args():
    # Needed when updating the models when the API is not running
    # Needed when configs are not passed as arguments in the API launchment
    config = configparser.ConfigParser()
    config.read('config.ini')

    parser = ArgumentParser(prog='argpconfig')
    parser.add_argument('--host',
                        '-hs',
                        required=True,
                        help='Host to be specified on api launch.',
                        default=config['lamapi']['host'])
    parser.add_argument('--port',
                        '-p',
                        required=True,
                        help='Port to be specified on api launch.',
                        default=config['lamapi']['port'])
    parser.add_argument('--debug',
                        '-d',
                        help='Activate debug mode',
                        action='store_true',
                        default=False)
    parser.add_argument('--cert',
                        '-ct',
                        help='Point to your ssl certification path',
                        default=config['lamapi']['cert'])
    parser.add_argument('--key',
                        '-ky',
                        help='Point to your ssl privatekey path',
                        default=config['lamapi']['key'])
    parser.add_argument('--dbhost',
                        '-bdh',
                        help='Point to x5gon db host',
                        efault=config['x5gondb']['dbhost'])
    parser.add_argument('--dbname',
                        '-bdn',
                        help='Point to x5gon db name',
                        default=config['x5gondb']['dbname'])
    parser.add_argument('--dbuser',
                        '-bdu',
                        help='Point to x5gon db user',
                        default=config['x5gondb']['dbuser'])
    parser.add_argument('--dbpass',
                        '-bdpw',
                        help='Point to x5gon db user password',
                        default=config['x5gondb']['dbpass'])
    parser.add_argument('--dbport',
                        '-bdp',
                        help='Point to x5gon db port',
                        default=config['x5gondb']['dbport'])
    args = parser.parse_args()
    return args
