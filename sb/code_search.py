import argparse
import os
import subprocess

from base import sb_config, sb_gitlab


def update_project_repo(project):
    old_path = os.getcwd()

    project_path = os.path.join(old_path, project.name)
    if os.path.isdir(project_path):
        os.chdir(project_path)
        subprocess.call(['git', 'pull', 'origin', 'master', '--depth', '1'])
    else:
        subprocess.call(['git', 'clone', '-b', 'master', '--depth', '1', project.http_url_to_repo])

    os.chdir(old_path)


def search(query):
    if query != '':
        subprocess.call(['grep', '-r', '-A', '5', '-B', '5', '-n', '--color=auto', '-E', query, '.'])


def refresh_repo():
    sb_cfg = sb_config.SBConfig()
    sb_gtlb = sb_gitlab.SBGitlab(sb_cfg)
    projects = sb_gtlb.get_projects_by_group(29)

    for p in projects:
        update_project_repo(p)


def main(refresh, query):
    root_path = '/Users/huangjinfu/work/codesearch/'
    os.chdir(root_path)

    if refresh:
        refresh_repo()

    search(query)


def get_cli_args():
    parser = argparse.ArgumentParser(description='代码搜索工具，hound本地替代版')

    parser.add_argument('-r', action='store_true', default=False, help='获取最新master分支代码')
    parser.add_argument('query', default='', type=str, help='要查找的内容，支持正则，使用单引号包裹')

    return parser.parse_args()


if __name__ == '__main__':
    args = get_cli_args()
    main(args.r, args.query)
