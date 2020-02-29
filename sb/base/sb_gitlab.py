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

    def update_app_dependencies(self, branch, app, lib_dict):
        """
        更新要被测试的app的测试分支上，指定库的版本号为测试专用版本号
        :param branch:
        :param app:
        :param lib:
        :param lib_version:
        :return:失败返回False
        """

        app_info = self._get_app_info(app)

        proj = self._server.projects.get(app_info['project_id'])
        build_file_path = 'app/build.gradle'
        old_build_file_content = str(proj.files.get(file_path=build_file_path, ref=branch).decode(), encoding='utf-8')

        lib_force = ''
        for lib, lib_version in lib_dict.items():
            lib_info = self._get_lib_info(lib)
            dependency_reg = re.compile(lib_info['group_id'] + ':' + lib + ':.*[\d|local]')
            new_dependency = lib_info['group_id'] + ':' + lib + ':' + lib_version
            new_build_file_content = re.sub(dependency_reg, new_dependency, old_build_file_content)

            lib_force += 'force ' + "'" + new_dependency + "'" + '\n'

        force_start = '//force start'
        force_end = '//force end'
        full_force = force_start + '\n' + '//TODO for test, must be deleted in release\nconfigurations.all { resolutionStrategy { ' + lib_force + ' } }' + '\n' + force_end
        force_reg = re.compile(force_start + '[\s\S]*' + force_end)
        if re.findall(force_reg, new_build_file_content):
            new_build_file_content = re.sub(force_reg, full_force, new_build_file_content)
        else:
            new_build_file_content += '\n'
            new_build_file_content += full_force

        data = {
            'branch': branch,
            'commit_message': 'change dependency',
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

    def _get_lib_info(self, lib):
        return self._sb_config['libs'][lib]

    def _get_app_info(self, app):
        return self._sb_config['apps'][app]
