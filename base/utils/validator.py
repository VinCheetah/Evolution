from base.utils.bazzar import in_range, greater_than



def is_positive(instance, attribute, x):
    if not greater_than(x, 0, False):
        raise ValueError(f"Attribute {attribute} of {instance} should be positive. Got {x}")


def greater_2(instance, attribute, x):
    if not greater_than(x, 2, False):
        raise ValueError(f"Attribute {attribute} of {instance} should be greater than 2. Got {x}")


def in_range_0_1(instance, attribute, x):
    if not in_range(x, 0, 1):
        raise ValueError(f"Attribute {attribute} of {instance} should be between 0 and 1. Got {x}")
