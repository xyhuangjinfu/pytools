import argparse

from base import sb_config, sb_jenkins


def build_lib(jks, arg):
    if 'debug' == arg.build_type:
        build_param = jks.create_build_lib_param(arg.lib, arg.branch, arg.release_note, True)
    else:
        build_param = jks.create_build_lib_param(arg.lib, arg.branch, arg.release_note, False)
    return jks.build_lib(build_param)


def get_cli_args():
    parser = argparse.ArgumentParser(description='Jenkins 本地工具')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', dest='app', action='store', default='', help='app code')
    group.add_argument('-l', dest='lib', action='store', default='', help='lib code')

    parser.add_argument('-bt', dest='build_type', action='store', default='debug', choices=['debug', 'release'],
                        help='BuildType, release 或者 debug, 默认 debug')
    parser.add_argument('-b', dest='branch', action='store', default='', required=True, help='branch')
    parser.add_argument('-r', dest='release_note', action='store', default='', required=True, type=str,
                        help='release note')

    return parser.parse_args()


if __name__ == '__main__':
    args = get_cli_args()

    sb_cfg = sb_config.SBConfig()
    sb_jks = sb_jenkins.SBJenkins(sb_cfg)

    if args.app:
        pass
    else:
        result = build_lib(sb_jks, args)
        print(f"build lib {'success' if result else 'failure'}")
