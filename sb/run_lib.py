import os
import re
import subprocess
import sys

from base import sb_config

sb_cfg = sb_config.SBConfig().config


def change_lib_version(lib_path):
    """
    修改lib版本号为local格式的版本号，输出格式为"0.0.0.0-local_version-local"
    :param lib_path:
    :return:
    """
    build_file_path = lib_path + '/build.gradle'
    fp = open(build_file_path, 'r+')
    content = fp.read()

    version_reg = re.compile('NEXUS_DEPLOY_VERSION = \".*\"')
    old_version = str.split(version_reg.findall(content)[0], ' = ')[1].replace('"', '')

    if old_version.endswith('-local'):  # 0.0.0.0-[everything]-local_version-local
        seg = old_version.split('-')
        local_version = seg[len(seg) - 2]
        new_version = seg[0] + '-' + str(int(local_version) + 1) + '-' + 'local'
    else:  # 0.0.0.0-[everything]
        pure_version = old_version.split('-')[0]
        seg = pure_version.split('.')
        lib_version = seg[2]
        new_version = seg[0] + '.' + seg[1] + '.' + str(int(lib_version) + 1) + '.' + seg[3] + '-1-local'

    content = content.replace(old_version, new_version)

    fp.seek(0)
    fp.truncate()
    fp.write(content)

    fp.close()

    return new_version


def change_app_dependency(app_path, lib_name, new_lib_version):
    """
    让app使用最新的lib版本号
    :param app_path:
    :param lib_name:
    :param new_lib_version:
    :return:
    """
    app_build_file = app_path + '/build.gradle'
    fp = open(app_build_file, 'r+')
    content = fp.read()

    new_dependency = lib_name + ':' + new_lib_version

    dependency_reg = re.compile(lib_name + ':.*[\d|local]')

    content = re.sub(dependency_reg, new_dependency, content)

    fp.seek(0)
    fp.truncate()
    fp.write(content)
    fp.close()


def upload_lib(lib_path):
    """
    打包lib，上传到本地maven仓库
    :param lib_path:
    :return: 0-success, 1-fail
    """
    os.chdir(lib_path)

    error = subprocess.call(['../gradlew', 'clean'])
    if error != 0:
        return error

    error = subprocess.call(['../gradlew', 'uploadArchives'])
    if error != 0:
        return error

    return 0


def build_app(app_path):
    """
    编译app
    :param app_path:
    :return:
    """
    os.chdir(app_path)
    subprocess.call(['../gradlew', 'clean'])
    error = subprocess.call(['../gradlew', 'assembleStableDebug'])
    if error == 0:
        return app_path + '/build/outputs/apk/stable/debug/app-stable-debug.apk'
    else:
        return None


def install_app(apk_path):
    """
    安装app
    :param apk_path:
    :return:0-success, 1-fail
    """
    error = subprocess.call(['adb', 'install', '-r', '-d', apk_path])
    return error


def launch_app(app_id, app_main_activity):
    """
    启动app
    :param app_id:
    :param app_main_activity:
    :return:
    """
    subprocess.call(['adb', 'shell', 'am', 'force-stop', app_id])
    subprocess.call(['adb', 'shell', 'am', 'start', '-n', app_id + '/' + app_main_activity])


def check_device():
    """
    检测是否只有一个设备连接在adb上
    adb devices | awk 'END {print NR}'
    :return:
    """
    call_adb = subprocess.Popen(['adb', 'devices'], stdout=subprocess.PIPE)
    call_awk = subprocess.check_output(['awk', 'END {print NR}'], stdin=call_adb.stdout)
    devices_count = int(call_awk.decode('utf-8')) - 2
    return devices_count == 1


def main():
    if not check_device():
        print('device connection error')
        return

    app_name = sys.argv[1]
    lib_names = sys.argv[2:]

    app_info = sb_cfg['apps'][app_name]
    for l in lib_names:
        l_info = sb_cfg['libs'][l]
        new_lib_version = change_lib_version(l_info['local_path'] + l_info['module'])
        change_app_dependency(app_info['local_path'] + 'app', l_info['group_id'] + ':' + l, new_lib_version)
        error = upload_lib(l_info['local_path'] + l_info['module'])
        if error != 0:
            return

    apk_path = build_app(app_info['local_path'] + 'app')
    if apk_path:
        error = install_app(apk_path)
        if error == 0:
            launch_app(app_info['id'], app_info['main_activity'])


if __name__ == '__main__':
    main()
