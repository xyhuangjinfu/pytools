import typing


class _Class:
    def __init__(self):
        self.class_object_id = None
        self.name = None
        self.super = None


class _Object:
    def __init__(self):
        self.id = None
        self.type = None
        self.parents: typing.List[_Field] = []


class _Field:
    def __init__(self):
        self.name = None
        self.value: _Object = None


class Node:
    def __init__(self):
        self.class_name = None
        self.field_name = None
        self.pre = None
        self.value = Node


class LeakDetector:
    def __init__(self, hprof):
        self._object_dict = {}
        self._class_object_dict = {}
        self._instance_object_dict = {}
        self._object_array_dict = {}
        self._string_dict = {}
        self._class_name_dict = {}
        self._class_dict = {}
        self._class_dict_name = {}
        self._roots = set()
        self._class_instance_object_list_dict = {}
        self._init(hprof)

    def _init(self, hprof):
        for r in hprof.heap.root_unknowns:
            self._roots.add(r.object_id)
        for r in hprof.heap.root_jni_globals:
            self._roots.add(r.object_id)
        for r in hprof.heap.root_jni_locals:
            self._roots.add(r.object_id)
        for r in hprof.heap.root_java_frames:
            self._roots.add(r.object_id)
        for r in hprof.heap.root_native_stacks:
            self._roots.add(r.object_id)
        for r in hprof.heap.root_sticky_classes:
            self._roots.add(r.object_id)
        for r in hprof.heap.root_thread_blocks:
            self._roots.add(r.object_id)
        for r in hprof.heap.root_monitor_useds:
            self._roots.add(r.object_id)
        for r in hprof.heap.root_thread_objects:
            self._roots.add(r.thread_object_id)

        for s in hprof.strings:
            self._string_dict[s.id] = s.value

        for klass in hprof.classes:
            c = _Class()
            c.class_object_id = klass.class_object_id
            c.name = klass.class_name
            self._class_dict[c.class_object_id] = c
            self._class_dict_name[c.name] = c

        for klass in hprof.classes:
            self._class_name_dict[klass.class_object_id] = klass.class_name

        for obj in hprof.heap.instance_objects:
            o = _Object()
            o.id = obj.object_id
            o.type = self._class_name_dict[obj.class_object_id]
            self._instance_object_dict[obj.object_id] = o
            self._object_dict[obj.object_id] = o

            klass = self._class_dict[obj.class_object_id]
            if obj.class_object_id in self._class_instance_object_list_dict:
                self._class_instance_object_list_dict[klass.name].append(o)
            else:
                self._class_instance_object_list_dict[klass.name] = [o]

        for obj in hprof.heap.class_objects:
            o = _Object()
            o.id = obj.class_object_id
            o.type = self._class_name_dict[obj.class_object_id]
            self._class_object_dict[obj.class_object_id] = o
            self._object_dict[obj.class_object_id] = o

        for obj in hprof.heap.object_arrays:
            o = _Object()
            o.id = obj.array_object_id
            o.type = self._class_name_dict[obj.array_class_object_id]
            self._object_array_dict[obj.array_object_id] = o
            self._object_dict[obj.array_object_id] = o

        for cls_obj in hprof.heap.class_objects:
            class_object_id = cls_obj.class_object_id
            super_class_object_id = cls_obj.super_class_object_id
            if super_class_object_id != 0:
                self._class_dict[class_object_id].super = self._class_dict[super_class_object_id]

        for obj in hprof.heap.instance_objects:
            obj_this = self._object_dict[obj.object_id]
            for ins_field in obj.fields:
                if ins_field.value and ins_field.value in self._object_dict:
                    obj_child = self._object_dict[ins_field.value]

                    fie = _Field()
                    fie.name = ins_field.field_name
                    fie.value = obj_this
                    obj_child.parents.append(fie)

        for obj in hprof.heap.class_objects:
            obj_this = self._object_dict[obj.class_object_id]
            for sta_field in obj.static_fields:
                if sta_field.value and sta_field.value in self._object_dict:
                    obj_child = self._object_dict[sta_field.value]

                    fie = _Field()
                    fie.name = sta_field.field_name
                    fie.value = obj_this
                    obj_child.parents.append(fie)

        for obj in hprof.heap.object_arrays:
            obj_this = self._object_dict[obj.array_object_id]
            for ele in obj.elements:
                if ele and ele in self._object_dict:
                    obj_child = self._object_dict[ele]

                    fie = _Field()
                    fie.name = ""
                    fie.value = obj_this
                    obj_child.parents.append(fie)

    def _is_type(self, type_class_name, class_name):
        cls = self._class_dict_name[class_name]
        while cls:
            if cls.name == type_class_name:
                return True
            cls = cls.super

        return False

    def _search(self, check_instance_dict):
        leaks = []
        nodes = []
        for obj_id, class_name in check_instance_dict.items():
            is_leak, node = self._search_single(obj_id)
            if is_leak:
                leaks.append(class_name)
                nodes.append(node)
        return leaks, nodes

    def _search_single(self, object_id):
        start_object = self._object_dict[object_id]
        queueing = [start_object]
        visited = set()

        node_dict = {}

        n = Node()
        n.class_name = start_object.type
        n.field_name = None
        n.pre = None
        n.value = start_object.id
        node_dict[start_object.id] = n

        while queueing:
            obj = queueing.pop(0)
            visited.add(obj)

            if obj.id in self._roots:
                return True, node_dict[obj.id]
                break

            for f in obj.parents:
                if f.value not in queueing \
                        and f.value not in visited \
                        and not self._is_type("java.lang.ref.Reference", f.value.type):
                    queueing.append(f.value)

                    n = Node()
                    n.class_name = f.value.type
                    n.field_name = f.name
                    n.value = f.value.id
                    n.pre = node_dict[obj.id]
                    node_dict[f.value.id] = n

        return False, None

    def _get_check_class_name_list(self):
        return self._get_all_activities()

    def _get_all_activities(self):
        activity_set = set()
        for class_name, klass in self._class_dict_name.items():
            if self._is_type("android.app.Activity", class_name):
                activity_set.add(class_name)
        return activity_set

    def _find_instances_dict(self, class_name):
        if class_name not in self._class_instance_object_list_dict:
            return {}

        instance_objects = self._class_instance_object_list_dict[class_name]

        if not instance_objects:
            return {}

        ids_dict = {}
        for ins_obj in instance_objects:
            ids_dict[ins_obj.id] = class_name

        return ids_dict

    def detect(self):
        check_list = self._get_check_class_name_list()

        check_class_instances_dict = {}

        for class_name in check_list:
            check_class_instances_dict.update(self._find_instances_dict(class_name))

        leak_list, reference_links = self._search(check_class_instances_dict)

        return leak_list, reference_links
