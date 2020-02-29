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
    print('apps: ' + str(task['apps']))
    print('libs: ' + str(task['libs']))
    print('branch: ' + task['branch'])
    print('release_note: ' + task['release_note'])


def main():
    task_file = sys.argv[1]
    task = json.load(open(task_file))

    _print_task(task)
    execute = input('确认参数正确，继续执行？（y/n）')
    if execute != 'y':
        return

    apps = task['apps']
    libs = task['libs']
    branch = task['branch']
    release_note = task['release_note']

    sb_cfg = sb_config.SBConfig()
    sb_nxs = sb_nexus.SBNexus(sb_cfg)
    sb_gtlb = sb_gitlab.SBGitlab(sb_cfg)
    sb_jks = sb_jenkins.SBJenkins(sb_cfg)

    lib_version_dict = {}
    print('get lib test version:')
    for lib in libs:
        lib_test_version = sb_nxs.get_next_lib_version(lib)
        print(f'    {lib} -> {lib_test_version}')
        if lib_test_version is None:
            print(f'    get {lib} test version fail')
            return
        lib_version_dict[lib] = lib_test_version

    print('update lib version:')
    for lib, version in lib_version_dict.items():
        r = sb_gtlb.update_lib_version(branch, lib, lib_test_version)
        print(f'    {lib} -> {r}')
        if not r:
            print(f'    update {lib} version fail')
            return

    print('check app work branch:')
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
                return

    print('update app dependencies:')
    for app in apps:
        r = sb_gtlb.update_app_dependencies(branch, app, lib_version_dict)
        print(f'    {app} -> {r}')
        if not r:
            print(f'    update {app} dependencies fail')
            return

    print('build test lib:')
    for lib in libs:
        r = sb_jks.build_test_lib(lib, branch, release_note)
        print(f'    {lib} -> {r}')
        if not r:
            print(f'    build {lib} fail')
            return

    print('build test app:')
    for app in apps:
        r = sb_jks.build_test_app(app, branch, release_note)
        print(f'    {app} -> {r}')
        if not r:
            print(f'    build {app} fail')
            return


if __name__ == '__main__':
    main()
