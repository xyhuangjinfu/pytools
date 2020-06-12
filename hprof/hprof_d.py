# http://hg.openjdk.java.net/jdk6/jdk6/jdk/raw-file/tip/src/share/demo/jvmti/hprof/manual.html
path = "/Users/huangjinfu/Downloads/hpr/h1j.hprof"

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


def parse_load_class(data, body_start, body_len, name_to_id_dict):
    cur = body_start
    cur += 4
    class_object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
    cur += 4
    cur += 4
    class_name_string_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
    name_to_id_dict[class_name_string_ID] = class_object_ID
    CLASS_ID_TO_NAME_DICT[class_object_ID] = class_name_string_ID


# str 4216398 com.shanbay.words.home.thiz.HomeActivity
# class 318339368 4216398
# 4196292 com.shanbay.words.startup.SplashActivity
# class 315441912 4196292
# class ‭321121368 4196292
def parse_string(data, body_start, body_len, value_to_id_dict, id_to_value_dict):
    # print(f"parse_string {body_start} {body_len} , {len(data)}")
    cur = body_start
    ID_for_this_string = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
    cur += 4
    l = body_len - 4
    s = str(data[cur:cur + l], encoding="utf-8")

    value_to_id_dict[s] = ID_for_this_string
    id_to_value_dict[ID_for_this_string] = s

    if "com.shanbay" in s:
        print(f"{ID_for_this_string} {s}")


def parse_heap_dump_segment_record(data, body_start, body_len):
    # print(f"parse_heap_dump_segment_record {body_start} {body_len} , {len(data)}")
    cur = body_start
    offs = 0

    while cur + offs < body_start + body_len:
        type = data[cur]
        cur += 1
        if type == 0xFF:
            objid = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            # print(f"{hex(type)} ROOT UNKNOWN {objid}")
        elif type == 0x01:
            object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            JNI_global_ref_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            # if object_ID == 316467800:
            #     print(f"{hex(type)} ROOT JNI GLOBAL {object_ID}, {JNI_global_ref_ID}")
        elif type == 0x02:
            cur += 12
        elif type == 0x03:
            cur += 4
            object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 8
            # print(f"{hex(type)} ROOT JAVA FRAME {object_ID}")
        elif type == 0x04:
            cur += 8
        elif type == 0x05:
            cur += 4
        elif type == 0x06:
            cur += 8
        elif type == 0x07:
            cur += 4
        elif type == 0x08:
            thread_object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big',
                                              signed=False)
            # print(f"ROOT THREAD OBJECT {hex(thread_object_ID)}")
            cur += 4
            cur += 8
        elif type == 0x20:  # CLASS DUMP
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
                cur += 4
                t = data[cur]
                cur += 1
                cur += TYPE_LEN[t]

            Number_of_instance_fields = int.from_bytes(data[cur:cur + 2], byteorder='big', signed=False)
            cur += 2

            i = 0
            while i < Number_of_instance_fields:
                i += 1
                # cur += 5

                if class_object_ID == 316469984:
                    field_name_string_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
                    cur += 4
                    type_of_field = data[cur]
                    cur += 1
                    # print(f"{STR_ID_TO_VALUE_DICT[field_name_string_ID]}  {TYPE_NAME[type_of_field]}")
                    # print(f"{TYPE_NAME[type_of_field]}")
                else:
                    cur += 5



        elif type == 0x21:  # INSTANCE DUMP
            object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            # if object_ID == 0x13895dc0:
            #     print(f"---------------------------------------- {hex(object_ID)}")
            INSTANCE_ID.append(object_ID)
            # if object_ID == 316467800:
            #     print(f"----------------------------------------{316467800 in INSTANCE_ID}")
            cur += 4
            cur += 4
            class_object_ID = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            INSTANCE_CLASS_OBJECT_ID.append(class_object_ID)
            if class_object_ID == 0x1311ced0:
                print(hex(object_ID))
            cur += 4
            number_of_bytes_that_follow = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            cur += number_of_bytes_that_follow
            INSTANCE_ID_TO_CLASS_DICT[object_ID] = class_object_ID
        elif type == 0x22:
            cur += 8
            number_of_elements = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            cur += 4
            cur += (number_of_elements * 4)
        elif type == 0x23:
            cur += 8
            number_of_elements = int.from_bytes(data[cur:cur + 4], byteorder='big', signed=False)
            cur += 4
            t = data[cur]
            cur += 1
            cur += (number_of_elements * TYPE_LEN[t])
        else:
            raise RuntimeError(f"unknown type {type}")


