import re

import gitlab

from base import sb_config


class SBGitlab:
    def __init__(self, sb_config: sb_config.SBConfig):
        self._sb_config = sb_config.config
        self._server = gitlab.Gitlab(url=self._sb_config['gitlab']['server_url'],
                                     private_token=self._sb_config['gitlab']['private_token'])

    def is_app_branch_exist(self, app, branch):
        """
        检测app项目里面是否有指定branch
        :param app:
        :param branch:
        :return: False-没有
        """
        app_info = self._get_app_info(app)

        proj = self._server.projects.get(app_info['project_id'])

        try:
            proj.branches.get(branch)
            return True
        except Exception:
            return False

    def create_app_branch(self, app, branch):
        """
        为app新建工作分支，从master切
        :param app:
        :param branch:
        :return: False-创建失败
        """

        app_info = self._get_app_info(app)

        proj = self._server.projects.get(app_info['project_id'])

        data = {
            'branch': branch,
            'ref': 'master'
        }

        try:
            proj.branches.create(data)
            return True
        except Exception:
            return False

    def update_lib_version(self, branch, lib, lib_version):
        """
        更新库的测试分支版本号为测试专用版本号
        :param branch:
        :param lib:
        :param lib_version:
        :return:失败返回False
        """

        lib_info = self._get_lib_info(lib)

        proj = self._server.projects.get(lib_info['project_id'])
        module = lib_info['module']
        build_file_path = f'{module}/build.gradle'

        old_build_file_content = str(proj.files.get(file_path=build_file_path, ref=branch).decode(), encoding='utf-8')
        version_reg = re.compile('NEXUS_DEPLOY_VERSION.*\".*\"')

        all_match = re.findall(version_reg, old_build_file_content)
        old_version = all_match[0].split('=')[1].strip().replace('"', '')
        if old_version == lib_version:
            return True

        new_build_file_content = re.sub(version_reg, f'NEXUS_DEPLOY_VERSION = "{lib_version}"', old_build_file_content)

        data = {
            'branch': branch,
            'commit_message': 'change version',
            'actions': [
                {
                    'action': 'update',
                    'file_path': build_file_path,
                    'content': new_build_file_content
                }
            ]
        }

        try:
            proj.commits.create(data)
            return True
        except Exception:
            return False

    def get_lib_latest_version(self, lib):
        """
        从lib的master分支获取最新的版本号
        :param lib:
        :return:
        """

        lib_info = self._get_lib_info(lib)

        proj = self._server.projects.get(lib_info['project_id'])
        module = lib_info['module']
        build_file_path = f'{module}/build.gradle'

        build_file_content = str(proj.files.get(file_path=build_file_path, ref='master').decode(), encoding='utf-8')
        version_reg = re.compile('NEXUS_DEPLOY_VERSION.*\".*\"')

        all_match = re.findall(version_reg, build_file_content)
        version = all_match[0].split('=')[1].strip().replace('"', '')

        return version

    def update_app_dependencies(self, branch, app, lib_dict):
        """
        更新要被测试的app的测试分支上，指定库的版本号为测试专用版本号
        :param branch:
        :param app:
        :param lib:
        :param lib_version:
        :return:失败返回False
        """

        if not lib_dict:
            return True

        app_info = self._get_app_info(app)

        proj = self._server.projects.get(app_info['project_id'])
        build_file_path = 'app/build.gradle'
        build_file_content = str(proj.files.get(file_path=build_file_path, ref=branch).decode(), encoding='utf-8')

        lib_force = ''
        lib_version_changed = False
        for lib, lib_version in lib_dict.items():
            lib_info = self._get_lib_info(lib)
            dependency_reg = re.compile(lib_info['group_id'] + ':' + lib + ':.*[\d|local]')

            all_match = re.findall(dependency_reg, build_file_content)
            for m in all_match:
                old_lib_version = m.split(':')[2].strip()
                if old_lib_version != lib_version:
                    lib_version_changed = True
                    break

            new_dependency = lib_info['group_id'] + ':' + lib + ':' + lib_version
            build_file_content = re.sub(dependency_reg, new_dependency, build_file_content)

            lib_force += 'force ' + "'" + new_dependency + "'" + '\n'

        force_start = '//force start'
        force_end = '//force end'
        full_force = force_start + '\n' + '//TODO for test, must be deleted in release\nconfigurations.all { resolutionStrategy { ' + lib_force + ' } }' + '\n' + force_end
        force_reg = re.compile(force_start + '[\s\S]*' + force_end)
        if not re.findall(force_reg, build_file_content):
            build_file_content += '\n'
            build_file_content += full_force

        if not lib_version_changed:
            return True

        data = {
            'branch': branch,
            'commit_message': 'change dependency',
            'actions': [
                {
                    'action': 'update',
                    'file_path': build_file_path,
                    'content': build_file_content
                }
            ]
        }

        try:
            proj.commits.create(data)
            return True
        except Exception:
            return False

    def update_app_dependencies_without_force(self, branch, app, lib_dict):
        """
        更新要被测试的app的测试分支上，指定库的版本号为测试专用版本号
        :param branch:
        :param app:
        :param lib:
        :param lib_version:
        :return:失败返回False
        """

        if not lib_dict:
            return True

        app_info = self._get_app_info(app)

        proj = self._server.projects.get(app_info['project_id'])
        build_file_path = 'app/build.gradle'
        build_file_content = str(proj.files.get(file_path=build_file_path, ref=branch).decode(), encoding='utf-8')

        lib_version_changed = False
        for lib, lib_version in lib_dict.items():
            lib_info = self._get_lib_info(lib)
            dependency_reg = re.compile(lib_info['group_id'] + ':' + lib + ':.*[\d|local]')

            all_match = re.findall(dependency_reg, build_file_content)
            for m in all_match:
                old_lib_version = m.split(':')[2].strip()
                if old_lib_version != lib_version:
                    lib_version_changed = True
                    break

            new_dependency = lib_info['group_id'] + ':' + lib + ':' + lib_version
            build_file_content = re.sub(dependency_reg, new_dependency, build_file_content)

        if not lib_version_changed:
            return True

        data = {
            'branch': branch,
            'commit_message': 'change dependency',
            'actions': [
                {
                    'action': 'update',
                    'file_path': build_file_path,
                    'content': build_file_content
                }
            ]
        }

        try:
            proj.commits.create(data)
            return True
        except Exception:
            return False

    def get_projects_by_group(self, group_id):
        """
        查询给定group下面的所有未归档项目
        :param group_id:
        :return:
        """
        ps = []
        page = 1

        while True:
            r = self._server.groups.get(group_id).projects.list(per_page=100, page=page, archived=False)
            if r:
                ps.extend(r)
                page += 1
            else:
                break

        return ps

    def _get_lib_info(self, lib):
        return self._sb_config['libs'][lib]

    def _get_app_info(self, app):
        return self._sb_config['apps'][app]
