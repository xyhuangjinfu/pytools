"""
一键编译测试版本的app给qa：
1、改库版本号为测试版本号
2、改app的库依赖为测试版本号依赖
3、编库
4、编app
"""

import json
import sys

from base import sb_nexus, sb_jenkins, sb_config, sb_gitlab


def _print_task(task):
    print(f'apps: {str(task["apps"])}')
    print(f'libs: {str(task["libs"])}')
    print(f'branch: {task["branch"]}')
    print(f'release_note: {task["release_note"]}')
    print(f'rebuild_lib: {task["rebuild_lib"]}')


def get_lib_test_version(sb_nxs, libs, rebuild_lib):
    """
    获取所有库的测试版本号（-test-username-version）
    :param sb_nxs:
    :param libs:
    :param rebuild_lib: True-重新升版本号，编译。False-使用已有的包。
    :return:
    """
    print(f'get lib test version: {len(libs)}')
    lib_version_dict = {}
    for lib in libs:
        lib_test_version = sb_nxs.get_next_lib_version(lib, rebuild_lib)
        print(f'    {lib} -> {lib_test_version}')
        if lib_test_version is None:
            print(f'    get {lib} test version fail')
            return None
        lib_version_dict[lib] = lib_test_version
    return lib_version_dict


def update_lib_version(sb_gtlb, branch, lib_version_dict, rebuild_lib):
    """
    在库的指定分支上更新版本号
    :param sb_gtlb:
    :param branch:
    :param lib_version_dict:
    :param rebuild_lib:
    :return:
    """
    print(f'update lib version: {len(lib_version_dict)}')
    if rebuild_lib:
        for lib, version in lib_version_dict.items():
            r = sb_gtlb.update_lib_version(branch, lib, version)
            print(f'    {lib} -> {r}')
            if not r:
                print(f'    update {lib} version fail')
                return False
    else:
        print(f'    not rebuild libs')
    return True


def check_app_work_branch(sb_gtlb, apps, branch):
    """
    检测app上面是否存在工作分支，不存在就创建
    :param apps:
    :param branch:
    :return:
    """
    print(f'check app work branch: {len(apps)}')
    for app in apps:
        exist = sb_gtlb.is_app_branch_exist(app, branch)
        if exist:
            print(f'    {app} -> exist')
        else:
            create = sb_gtlb.create_app_branch(app, branch)

            if create:
                print(f'    {app} -> create')
            else:
                print(f'    create branch {branch} for {app} fail')
                return False
    return True


def update_app_dependencies(sb_gtlb, apps, branch, lib_version_dict):
    """
    在app的工作分支上更新库的版本号为测试版本号
    :param sb_gtlb:
    :param apps:
    :return:
    """
    print(f'update app dependencies: {len(apps)}')
    for app in apps:
        r = sb_gtlb.update_app_dependencies(branch, app, lib_version_dict)
        print(f'    {app} -> {r}')
        if not r:
            print(f'    update {app} dependencies fail')
            return False
    return True


def build_test_lib(sb_jks, libs, rebuild_lib, branch, release_note):
    """
    编译测试的库
    :param sb_jks:
    :param libs:
    :param rebuild_lib:
    :param branch:
    :param release_note:
    :return:
    """
    print(f'build test lib: {len(libs)}')
    if rebuild_lib:
        for lib in libs:
            r = sb_jks.build_test_lib(lib, branch, release_note)
            print(f'    {lib} -> {r}')
            if not r:
                print(f'    build {lib} fail')
                return False
    else:
        print(f'    not rebuild libs')
    return True


def build_test_app(sb_jks, apps, branch, release_note):
    """
    编译测试app
    :return:
    """
    print(f'build test app: {len(apps)}')
    for app in apps:
        r = sb_jks.build_test_app(app, branch, release_note)
        print(f'    {app} -> {r}')
        if not r:
            print(f'    build {app} fail')
            return False
    return True


def main():
    task_file = sys.argv[1]
    task = json.load(open(task_file))

    _print_task(task)
    execute = input('确认参数正确，继续执行？（y/n）')
    if execute != 'y':
        return 1

    apps = task['apps']
    libs = task['libs']
    branch = task['branch']
    release_note = task['release_note']
    rebuild_lib = task['rebuild_lib']

    sb_cfg = sb_config.SBConfig()
    sb_nxs = sb_nexus.SBNexus(sb_cfg)
    sb_gtlb = sb_gitlab.SBGitlab(sb_cfg)
    sb_jks = sb_jenkins.SBJenkins(sb_cfg)

    lib_version_dict = get_lib_test_version(sb_nxs, libs, rebuild_lib)
    if not lib_version_dict:
        return 2

    ulv = update_lib_version(sb_gtlb, branch, lib_version_dict, rebuild_lib)
    if not ulv:
        return 3

    cawb = check_app_work_branch(sb_gtlb, apps, branch)
    if not cawb:
        return 4

    uad = update_app_dependencies(sb_gtlb, apps, branch, lib_version_dict)
    if not uad:
        return 5

    btl = build_test_lib(sb_jks, lib_version_dict, rebuild_lib, branch, release_note)
    if not btl:
        return 6

    bta = build_test_app(sb_jks, apps, branch, release_note)
    if not bta:
        return 7

    return 0


if __name__ == '__main__':
    main()
