import inspect

def positive(x):
    return x >= 0

def strict_positive(x):
    return x > 0

def negative(x):
    return x <= 0

def strict_negative(x):
    return x < 0

def equal_to(y):
    return lambda x: x == y

def not_equal_to(y):
    return lambda x: x != y

def has_arity(n):
    return lambda f: len(inspect.signature(f).parameters) == n
def type_check(name, value, *accepted_types, optional = False):
    # check if accepted_types are all types
    if not all(type(t) == type for t in accepted_types):
        raise RuntimeError('accepted_types need to be all types')

    if value == None and not optional:
        raise TypeError(
            '{} = {} is None, but not optional'
            .format(name, value)
        )

    if value and type(value) not in accepted_types:
        if len(accepted_types) == 1:
            raise TypeError(
                '{} :: {} must be of type {}'
                .format(name, type(value), accepted_types[0])
            )
        else:
            raise TypeError(
                '{} :: {} must be either of {}'
                .format(name, type(value), accepted_types)
            )

def instance_check(name, value, *accepted_classes, quantifier = 'any', optional = False):
    if not all(inspect.isclass(t) for t in accepted_classes):
        raise RuntimeError('accepted_classes need to be all classes')
    if not quantifier in ['any','all']:
        raise RuntimeError('quantifier needs to be \'any\' or \'all\'')

    if value == None and not optional:
        raise TypeError(
            '{} is None, but not optional'
            .format(name)
        )

    q = dict(all = all, any = any)
    if value and not q[quantifier](isinstance(value,c) for c in accepted_classes):
        if len(accepted_classes) == 1:
            raise TypeError(
                '{} must be an instance of {}'
                .format(name, accepted_classes[0])
            )
        else:
            raise TypeError(
                '{} must be an instance of {} of {}'
                .format(name, quantifier, accepted_classes)
            )

def value_check(name, value, optional = False, error = ValueError, **predicates):
    if not all(callable(f) and len(inspect.signature(f).parameters) == 1
               for _,f in predicates.items()):
        raise RuntimeError(
            'accepted_classes values need to be callable with arity 1'
        )

    if value == None and not optional:
        raise TypeError(
            '{} = {} is None, but not optional'
            .format(name, value)
        )

    if value:
        for n,p in predicates.items():
            if not p(value):
                raise error(
                    '{} = {} does not satisfy predicate {}'
                    .format(name,value,n)
                )
