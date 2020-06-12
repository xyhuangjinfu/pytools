import cache
import model

TYPE_LEN = {
    2: 4,  # object
    4: 1,  # boolean
    5: 2,  # char
    6: 4,  # float
    7: 8,  # double
    8: 1,  # byte
    9: 2,  # short
    10: 4,  # int
    11: 8  # long
}
TYPE_NAME = {
    2: "object",
    4: "boolean",
    5: "char",
    6: "float",
    7: "double",
    8: "byte",
    9: "short",
    10: "int",
    11: "long"
}

STR_VALUE_TO_ID_DICT = {}
STR_ID_TO_VALUE_DICT = {}
CLASS_NAME_TO_ID_DICT = {}
CLASS_ID_TO_NAME_DICT = {}
INSTANCE_ID = []
INSTANCE_CLASS_OBJECT_ID = []
INSTANCE_ID_TO_CLASS_DICT = {}
THREAD_ID_TO_NAME_DICT = {}


# str value -> str id -> class object id -> filter instance id


def parse_start_thread(data, body_start, body_len, name_to_id_dict):
    cur = body_start
    cur += 4
    thread_object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
    cur += 4
    cur += 4
    thread_name_string_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
    cur += 4
    THREAD_ID_TO_NAME_DICT[thread_object_ID] = thread_name_string_ID


def parse_load_class(data, body_start, body_len, name_to_id_dict, classes_list):
    cur = body_start
    cur += 4
    class_object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
    cur += 4
    cur += 4
    class_name_string_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
    name_to_id_dict[class_name_string_ID] = class_object_ID
    CLASS_ID_TO_NAME_DICT[class_object_ID] = class_name_string_ID
    cls = model.Class()
    cls.class_object_id = class_object_ID
    cls.class_name_string_id = class_name_string_ID
    classes_list.append(cls)


def parse_string(data, body_start, body_len, value_to_id_dict, id_to_value_dict, string_list):
    cur = body_start
    ID_for_this_string = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
    cur += 4
    l = body_len - 4
    s = str(data[cur:cur + l], encoding="utf-8")

    value_to_id_dict[s] = ID_for_this_string
    id_to_value_dict[ID_for_this_string] = s

    st = model.String()
    st.id = ID_for_this_string
    st.value = s
    string_list.append(st)


