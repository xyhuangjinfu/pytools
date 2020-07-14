import os.path
import subprocess

from hprof import model


class _Cache:
    def __init__(self):
        self._class_object_key_class_object_id_dict = {}
        self._class_key_class_object_id_dict = {}
        self._string_key_string_id_dict = {}

    def get_class_object(self, hprof, class_object_id):
        if not self._class_object_key_class_object_id_dict:
            for co in hprof.heap.class_objects:
                self._class_object_key_class_object_id_dict[co.class_object_id] = co

        if class_object_id in self._class_object_key_class_object_id_dict:
            return self._class_object_key_class_object_id_dict[class_object_id]
        else:
            return None

    def get_class_by_class_object_id(self, hprof, class_object_id):
        if not self._class_key_class_object_id_dict:
            for cls in hprof.classes:
                self._class_key_class_object_id_dict[cls.class_object_id] = cls

        if class_object_id in self._class_key_class_object_id_dict:
            return self._class_key_class_object_id_dict[class_object_id]
        else:
            return None

    def get_string_by_id(self, hprof, string_id):
        if not self._string_key_string_id_dict:
            for s in hprof.strings:
                self._string_key_string_id_dict[s.id] = s

        return self._string_key_string_id_dict[string_id]


class HprofParser:
    """
    http://hg.openjdk.java.net/jdk6/jdk6/jdk/raw-file/tip/src/share/demo/jvmti/hprof/manual.html
    """

    def __init__(self, file_path, need_convert):
        if need_convert:
            converted_path = self._hprof_convert(file_path)
            os.remove(file_path)
        else:
            converted_path = file_path

        fd = open(converted_path, "rb")
        d = fd.read()
        fd.close()
        os.remove(converted_path)

        self._data = d
        self._hprof = model.Hprof()
        self._cache = _Cache()

        self._parse_hprof()
        pass

    def _parse_load_class(self, body_start):
        cur = body_start
        cur += 4
        class_object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
        cur += 4
        cur += 4
        class_name_string_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
        cls = model.Class()
        cls.class_object_id = class_object_id
        cls.class_name_string_id = class_name_string_id
        cls.class_name = self._cache.get_string_by_id(self._hprof, cls.class_name_string_id).value
        self._hprof.classes.append(cls)

    def _parse_string(self, body_start, body_len):
        cur = body_start
        id_for_this_string = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
        cur += 4
        str_len = body_len - 4
        s = str(self._data[cur:cur + str_len], encoding="utf-8")

        st = model.String()
        st.id = id_for_this_string
        st.value = s
        self._hprof.strings.append(st)

    def _parse_heap_dump_segment(self, body_start, body_len):
        cur = body_start
        offs = 0

        while cur + offs < body_start + body_len:
            tag = self._data[cur]
            cur += 1
            if tag == 0xFF:
                object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                ro = model.RootUnknown()
                ro.object_id = object_id
                self._hprof.heap.root_unknowns.append(ro)
            elif tag == 0x01:
                object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                cur += 4
                ro = model.RootJniGlobal()
                ro.object_id = object_id
                self._hprof.heap.root_jni_globals.append(ro)
            elif tag == 0x02:
                object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                cur += 8
                ro = model.RootJniLocal()
                ro.object_id = object_id
                self._hprof.heap.root_jni_locals.append(ro)
            elif tag == 0x03:
                object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                cur += 8
                ro = model.RootJavaFrame()
                ro.object_id = object_id
                self._hprof.heap.root_java_frames.append(ro)
            elif tag == 0x04:
                object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                cur += 4
                ro = model.RootNativeStack()
                ro.object_id = object_id
                self._hprof.heap.root_native_stacks.append(ro)
            elif tag == 0x05:
                object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                ro = model.RootStickyClass()
                ro.object_id = object_id
                self._hprof.heap.root_sticky_classes.append(ro)
            elif tag == 0x06:
                object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                cur += 4
                ro = model.RootThreadBlock()
                ro.object_id = object_id
                self._hprof.heap.root_thread_blocks.append(ro)
            elif tag == 0x07:
                object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                ro = model.RootMonitorUsed()
                ro.object_id = object_id
                self._hprof.heap.root_monitor_useds.append(ro)
            elif tag == 0x08:
                thread_object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big',
                                                  signed=False)
                cur += 4
                cur += 8
                ro = model.RootThreadObject()
                ro.thread_object_id = thread_object_id
                self._hprof.heap.root_thread_objects.append(ro)
            elif tag == 0x20:  # CLASS DUMP
                cls_obj = model.ClassObject()

                class_object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big',
                                                 signed=False)
                cur += 4

                cur += 4
                super_class_object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big',
                                                       signed=False)
                cur += 4
                cur += 24

                size_of_constant_pool_and_number_of_records = int.from_bytes(self._data[cur:cur + 2], byteorder='big',
                                                                             signed=False)
                cur += 2

                i = 0
                while i < size_of_constant_pool_and_number_of_records:
                    i += 1
                    cur += 2
                    t = self._data[cur]
                    cur += 1
                    cur += model.BASIC_TYPE_DICT[t].size

                number_of_static_fields = int.from_bytes(self._data[cur:cur + 2], byteorder='big', signed=False)
                cur += 2

                i = 0
                while i < number_of_static_fields:
                    i += 1
                    st_field = model.StaticField()

                    name_string_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                    cur += 4
                    t = self._data[cur]
                    cur += 1
                    if t == model.BasicType_object.type:
                        obj_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                        st_field.value = obj_id
                    cur += model.BASIC_TYPE_DICT[t].size

                    st_field.field_name_string_id = name_string_id
                    st_field.field_name = self._cache.get_string_by_id(self._hprof, name_string_id).value
                    st_field.type_of_field = t
                    cls_obj.static_fields.append(st_field)

                number_of_instance_fields = int.from_bytes(self._data[cur:cur + 2], byteorder='big', signed=False)
                cur += 2

                i = 0
                while i < number_of_instance_fields:
                    i += 1
                    ins_field = model.InstanceField()

                    field_name_string_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                    cur += 4
                    type_of_field = self._data[cur]
                    cur += 1

                    ins_field.field_name_string_id = field_name_string_id
                    ins_field.type_of_field = type_of_field

                    cls_obj.instance_fields.append(ins_field)

                cls_obj.class_object_id = class_object_id
                cls_obj.class_name = self._cache.get_class_by_class_object_id(self._hprof,
                                                                              cls_obj.class_object_id).class_name
                cls_obj.super_class_object_id = super_class_object_id
                self._hprof.heap.class_objects.append(cls_obj)

            elif tag == 0x21:  # INSTANCE DUMP
                ins_obj = model.InstanceObject()

                object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                cur += 4
                class_object_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                number_of_bytes_that_follow = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4

                field_values = self._data[cur:cur + number_of_bytes_that_follow]
                cur += number_of_bytes_that_follow

                ins_obj.object_id = object_id
                ins_obj.class_object_id = class_object_id
                ins_obj.instance_field_values = field_values
                self._hprof.heap.instance_objects.append(ins_obj)
            elif tag == 0x22:
                obj_array = model.ObjectArray()
                arr_obj_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                cur += 4
                number_of_elements = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                arr_class_obj_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4

                end = cur + (number_of_elements * 4)
                c = cur
                while c < end:
                    v = int.from_bytes(self._data[c:c + 4], byteorder='big', signed=False)
                    c += 4
                    obj_array.elements.append(v)

                cur += (number_of_elements * 4)

                obj_array.array_object_id = arr_obj_id
                obj_array.array_class_object_id = arr_class_obj_id
                self._hprof.heap.object_arrays.append(obj_array)
            elif tag == 0x23:
                primitive_array = model.PrimitiveArray()

                arr_obj_id = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                cur += 4
                number_of_elements = int.from_bytes(self._data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                t = self._data[cur]
                cur += 1
                cur += (number_of_elements * model.BASIC_TYPE_DICT[t].size)

                primitive_array.array_object_id = arr_obj_id
                self._hprof.heap.primitive_arrays.append(primitive_array)
            else:
                raise RuntimeError(f"unknown tag {tag}")

    def _parse_hprof(self):
        self._hprof.heap = model.Heap()

        cursor = 0
        offset = 0

        # version
        while self._data[cursor + offset] != 0:
            offset += 1

        name_version = str(self._data[cursor:cursor + offset], encoding="utf-8")
        self._hprof.format_and_version = name_version
        cursor = cursor + offset

        #
        cursor += 1
        offset = 4
        size_of_identifiers = int.from_bytes(self._data[cursor:cursor + offset], byteorder='big', signed=False)
        self._hprof.identifier_size = size_of_identifiers
        cursor = cursor + offset
        offset = 0

        # skip
        cursor += 8

        while cursor + offset < len(self._data):
            tag = self._data[cursor]
            cursor += 1
            cursor += 4
            p = self._data[cursor:cursor + 4]
            record_length = int.from_bytes(p, byteorder='big', signed=False)
            cursor += 4

            bo_st = cursor
            bo_len = record_length

            cursor += record_length

            if tag == 0x1c:
                self._parse_heap_dump_segment(bo_st, bo_len)
            elif tag == 0x01:
                self._parse_string(bo_st, bo_len)
            elif tag == 0x02:
                self._parse_load_class(bo_st)

        self._parse_instance_field()

    def _parse_instance_field(self):
        for ins_obj in self._hprof.heap.instance_objects:
            cls_obj = self._cache.get_class_object(self._hprof, ins_obj.class_object_id)
            cur = 0

            while cur < len(ins_obj.instance_field_values):
                for ins_field in cls_obj.instance_fields:
                    copy_ins_field = model.InstanceField()
                    copy_ins_field.field_name_string_id = ins_field.field_name_string_id
                    copy_ins_field.field_name = self._cache.get_string_by_id(self._hprof,
                                                                             copy_ins_field.field_name_string_id).value
                    copy_ins_field.type_of_field = ins_field.type_of_field

                    if copy_ins_field.type_of_field == model.BasicType_object.type:
                        obj_id = int.from_bytes(ins_obj.instance_field_values[cur:cur + model.BasicType_object.size],
                                                byteorder='big', signed=False)
                        copy_ins_field.value = obj_id

                    cur += model.BASIC_TYPE_DICT[copy_ins_field.type_of_field].size
                    ins_obj.fields.append(copy_ins_field)
                cls_obj = self._cache.get_class_object(self._hprof, cls_obj.super_class_object_id)

    @staticmethod
    def _hprof_convert(file_path):
        converted_path = file_path + ".java.hprof"
        subprocess.check_call(["hprof-conv", file_path, converted_path])
        return converted_path

    def get(self):
        return self._hprof


if __name__ == '__main__':
    pass
