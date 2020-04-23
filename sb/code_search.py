import argparse
import os
import shutil
import subprocess

from colorama import Fore, Style

from base import sb_config, sb_gitlab


def get_remote_master_latest_commit(sb_gtlb: sb_gitlab.SBGitlab, project_id):
    return sb_gtlb.get_latest_commit(project_id, 'master')


def get_local_master_latest_commit(project_path):
    """
    获取指定项目本地master的最新提交id
    :param project_path:
    :return:
    """
    old_path = os.getcwd()

    os.chdir(project_path)
    call_git = subprocess.check_output(['git', 'rev-parse', 'master'])
    commit = call_git.decode('utf-8')

    os.chdir(old_path)
    return commit


def clone_project_repo(project):
    subprocess.call(['git', 'clone', '-b', 'master', '--depth', '1', project.http_url_to_repo])


def search(query):
    print(Fore.BLUE + '----- search result---------------------------------------------'
                      '----------------------------------------------------------------'
                      '----------------------------------------------------------------')
    print(Fore.BLUE + '----------------------------------------------------------------'
                      '----------------------------------------------------------------'
                      '----------------------------------------------------------------')
    print(Style.RESET_ALL)
    if query != '':
        subprocess.call(['grep', '-r', '-A', '5', '-B', '5', '-n', '--color=auto', '-E', query, '.'])


def refresh_repo():
    sb_cfg = sb_config.SBConfig()
    sb_gtlb = sb_gitlab.SBGitlab(sb_cfg)
    projects = sb_gtlb.get_projects_by_group(29)

    delete_all_project()

    for p in projects:
        clone_project_repo(p)


def delete_project(project):
    old_path = os.getcwd()

    project_path = os.path.join(old_path, project.name)
    if os.path.exists(project_path):
        shutil.rmtree(project_path)

    os.chdir(old_path)


def delete_all_project():
    project_dirs = os.listdir()
    for project_dir in project_dirs:
        if os.path.isdir(project_dir):
            shutil.rmtree(project_dir)


def get_all_local_projects():
    project_names = []
    project_dirs = os.listdir()
    for project_dir in project_dirs:
        if os.path.isdir(project_dir):
            project_names.append(project_dir)
    return project_names


def get_all_remote_projects():
    sb_cfg = sb_config.SBConfig()
    sb_gtlb = sb_gitlab.SBGitlab(sb_cfg)
    projects = sb_gtlb.get_projects_by_group(29)
    return projects


def get_projects_diff(local_project_name_set: set, remote_project_name_set: set):
    deleted = local_project_name_set.difference(remote_project_name_set)
    newly = remote_project_name_set.difference(local_project_name_set)
    remain = local_project_name_set.intersection(remote_project_name_set)

    return deleted, newly, remain


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
