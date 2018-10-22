import src.solver.utils as s_utils

class Measurement:
    """ Abstract Measurement Class;
    the generic SLS solver needs the given measurement object
    to be an instance of this class or a subclass.
    """
    def init_run(self, assgn):
        raise Warning('Nothing implemented yet.')

    def count(self, flipped_var):
        raise Warning('Nothing implemented yet.')


class DummyMeasurement(Measurement):
    def __init__(self):
        self.flips = 0

    def init_run(self,assgn):
        pass

    def count(self, flipped_var):
        self.flips += 1


class EntropyMeasurement(Measurement):
    """ Counts probability distribution ofr
        - Single steps
        - Joint steps
        - TMS steps
    """

    def __init__(self, formula):
        if __debug__:
            instance_check('formula',formula,Formula)

        self.run_id = 0
        self.sat_assgn = formula.satisfying_assignment
        self.formula   = formula
        self.single_steps_total = [] # :: List[Dict[int,int]]
        self.joint_steps_total  = [] # :: List[Dict[(int,int),int)]]
        self.tms_steps = {}          # :: Dict[(int,int),int]


    def init_run(self, assgn):
        if __debug__:
            instance_check('assgn',assgn,Assignment)

        # save previous path, if there was one
        if self.run_id > 0:
            self.single_steps_total.append(self.single_steps)
            self.joint_steps_total.append(self.joint_steps)

        self.run_id += 1

        # path entropy
        self.single_steps = {}

        # joint path entropy
        self.joint_steps = {}
        self.last_step = None

        # TMS entropy
        self.curr_assgn = assgn
        self.curr_hamming_dist = self.sat_assgn.hamming_dist(assgn)


    def count(self, flipped_var):
        if __debug__:
            type_check('flipped_var',flipped_var,int)
            value_check(
                'flipped_var',flipped_var,
                strict_positive = strict_positive
            )

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
        tmp = self.curr_hamming_dist
        if self.curr_assgn[flipped_var] == self.sat_assgn[flipped_var]:
            self.curr_hamming_dist += 1
        else:
            self.curr_hamming_dist -= 1

        tpl = (tmp, self.curr_hamming_dist)
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
      self.buffer.append(s_utils.Formula(self.file_paths.pop()))
      i -= 1

  def __iter__(self):
    return self

  def __next__(self):
    if not self.buffer and not self.file_paths:
      raise StopIteration()
    elif not self.buffer:
      self.__fill_buffer()
    return self.buffer.pop()


