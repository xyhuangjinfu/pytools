import model

_class_object_dict = {}
_class_string_id_dict = {}
_class_object_id_dict = {}
_instance_object_dict = {}
_instance_object_class_object_id_dict = {}
_object_array_object_dict = {}
_string_value_dict = {}
_string_id_dict = {}


def get_object_array_object(object_array_object_id, heap):
    if not _object_array_object_dict:
        for oa in heap.object_arrays:
            _object_array_object_dict[oa.array_object_id] = oa

    if object_array_object_id in _object_array_object_dict:
        return _object_array_object_dict[object_array_object_id]
    else:
        return None


def get_instance_object(instance_object_id, heap):
    if not _instance_object_dict:
        for io in heap.instance_objects:
            _instance_object_dict[io.object_id] = io

    if instance_object_id in _instance_object_dict:
        return _instance_object_dict[instance_object_id]
    else:
        return None


def get_instance_objects_by_class_object_id(class_object_id, heap):
    if not _instance_object_class_object_id_dict:
        for io in heap.instance_objects:
            if io.class_object_id in _instance_object_class_object_id_dict:
                _instance_object_class_object_id_dict[io.class_object_id].append(io)
            else:
                _instance_object_class_object_id_dict[io.class_object_id] = [io]

    if class_object_id in _instance_object_class_object_id_dict:
        return _instance_object_class_object_id_dict[class_object_id]
    else:
        return None


def get_class_object(class_object_id, heap):
    if not _class_object_dict:
        for co in heap.class_objects:
            _class_object_dict[co.class_object_id] = co

    if class_object_id in _class_object_dict:
        return _class_object_dict[class_object_id]
    else:
        return None


def get_class_by_string_id(string_id, hprof):
    if not _class_string_id_dict:
        for cls in hprof.classes:
            _class_string_id_dict[cls.class_name_string_id] = cls

    if string_id in _class_string_id_dict:
        return _class_string_id_dict[string_id]
    else:
        return None


def get_class_by_class_object_id(class_object_id, hprof):
    if not _class_object_id_dict:
        for cls in hprof.classes:
            _class_object_id_dict[cls.class_object_id] = cls

    if class_object_id in _class_object_id_dict:
        return _class_object_id_dict[class_object_id]
    else:
        return None


def get_string_by_id(string_id, hprof):
    if not _string_id_dict:
        for s in hprof.strings:
            _string_id_dict[s.id] = s

    return _string_id_dict[string_id]


def get_string_by_value(string_value, hprof):
    if not _string_value_dict:
        for s in hprof.strings:
            _string_value_dict[s.value] = s

    return _string_value_dict[string_value]


def get_basic_type(type):
    if type == 2:
        return model.BasicType_object
    elif type == 4:
        return model.BasicType_boolean
    elif type == 5:
        return model.BasicType_char
    elif type == 6:
        return model.BasicType_float
    elif type == 7:
        return model.BasicType_double
    elif type == 8:
        return model.BasicType_byte
    elif type == 9:
        return model.BasicType_short
    elif type == 10:
        return model.BasicType_int
    elif type == 11:
        return model.BasicType_long