def parse_heap_dump_segment_record(data, body_start, body_len, heap):
    # print(f"parse_heap_dump_segment_record {body_start} {body_len} , {len(data)}")
    cur = body_start
    offs = 0

    while cur + offs < body_start + body_len:
        type = data[cur]
        cur += 1
        if type == 0xFF:
            objid = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            ro = model.RootUnknown()
            ro.object_id = objid
            heap.root_unknowns.append(ro)
        elif type == 0x01:
            object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            JNI_global_ref_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            ro = model.RootJniGlobal()
            ro.object_id = object_ID
            heap.root_jni_globals.append(ro)
        elif type == 0x02:
            object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            cur += 8
            ro = model.RootJniLocal()
            ro.object_id = object_ID
            heap.root_jni_locals.append(ro)
        elif type == 0x03:
            object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            cur += 8
            ro = model.RootJavaFrame()
            ro.object_id = object_ID
            heap.root_java_frames.append(ro)
        elif type == 0x04:
            object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            cur += 4
            ro = model.RootNativeStack()
            ro.object_id = object_ID
            heap.root_native_stacks.append(ro)
        elif type == 0x05:
            object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            ro = model.RootStickyClass()
            ro.object_id = object_ID
            heap.root_sticky_classes.append(ro)
        elif type == 0x06:
            object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            cur += 4
            ro = model.RootThreadBlock()
            ro.object_id = object_ID
            heap.root_thread_blocks.append(ro)
        elif type == 0x07:
            object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            ro = model.RootMonitorUsed()
            ro.object_id = object_ID
            heap.root_monitor_useds.append(ro)
        elif type == 0x08:
            thread_object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big',
                                              signed=False)
            cur += 4
            cur += 8
            ro = model.RootThreadObject()
            ro.thread_object_id = thread_object_ID
            heap.root_thread_objects.append(ro)
        elif type == 0x20:  # CLASS DUMP
            cls_obj = model.ClassObject()

            class_object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big',
                                             signed=False)
            cur += 4
            cur += 32

            size_of_constant_pool_and_number_of_records = int.from_bytes(data[cur:cur + 2], byteorder='big',
                                                                         signed=False)
            cur += 2

            i = 0
            while i < size_of_constant_pool_and_number_of_records:
                i += 1
                cur += 2
                t = data[cur]
                cur += 1
                cur += TYPE_LEN[t]

            Number_of_static_fields = int.from_bytes(data[cur:cur + 2], byteorder='big', signed=False)
            cur += 2

            i = 0
            while i < Number_of_static_fields:
                i += 1
                st_field = model.StaticField()

                name_string_id = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                t = data[cur]
                cur += 1
                if t == model.BasicType_object.type:
                    obj_id = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
                    st_field.value = obj_id
                cur += TYPE_LEN[t]

                st_field.field_name_string_id = name_string_id
                st_field.type_of_field = t
                cls_obj.static_fields.append(st_field)

            Number_of_instance_fields = int.from_bytes(data[cur:cur + 2], byteorder='big', signed=False)
            cur += 2

            i = 0
            while i < Number_of_instance_fields:
                i += 1
                ins_field = model.InstanceField()
                # cur += 5

                field_name_string_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
                cur += 4
                type_of_field = data[cur]
                cur += 1

                ins_field.field_name_string_id = field_name_string_ID
                ins_field.type_of_field = type_of_field

                cls_obj.instance_fields.append(ins_field)

            cls_obj.class_object_id = class_object_ID
            heap.class_objects.append(cls_obj)

        elif type == 0x21:  # INSTANCE DUMP
            ins_obj = model.InstanceObject()

            object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            INSTANCE_ID.append(object_ID)
            cur += 4
            cur += 4
            class_object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            INSTANCE_CLASS_OBJECT_ID.append(class_object_ID)
            cur += 4
            number_of_bytes_that_follow = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4

            # cls_obj = cache.get_class_object(class_object_ID, heap)
            # print(cls_obj)
            # end = cur + number_of_bytes_that_follow
            # c = cur
            # # while c < end:
            # #     pass
            field_values = data[cur:cur + number_of_bytes_that_follow]
            cur += number_of_bytes_that_follow
            INSTANCE_ID_TO_CLASS_DICT[object_ID] = class_object_ID

            ins_obj.object_id = object_ID
            ins_obj.class_object_id = class_object_ID
            ins_obj.instance_field_values = field_values
            heap.instance_objects.append(ins_obj)
        elif type == 0x22:
            obj_array = model.ObjectArray()
            arr_obj_id = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            cur += 4
            number_of_elements = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            arr_class_obj_id = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4

            end = cur + (number_of_elements * 4)
            c = cur
            while c < end:
                v = int.from_bytes(data[c:c + 4], byteorder='big', signed=False)
                c += 4
                obj_array.elements.append(v)

            cur += (number_of_elements * 4)

            obj_array.array_object_id = arr_obj_id
            obj_array.array_class_object_id = arr_class_obj_id
            heap.object_arrays.append(obj_array)
        elif type == 0x23:
            cur += 8
            number_of_elements = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            t = data[cur]
            cur += 1
            cur += (number_of_elements * TYPE_LEN[t])
        else:
            raise RuntimeError(f"unknown type {type}")


