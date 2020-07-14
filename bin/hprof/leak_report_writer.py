def write(file_path, node_list):
    if not node_list:
        return

    for n in node_list:
        no = n
        que = []
        while no:
            que.append(no)
            no = no.pre

    fd = open(file_path, "a+")

    for n in node_list:
        no = n
        deep = 0
        fd.write(
            "-------------------------------------------------------------------------------------------------------------------------\n")
        while no:
            indent = "    " * deep
            if no.class_name:
                if no.field_name:
                    fd.write(f"{indent}{no.class_name}  {no.field_name}\n")
                else:
                    fd.write(f"{indent}{no.class_name}\n")
            no = no.pre
            deep += 1

    fd.close()


def write_reverse(file_path, node_list):
    if not node_list:
        return

    fd = open(file_path, "a+")

    for n in node_list:
        no = n
        que = []
        while no:
            que.append(no)
            no = no.pre

        no = que.pop(len(que) - 1)
        deep = 0
        fd.write(
                "-------------------------------------------------------------------------------------------------------------------------\n")
        while no:
            indent = "    " * deep
            if no.class_name:
                if no.field_name:
                    fd.write(f"{indent}{no.class_name}  {no.field_name}  {hex(no.value)}\n")
                else:
                    fd.write(f"{indent}{no.class_name}  {hex(no.value)}\n")
            if que:
                no = que.pop(len(que) - 1)
            else:
                no = None
            deep += 1

    fd.close()


def print_console(node_list):
    if not node_list:
        return

    for n in node_list:
        no = n
        deep = 0
        print(
            "-------------------------------------------------------------------------------------------------------------------------\n",
            end="")
        while no:
            indent = "    " * deep
            if no.class_name:
                if no.field_name:
                    print(f"{indent}{no.class_name} -> {no.field_name}\n", end="")
                else:
                    print(f"{indent}{no.class_name}\n", end="")
            no = no.pre
            deep += 1


def print_console_reverse(node_list):
    if not node_list:
        return

    for n in node_list:
        no = n
        que = []
        while no:
            que.append(no)
            no = no.pre

        no = que.pop(len(que) - 1)
        deep = 0
        print(
            "-------------------------------------------------------------------------------------------------------------------------\n",
            end="")
        while no:
            indent = "    " * deep
            if no.class_name:
                if no.field_name:
                    print(f"{indent}{no.class_name} -> {no.field_name}  {hex(no.value)}\n", end="")
                else:
                    print(f"{indent}{no.class_name}  {hex(no.value)}\n", end="")
            if que:
                no = que.pop(len(que) - 1)
            else:
                no = None
            deep += 1
