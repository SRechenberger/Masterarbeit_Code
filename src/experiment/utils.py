"""
## Module src.experiment.utils

### Contents
    - function eta
    - function arr_entropy
    - function entropy
    - function mutual_information
    - class Queue
    - class WindowEntropy
"""


import math
from functools import partial


def eta(p, base=2):
    """ eta function to calculate entropy """

    if p <= 0:
        return 0
    if p >= 1:
        return 0
    return -p * math.log(p, base)


def arr_entropy(distr, base=2):
    """ Calculate entropy from a probability distribution given as an array """

    return sum(map(partial(eta, base=base), distr))


def entropy(distr, base=2):
    """ calculate entropy from a measured distribution given as a dict """

    total = 0
    for _, count in distr.items():
        total += count

    h = 0
    for _, count in distr.items():
        h += eta(count/total, base=base)

    return h


def mutual_information(distr):
    """ Calculate the mututal information from a measured distribution
    of joint symbols given as a dict
    """

    X = {}
    Y = {}
    for (x, y), v in distr.items():
        if x in X:
            X[x] += v
        else:
            X[x] = v

        if y in Y:
            Y[y] += v
        else:
            Y[y] = v

    return entropy(X) + entropy(Y) - entropy(distr)


class Queue:
    """ FIFO storage """
    def __init__(self, buffsize, default=None):
        self.buffsize = buffsize
        self.default = default
        self.buffer = [self.default for _ in range(0, self.buffsize)]
        self.length = 0
        self.begin = 0


    def push(self, x):
        """ Push a value into the queue """
        assert self.length >= 0,\
            "self.length = {} < 0".format(self.length)

        if self.length < self.buffsize:
            self.buffer[(self.begin + self.length) % self.buffsize] = x
            self.length += 1
            return self.default

        ret = self.buffer[self.begin]
        self.buffer[(self.begin + self.length) % self.buffsize] = x
        self.begin += 1
        self.begin %= self.buffsize
        return ret


    def top(self):
        """ Get the next value to be put out by the queue, without popping it out """
        if self.length <= 0:
            raise IndexError('Empty Queue')

        return self.buffer[self.begin]


    def pop(self):
        """ Pop out the next value of the queue """
        if self.length <= 0:
            raise IndexError('Empty Queue')

        ret = self.buffer[self.begin]
        self.begin += 1
        self.begin %= self.buffsize
        self.length -= 1
        return ret

    def is_full(self):
        """ Check whether the queue is completely filled """
        return self.length == self.buffsize


    def is_empty(self):
        """ Check wether the queue is empty """
        return self.length == 0


class WindowEntropy:
    """ Trace the entropy over a window of a sequence """
    def __init__(self, window_width, base=2, blank=None):
        self.queue = Queue(window_width, default=blank)
        self.window_width = window_width
        self.symbol_count = {}
        self.current_entropy = 0
        self.blank = None
        self.base = base


    def count(self, x):
        """ Count a new symbol """
        # push the symbol in the queue,
        # and catch what may be dropped out of it.
        dropped = self.queue.push(x)

        # if the dropped and the new symbol are the same,
        # the entropy does not change
        if dropped == x:
            return

        # if a symbol was dropped
        if dropped != self.blank:
            assert dropped in self.symbol_count,\
                "symbol {} never counted".format(dropped)
            assert self.symbol_count[dropped] > 0,\
                "self.symbol_count[{}] = {} <= 0".format(dropped, self.symbol_count[dropped])

            # the old share of the dropped symbol
            h_old = eta(self.symbol_count[dropped] / self.window_width, self.base)

            # the new share of the dropped symbol
            h_new = eta((self.symbol_count[dropped] - 1) / self.window_width, self.base)

            # update the counter
            self.symbol_count[dropped] -= 1

            # update the current entropy
            self.current_entropy += h_new - h_old

        # init the count for the new symbol,
        # if not already done
        if x not in self.symbol_count:
            self.symbol_count[x] = 0

        # calculate new and old share of the new symbol
        h_old = eta(self.symbol_count[x]/self.window_width, self.base)
        h_new = eta((self.symbol_count[x]+1)/self.window_width, self.base)

        # update counter and entropy
        self.symbol_count[x] += 1
        self.current_entropy += h_new - h_old


    def get_entropy(self, if_not_ready=None):
        """ Return the entropy traced, if the minimum path length is reached.

        Keywords:
            if_not_ready -- what to return, if the minimum path length is not reached.

        Returns:
            h -- entropy value of the current path window
        """
        if not self.queue.is_full():
            return if_not_ready

        return self.current_entropy