def parse(data):
    hprof = model.Hprof()
    hprof.heap = model.Heap()

    cursor = 0
    offset = 0

    # version
    while data[cursor + offset] != 0:
        offset += 1

    name_version = str(data[cursor:cursor + offset], encoding="utf-8")
    hprof.format_and_version = name_version
    cursor = cursor + offset
    offset = 0

    #
    cursor += 1
    offset = 4
    size_of_identifiers = int.from_bytes(data[cursor:cursor + offset], byteorder='big', signed=False)
    hprof.identifier_size = size_of_identifiers
    cursor = cursor + offset
    offset = 0

    # skip
    cursor += 8

    while cursor + offset < len(data):
        tag = data[cursor]
        cursor += 1
        cursor += 4
        p = data[cursor:cursor + 4]
        record_length = int.from_bytes(p, byteorder='big', signed=False)
        cursor += 4

        bo_st = cursor
        bo_len = record_length

        cursor += record_length
        # print(f"{tag} - {record_length}")

        if tag == 0x1c:
            parse_heap_dump_segment_record(data, bo_st, bo_len, hprof.heap)
        elif tag == 0x01:
            parse_string(data, bo_st, bo_len, STR_VALUE_TO_ID_DICT, STR_ID_TO_VALUE_DICT, hprof.strings)
        elif tag == 0x02:
            parse_load_class(data, bo_st, bo_len, CLASS_NAME_TO_ID_DICT, hprof.classes)
        elif tag == 0x0A:
            parse_start_thread(data, bo_st, bo_len)

    return hprof


def _parse_instance_field(hprof):
    for ins_obj in hprof.heap.instance_objects:
        cls_obj = cache.get_class_object(ins_obj.class_object_id, hprof.heap)
        cur = 0
        for ins_field in cls_obj.instance_fields:
            copy_ins_field = model.InstanceField()
            copy_ins_field.field_name_string_id = ins_field.field_name_string_id
            copy_ins_field.type_of_field = ins_field.type_of_field

            if copy_ins_field.type_of_field == model.BasicType_object.type:
                obj_id = int.from_bytes(ins_obj.instance_field_values[cur:cur + model.BasicType_object.size],
                                        byteorder='big', signed=False)
                copy_ins_field.value = obj_id

            cur += cache.get_basic_type(copy_ins_field.type_of_field).size
            ins_obj.fields.append(copy_ins_field)


def get_all_root_objects(hprof):
    root_object_ids = set()

    for r in hprof.heap.root_unknowns:
        root_object_ids.add(r.object_id)
    for r in hprof.heap.root_jni_globals:
        root_object_ids.add(r.object_id)
    for r in hprof.heap.root_jni_locals:
        root_object_ids.add(r.object_id)
    for r in hprof.heap.root_java_frames:
        root_object_ids.add(r.object_id)
    for r in hprof.heap.root_native_stacks:
        root_object_ids.add(r.object_id)
    for r in hprof.heap.root_sticky_classes:
        root_object_ids.add(r.object_id)
    for r in hprof.heap.root_thread_blocks:
        root_object_ids.add(r.object_id)
    for r in hprof.heap.root_monitor_useds:
        root_object_ids.add(r.object_id)

    return root_object_ids


def get_all_using_objects(hprof, root_object_ids):
    # using = []
    visited = set()
    count = 0
    for r in root_object_ids:
        count += 1
        # print(f"scan gc {count}/{len(root_object_ids)} , {len(visited)}")
        # if count % 1000 == 0:
        #     print(f"scan gc {count}/{len(root_object_ids)}")
        # print(r)
        scan_root(hprof, r, visited)
        # using.extend(list(u))

    return visited


def scan_root(hprof, root_object_id, visited):
    # print(f"scan_root {root_object_id}")
    queueing = []
    if root_object_id not in visited:
        queueing.append(root_object_id)

    while queueing:
        object_id = queueing.pop(0)
        # if object_id == 322040032:
        #     print()
        # print(f"{object_id}  {len(queueing)}")
        if object_id in visited:
            print(f"--- ---- --- --- --- wocao already visited {hex(object_id)}")
        visited.add(object_id)
        # print(f"visited {len(visited)}")

        children = get_child_object_ids(hprof, object_id)
        for c in children:
            if c == 0x6f97ff88:
                print(f"meet {c not in visited} {c not in queueing}")
            if c not in visited and c not in queueing:
                if c == 0x6f97ff88:
                    print(f"add {c not in visited} {c not in queueing}")
                queueing.append(c)
            # else:
            # print(f"already visited {hex(c)}")


