import math
from src.solver.utils import Formula, Assignment
from src.experiment.utils import entropy, mutual_information, WindowEntropy


class Measurement:
    """ Abstract Measurement Class;
    the generic SLS solver needs the given measurement object
    to be an instance of this class or a subclass.
    """
    def __init__(self, formula, *more_args):
        pass
    def init_run(self, assgn):
        pass

    def end_run(self, success = False):
        pass

    def count(self, flipped_var):
        pass


def entropy_data(window_width):
    return dict(
        latest=0,
        latest_at=None,
        minimum=math.log(window_width,2),
        minimum_at=None,
        maximum=0,
        maximum_at=None,
        accum=0,
        count=0,
    )

def update_entropy_data(data, curr_entropy, curr_hamming_dist):
    data['latest'] = curr_entropy
    data['latest_at'] = curr_hamming_dist
    if curr_entropy < data['minimum']:
        data['minimum'] = curr_entropy
        data['minimum_at'] = curr_hamming_dist
    if curr_entropy > data['maximum']:
        data['maximum'] = curr_entropy
        data['maximum_at'] = curr_hamming_dist
    data['accum'] += curr_entropy
    data['count'] += 1


class RuntimeMeasurement(Measurement):
    def __init__(self, formula, window_width):
        self.flips = 0
        self.success = False

    def end_run(self, success=False):
        self.success = success

    def count(self, flip):
        self.flips += 1


class EntropyMeasurement(Measurement):

    """ Counts probability distribution of
        - Single steps
        - Joint steps
        - Mutual Information
        - TMS steps
    """

    def __init__(self, formula, window_width):
        assert isinstance(formula, Formula),\
            "formula = {} is no Formula".format(formula)
        assert isinstance(window_width,int),\
            "window_width = {} :: {} is no int".format(window_width, type(window_width))

        self.run_id = 0
        self.window_width = window_width


        self.run_measurements = []

        self.sat_assgn = formula.satisfying_assignment
        self.formula   = formula
        self.base      = 2
        self.tms_steps = {}

        self.last_step = None



    def count(self, flip):
        assert isinstance(flip,int),\
            "flip = {} :: {} is no int".format(flip, type(flip))
        assert flip > 0,\
            "flip = {} <= 0".format(flip)

        self.steps += 1
        self.simple_entropy_tracker.count(flip)
        h_tmp = self.simple_entropy_tracker.get_entropy()
        if h_tmp:
            update_entropy_data(
                self.simple_entropy_data,
                h_tmp,
                self.curr_hamming_dist
            )

        if self.last_step:
            self.joint_entropy_tracker.count((self.last_step,flip))
            self.left_entropy_tracker.count(self.last_step)
            self.right_entropy_tracker.count(flip)


            h_tmp = self.joint_entropy_tracker.get_entropy()
            if h_tmp:
                update_entropy_data(
                    self.joint_entropy_data,
                    h_tmp,
                    self.curr_hamming_dist
                )
                l_tmp = self.left_entropy_tracker.get_entropy()
                r_tmp = self.right_entropy_tracker.get_entropy()
                update_entropy_data(
                    self.mutual_information_data,
                    l_tmp + r_tmp - h_tmp,
                    self.curr_hamming_dist
                )
                update_entropy_data(
                    self.cond_entropy,
                    h_tmp - l_tmp,
                    self.curr_hamming_dist
                )
        self.last_step = flip

        # TMS entropy
        #  there are no sideway-steps considering hamming distance!
        tmp = self.curr_hamming_dist
        if self.curr_assgn[flip] == self.sat_assgn[flip]:
            self.curr_hamming_dist -= 1
        else:
            self.curr_hamming_dist += 1

        n = self.formula.num_vars
        tpl = (n - tmp, n - self.curr_hamming_dist)
        if tpl in self.tms_steps:
            self.tms_steps[tpl] += 1
        else:
            self.tms_steps[tpl] = 1


    def init_run(self, assgn):
        assert isinstance(assgn, Assignment),\
            "assgn = {} :: {} is no Assignment".format(assgn, type(assgn))

        self.run_id += 1

        self.steps = 0
        # path entropy
        self.simple_entropy_tracker = WindowEntropy(self.window_width, base=self.base)
        self.simple_entropy_data = entropy_data(self.window_width)

        # joint path entropy
        self.joint_entropy_tracker = WindowEntropy(self.window_width, base=self.base)
        self.left_entropy_tracker = WindowEntropy(self.window_width, base=self.base)
        self.right_entropy_tracker = WindowEntropy(self.window_width, base=self.base)
        self.joint_entropy_data = entropy_data(self.window_width-1)
        self.mutual_information_data = entropy_data(self.window_width-1)
        self.cond_entropy = entropy_data(self.window_width-1)
        self.last_step = None

        # TMS entropy
        self.start_assgn = assgn
        self.curr_assgn = assgn
        self.curr_hamming_dist = self.sat_assgn.hamming_dist(assgn)
        # self.tms_steps = {}


    def end_run(self, success = False):
        self.run_measurements.append(
            dict(
                flips=self.steps,
                single_entropy=self.simple_entropy_data,
                joint_entropy=self.joint_entropy_data,
                mutual_information=self.mutual_information_data,
                cond_entropy=self.cond_entropy,
                hamming_dist=self.formula.satisfying_assignment.hamming_dist(self.start_assgn),
                start_assgn=str(self.start_assgn),
                final_assgn=str(self.curr_assgn),
                success=success,
            )
        )
