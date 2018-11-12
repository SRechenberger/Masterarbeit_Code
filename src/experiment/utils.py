import src.solver.utils as s_utils
import math
import numpy as np
import sys
from scipy.special import binom
from src.utils import *
from src.solver.utils import Formula, Assignment

def eta(p):
    if p == 0:
        return 0
    else:
        return -p * math.log(p,2)


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
            self.length -= 1
            return ret

    def is_full(self):
        return self.length == self.buffsize


    def is_empty(self):
        return self.length == 0


class WindowEntropy:
    def __init__(self, window_width, blank = None):
        self.queue = Queue(window_width, default = blank)
        self.symbol_count = {}
        self.current_entropy = 0
        self.blank = None


    def count(x):
        # push the symbol in the queue,
        # and catch what may be dropped out of it.
        dropped = self.queue.push(x)

        # if the dropped and the new symbol are the same,
        # the entropy does not change
        if dropped == x:
            return

        # if a symbol was dropped
        if dropped != self.blank:
            assert dropped in self.symbol_count[dropped],\
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
        if x not in self.count_symbols:
            self.count_symbols[x] = 0

        # calculate new and old share of the new symbol
        h_old = eta(self.count_symbols[x]/self.window_width)
        h_new = eta((self.count_symbols[x]+1)/self.window_width)

        # update counter and entropy
        self.symbol_count[x] += 1
        self.current_entropy += h_new - h_old


    def get_entropy(if_not_ready = None):
        if not self.queue.is_full():
            return if_not_ready
        else:
            return self.current_entropy


class Measurement:
    """ Abstract Measurement Class;
    the generic SLS solver needs the given measurement object
    to be an instance of this class or a subclass.
    """
    def __init__(self, formula):
        pass
    def init_run(self, assgn):
        pass

    def end_run(self, success = False):
        pass

    def count(self, flipped_var):
        pass


class EntropyMeasurement(Measurement):

    """ Counts probability distribution of
        - Single steps
        - Joint steps
        - Mutual Information
        - TMS steps
    """

    def __init__(self, formula):
        if __debug__:
            instance_check('formula',formula,Formula)

        self.run_id = 0
        self.sat_assgn = formula.satisfying_assignment
        self.formula   = formula
        self.run_measurements = []
        self.tms_steps = {}

    def init_run(self, assgn):
        if __debug__:
            instance_check('assgn',assgn,Assignment)

        self.run_id += 1

        self.steps = 0
        # path entropy
        self.single_steps = {}

        # joint path entropy
        self.joint_steps = {}
        self.last_step = None

        # TMS entropy
        self.start_assgn = assgn
        self.curr_assgn = assgn
        self.curr_hamming_dist = self.sat_assgn.hamming_dist(assgn)
        self.tms_steps = {}


    def end_run(self, success = False):
        self.run_measurements.append(
            dict(
                flips               = self.steps,
                single_entropy      = entropy(self.single_steps),
                joint_entropy       = entropy(self.joint_steps),
                mututal_information = mutual_information(self.joint_steps),
                hamming_dist        = self.formula.satisfying_assignment.hamming_dist(self.start_assgn),
                start_assgn         = str(self.start_assgn),
                final_assgn         = str(self.curr_assgn),
                success             = success,
            )
        )


    def get_tms_entropy(self, eps = 0.001, max_loops = 10000):
        # get number of states
        tms_states = self.sat_assgn.num_vars + 1

        # initiate initial distribution
        T_0 = binomial_vec(tms_states)

        # initiate transition matrix
        Pi = np.zeros((tms_states,tms_states))

        ## absolute probability
        for (s,t),count in self.tms_steps.items():
            Pi[s][t] = count


        ## relative probability
        for i,row in enumerate(Pi):
            s = sum(row)
            if s == 0:
                if i == 0:
                    Pi[0][0] = 1
                    Pi[0][1] = 1
                    s = 2
                elif i == tms_states-1:
                    Pi[i][i] = 1
                    Pi[i][i-1] = 1
                    s = 2
                else:
                    Pi[i][i+1] = 1
                    Pi[i][i-1] = 1
                    s = 2

            for j,cell in enumerate(row):
                Pi[i][j] = cell/s

        for row in Pi:
            test = 0
            for cell in row:
                if cell > 0:
                    test += 1



        # approximate stationary distribution
        distr = T_0.copy()

        s = sum(distr)

        loops = 0
        converging = 0
        while loops < 100 or (converging < len(distr) and loops < max_loops):
            # calculate new tmp
            tmp = distr @ Pi

            converging = 0
            for (d,t) in zip(distr,tmp):
                if abs(d-t) <= eps:
                    converging += 1

            # save new tmp
            distr = tmp

            # next loop
            loops += 1

        # calculate state entropy
        state_entropy = np.array([sum(map(eta,row)) for row in Pi])

        # calculate entropy rate
        h = np.inner(state_entropy, distr)
        return h


    def count(self, flipped_var):
        if __debug__:
            type_check('flipped_var',flipped_var,int)
            value_check(
                'flipped_var',flipped_var,
                strict_positive = strict_positive
            )

        # count steps
        self.steps += 1

        # path entropy
        if flipped_var in self.single_steps:
            self.single_steps[flipped_var] += 1
        else:
            self.single_steps[flipped_var] = 1

        # joint path entropy
        if self.last_step:
            tpl = (self.last_step, flipped_var)
            if tpl in self.joint_steps:
                self.joint_steps[tpl] += 1
            else:
                self.joint_steps[tpl] = 1

        self.last_step = flipped_var

        # TMS entropy
        #  there are no sideway-steps considering hamming distance!
        tmp = self.curr_hamming_dist
        if self.curr_assgn[flipped_var] == self.sat_assgn[flipped_var]:
            self.curr_hamming_dist -= 1
        else:
            self.curr_hamming_dist += 1

        n = self.formula.num_vars
        tpl = (n - tmp, n - self.curr_hamming_dist)
        if tpl in self.tms_steps:
            self.tms_steps[tpl] += 1
        else:
            self.tms_steps[tpl] = 1



class FormulaSupply:
  """ Support of formulae, holding at max 'buffsize' formulae,
  and reloads at max 'buffsize' new, if necessary.
  """
  def __init__(self, file_paths, buffsize = 10):
    self.file_paths = file_paths
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


