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