# def scan_class_object(class_object, hprof):
#     for st_fi in class_object.static_fields:
#         if st_fi.type_of_field == model.BasicType_object.type:
#
#
# def scan_instance_object(instance_object, hprof):
#     pass
#
#
# def scan_object_array_object(class_object, hprof):
#     pass


def get_child_object_ids(hprof, object_id):
    ins_obj = cache.get_instance_object(object_id, hprof.heap)
    child = []

    if ins_obj:
        for ins_field in ins_obj.fields:
            if ins_field.type_of_field == model.BasicType_object.type:
                if is_strong_reference(hprof, ins_field.value):
                    child.append(ins_field.value)
    else:
        cls_obj = cache.get_class_object(object_id, hprof.heap)
        if cls_obj:
            for sta_field in cls_obj.static_fields:
                if sta_field.type_of_field == model.BasicType_object.type:
                    child.append(sta_field.value)
        else:
            object_array_obj = cache.get_object_array_object(object_id, hprof.heap)
            if object_array_obj:
                for e in object_array_obj.elements:
                    child.append(e)

    return list(set(child))


def is_strong_reference(hprof, object_id):
    ins_obj = cache.get_instance_object(object_id, hprof.heap)
    if ins_obj:
        class_object_id = ins_obj.class_object_id
        class_c = cache.get_class_by_class_object_id(class_object_id, hprof)
        string_id = class_c.class_name_string_id
        string_value = cache.get_string_by_id(string_id, hprof).value

        if "Reference" in string_value:
            # print(string_value)
            return False
        elif "java.lang.String" == string_value:
            return False
        else:
            # print(string_value)
            pass

        return True
    else:
        return True


def find_instances(hprof, class_name):
    str_id = cache.get_string_by_value(class_name, hprof).id
    class_object_id = cache.get_class_by_string_id(str_id, hprof).class_object_id
    instance_objects = cache.get_instance_objects_by_class_object_id(class_object_id, hprof.heap)

    if not instance_objects:
        return []

    ids = []
    for ins_obj in instance_objects:
        ids.append(ins_obj.object_id)

    return ids


def check(using, class_name):
    ids = find_instances(h, class_name)
    print("---")
    if not ids:
        print(f"{class_name} not found")
        return
    for id in ids:
        print(hex(id))
        print(f"{class_name} found, is in using ? {id in using}")


def get_all_objects_count(hprof):
    count = 0
    count += len(hprof.heap.class_objects)
    count += len(hprof.heap.instance_objects)
    count += len(hprof.heap.object_arrays)
    return count


if __name__ == '__main__':
    path = "C:\\Users\\huangjinfu\\Desktop\\hp\\h1j.hprof"
    fd = open(path, "rb")
    d = fd.read()
    fd.close()
    h = parse(d)
    print(h)
    _parse_instance_field(h)
    print(h)

    print(f"all objects {get_all_objects_count(h)}")

    root_objects = get_all_root_objects(h)
    print(f"gc roots {len(root_objects)}")

    using = get_all_using_objects(h, root_objects)

    print("--")
    print(len(using))

    # scan_root(h, 315359232)

    # ids = find_instances(h, "com.shanbay.words.setting.SettingActivity")
    # print("---")
    # for id in ids:
    #     print(hex(id))
    #     print(f"is in using ? {id in using}")

    check(using, "com.shanbay.words.startup.SplashActivity")
    check(using, "com.shanbay.biz.account.user.bridge.BayLoginMainActivity")
    check(using, "com.shanbay.biz.account.user.bayuser.login.BayLoginActivity")
    check(using, "com.shanbay.words.startup.InitActivity")
    check(using, "com.shanbay.words.home.thiz.HomeActivity")
    check(using, "com.shanbay.biz.message.center.MessageCenterActivity")
    check(using, "com.shanbay.words.setting.SettingActivity")
    check(using, "com.shanbay.biz.web.activity.ShanbayWebPageActivity")
