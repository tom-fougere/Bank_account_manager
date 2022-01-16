def get_class_attributes(my_class):
    return [att for att in dir(my_class) if not att.startswith('__') and not callable(getattr(my_class, att))]
