class Hprof:
    def __init__(self):
        self.format_and_version = None
        self.identifier_size = None
        self.strings = []
        self.classes = []
        self.heap = None


class Heap:
    def __init__(self):
        self.root_unknowns = []
        self.root_jni_globals = []
        self.root_jni_locals = []
        self.root_java_frames = []
        self.root_native_stacks = []
        self.root_sticky_classes = []
        self.root_thread_blocks = []
        self.root_monitor_useds = []
        self.root_thread_objects = []
        self.class_objects = []
        self.instance_objects = []
        self.object_arrays = []
        self.primitive_arrays = []


class RootUnknown:
    def __init__(self):
        self.object_id = None


class RootJniGlobal:
    def __init__(self):
        self.object_id = None


class RootJniLocal:
    def __init__(self):
        self.object_id = None


class RootJavaFrame:
    def __init__(self):
        self.object_id = None


class RootNativeStack:
    def __init__(self):
        self.object_id = None


class RootStickyClass:
    def __init__(self):
        self.object_id = None


class RootThreadBlock:
    def __init__(self):
        self.object_id = None


class RootMonitorUsed:
    def __init__(self):
        self.object_id = None


class RootThreadObject:
    def __init__(self):
        self.thread_object_id = None


class String:
    def __init__(self):
        self.id = None
        self.value = None


class Class:
    def __init__(self):
        self.class_object_id = None
        self.class_name_string_id = None
        self.class_name = None


class ClassObject:
    def __init__(self):
        self.class_object_id = None
        self.class_name = None
        self.super_class_object_id = None
        self.number_of_static_fields = None
        self.static_fields = []
        self.number_of_instance_fields = None
        self.instance_fields = []


class Field:
    def __init__(self):
        self.field_name_string_id = None
        self.type_of_field = None
        self.value = None
        self.class_name = None
        self.field_name = None

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.value == other.value
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.value)


class StaticField(Field):
    pass


class InstanceField(Field):
    pass


class InstanceObject:
    def __init__(self):
        self.object_id = None
        self.class_object_id = None
        self.fields = []
        self.instance_field_values = None


class ObjectArray:
    def __init__(self):
        self.array_object_id = None
        self.array_class_object_id = None
        self.elements = []


class PrimitiveArray:
    def __init__(self):
        self.array_object_id = None
        self.element_type = None
        self.elements = []


class BasicType:
    def __init__(self, type, name, size):
        self.type = type
        self.name = name
        self.size = size


BasicType_object = BasicType(2, "object", 4)
BasicType_boolean = BasicType(4, "boolean", 1)
BasicType_char = BasicType(5, "char", 2)
BasicType_float = BasicType(6, "float", 4)
BasicType_double = BasicType(7, "double", 8)
BasicType_byte = BasicType(8, "byte", 1)
BasicType_short = BasicType(9, "short", 2)
BasicType_int = BasicType(10, "int", 4)
BasicType_long = BasicType(11, "long", 8)

BASIC_TYPE_DICT = {
    2: BasicType_object,
    4: BasicType_boolean,
    5: BasicType_char,
    6: BasicType_float,
    7: BasicType_double,
    8: BasicType_byte,
    9: BasicType_short,
    10: BasicType_int,
    11: BasicType_long
}