fd = open(path, "rb")
content = fd.read()
fd.close()

# parse_heap_dump_segment_record(content, 5484314, 4264)


cursor = 0
offset = 0

# version
while content[cursor + offset] != 0:
    offset += 1

version = str(content[cursor:cursor + offset], encoding="utf-8")
cursor = cursor + offset
offset = 0

#
cursor += 1
offset = 4
size_of_identifiers = int.from_bytes(content[cursor:cursor + offset], byteorder='big', signed=False)
cursor = cursor + offset
offset = 0

# skip
cursor += 8

while cursor + offset < len(content):
    tag = content[cursor]
    cursor += 1
    cursor += 4
    p = content[cursor:cursor + 4]
    record_length = int.from_bytes(p, byteorder='big', signed=False)
    cursor += 4

    bo_st = cursor
    bo_len = record_length

    cursor += record_length
    # print(f"{tag} - {record_length}")

    if tag == 0x1c:
        parse_heap_dump_segment_record(content, bo_st, bo_len)
    elif tag == 0x01:
        parse_string(content, bo_st, bo_len, STR_VALUE_TO_ID_DICT, STR_ID_TO_VALUE_DICT)
    elif tag == 0x02:
        parse_load_class(content, bo_st, bo_len, CLASS_NAME_TO_ID_DICT)
    elif tag == 0x0A:
        # print("parse_start_thread")
        parse_start_thread(content, bo_st, bo_len)


# print(CLASS_NAME_TO_ID_DICT[4196292])


def get_class_object_id(class_name):
    return CLASS_NAME_TO_ID_DICT[STR_VALUE_TO_ID_DICT[class_name]]


def find_instance(class_name):
    # 4217296 com.shanbay.biz.web.activity.ShanbayWebPageActivity
    # 4203986 com.shanbay.biz.web.activity.ShanbayWebPageActivity$1
    # 4203987 com.shanbay.biz.web.activity.ShanbayWebPageActivity$2
    # 4225504 com.shanbay.biz.web.activity.ShanbayWebPageActivity$FullscreenHolder
    str_id = STR_VALUE_TO_ID_DICT[class_name]
    class_object_id = CLASS_NAME_TO_ID_DICT[str_id]
    print(f"class_object_id {hex(class_object_id)}")
    found = class_object_id in INSTANCE_CLASS_OBJECT_ID
    print(f"find instance {class_name} - {found}")


print("---")
# print(get_class_object_id("com.shanbay.words.home.thiz.HomeActivity"))
# print(get_class_object_id("com.shanbay.words.startup.SplashActivity"))
# print(get_class_object_id("com.shanbay.words.startup.InitActivity"))
# print(len(INSTANCE_ID))
# print(314651808 in INSTANCE_ID)
# print(THREAD_ID_TO_NAME_DICT[0x12c13570])
# print(STR_ID_TO_VALUE_DICT[THREAD_ID_TO_NAME_DICT[0x12c13570]])
# print(STR_ID_TO_VALUE_DICT[CLASS_ID_TO_NAME_DICT[INSTANCE_ID_TO_CLASS_DICT[0x12c13570]]])

# find_instance("com.shanbay.words.startup.SplashActivity")
# find_instance("com.shanbay.biz.account.user.bridge.BayLoginMainActivity")
# find_instance("com.shanbay.biz.account.user.bayuser.login.BayLoginActivity")
# find_instance("com.shanbay.words.startup.InitActivity")
# find_instance("com.shanbay.words.home.thiz.HomeActivity")
# find_instance("com.shanbay.biz.message.center.MessageCenterActivity")
# find_instance("com.shanbay.words.setting.SettingActivity")
find_instance("com.shanbay.biz.web.activity.ShanbayWebPageActivity")
# find_instance("")
# find_instance("")
