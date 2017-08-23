import types


if hasattr(types, 'ClassType'):
    class_types = (type, types.ClassType)
else:
    class_types = (type,)
