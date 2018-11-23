import src.solver.utils as s_utils
import math
import numpy as np
import sys
from scipy.special import binom
from src.solver.utils import Formula, Assignment


def eta(p):
    if p == 0:
        return 0
    else:
        return -p * math.log(p,2)

def arr_entropy(distr):
    return sum(map(eta,distr))

def entropy(distr):
    total = 0
    for _, count in distr.items():
        total += count

    h = 0
    for symbol, count in distr.items():
        h += eta(count/total)

    return h


def mutual_information(distr):
    X = {}
    Y = {}
    for (x,y),v in distr.items():
        if x in X:
            X[x] += v
        else:
            X[x] = v

        if y in Y:
            Y[y] += v
        else:
            Y[y] = v

    return entropy(X) + entropy(Y) - entropy(distr)


def binomial_vec(length):
    return np.array([binom(length-1,x)/pow(2,length-1) for x in range(0,length)])


class Queue:
    def __init__(self, buffsize, default = None):
        self.buffsize = buffsize
        self.default = default
        self.buffer = [self.default for _ in range(0,self.buffsize)]
        self.length = 0
        self.begin = 0


    def push(self, x):
        assert self.length >= 0,\
            "self.length = {} < 0".format(self.length)

        if self.length < self.buffsize:
            self.buffer[(self.begin + self.length) % self.buffsize] = x
            self.length += 1
            return self.default
        else:
            ret = self.buffer[self.begin]
            self.buffer[(self.begin + self.length) % self.buffsize] = x
            self.begin += 1
            self.begin %= self.buffsize
            return ret


    def top(self):
        if self.length <= 0:
            raise IndexError('Empty Queue')

        else:
            return self.buffer[self.begin]


    def pop(self):
        if self.length <= 0:
            raise IndexError('Empty Queue')

        else:
            ret = self.buffer[self.begin]
            self.begin += 1
            self.begin %= self.buffsize
            self.length -= 1
            return ret

    def is_full(self):
        return self.length == self.buffsize


    def is_empty(self):
        return self.length == 0


class WindowEntropy:
    def __init__(self, window_width, blank = None):
        self.queue = Queue(window_width, default = blank)
        self.window_width = window_width
        self.symbol_count = {}
        self.current_entropy = 0
        self.blank = None


    def count(self, x):
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
                "self.symbol_count[{}] = {} <= 0".format(dropped,self.symbol_count[dropped])

            # the old share of the dropped symbol
            h_old = eta(self.symbol_count[dropped] / self.window_width)

            # the new share of the dropped symbol
            h_new = eta((self.symbol_count[dropped] - 1) / self.window_width)

            # update the counter
            self.symbol_count[dropped] -= 1

            # update the current entropy
            self.current_entropy += h_new - h_old

        # init the count for the new symbol,
        # if not already done
        if x not in self.symbol_count:
            self.symbol_count[x] = 0

        # calculate new and old share of the new symbol
        h_old = eta(self.symbol_count[x]/self.window_width)
        h_new = eta((self.symbol_count[x]+1)/self.window_width)

        # update counter and entropy
        self.symbol_count[x] += 1
        self.current_entropy += h_new - h_old


    def get_entropy(self, if_not_ready = None):
        if not self.queue.is_full():
            return if_not_ready
        else:
            return self.current_entropy


class FormulaSupply:
  """ Support of formulae, holding at max 'buffsize' formulae,
  and reloads at max 'buffsize' new, if necessary.
  """
  def __init__(self, file_paths, buffsize = 10):
    self.file_paths = file_paths
    self.length = len(self.file_paths)
    self.buffer = []
    self.buffsize = 10
    self.__fill_buffer()

  def __fill_buffer(self):
    i = self.buffsize
    while i > 0 and self.file_paths:
        fp = self.file_paths.pop()
        with open(fp, 'r') as f:
            self.buffer.append((fp,s_utils.Formula(f.read())))
        i -= 1

  def __iter__(self):
    return self

  def __next__(self):
    if not self.buffer and not self.file_paths:
      raise StopIteration()
    elif not self.buffer:
      self.__fill_buffer()
    return self.buffer.pop()

  def __len__(self):
    return self.length

class BloomFilter:
    def __hash_func(self, value, k=0):
        return (hash(value) + (hash(value) + (11*13+1)) ** k) % self.m


    def __init__(self, max_elements=1000, error_rate=0.1):
        self.m = math.ceil(max_elements * math.log(error_rate,.5)/math.log(2))
        self.k = math.ceil(math.log(2) * self.m/max_elements)
        self.array = [False] * self.m


    def add(self, value):
        for k in range(0, self.k):
            self.array[self.__hash_func(value, k)] = True


    def __contains__(self, value):
        for k in range(0, self.k):
            if not self.array[self.__hash_func(value, k)]:
                return False

        return True





