"""
一键编译测试版本的app给qa：
1、改库版本号为测试版本号
2、改app的库依赖为测试版本号依赖
3、编库
4、编app
"""

import json
import sys

import sb_config
import sb_gitlab
import sb_jenkins
import sb_nexus


def main():
    task_file = sys.argv[1]
    task = json.load(open(task_file))

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
            return
        lib_version_dict[lib] = lib_test_version

    print('update lib version:')
    for lib, version in lib_version_dict.items():
        r = sb_gtlb.update_lib_version(branch, lib, lib_test_version)
        print(f'    {lib} -> {r}')
        if not r:
            return

    print('update app dependencies:')
    for app in apps:
        r = sb_gtlb.update_app_dependencies(branch, app, lib_version_dict)
        print(f'    {app} -> {r}')
        if not r:
            return

    print('build test lib:')
    for lib in libs:
        r = sb_jks.build_test_lib(lib, branch, release_note)
        print(f'    {lib} -> {r}')
        if not r:
            return

    print('build test app:')
    for app in apps:
        r = sb_jks.build_test_app(app, branch, release_note)
        print(f'    {app} -> {r}')
        if not r:
            return


if __name__ == '__main__':
    main()
