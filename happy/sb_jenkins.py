import time

import jenkins

import sb_config


class SBJenkins:
    def __init__(self, sb_config: sb_config.SBConfig):
        self._sb_config = sb_config.config
        self._server = jenkins.Jenkins(self._sb_config['jenkins']['server_url'],
                                       username=self._sb_config['jenkins']['username'],
                                       password=self._sb_config['jenkins']['password'])

    def build_test_app(self, app, branch, release_note):
        """
        编译测试版本app
        :param jks_server: jenkins服务器
        :param app: app名
        :param branch: 分支名
        :param release_note: changelog
        :return: 失败返回False
        """

        app_job_name = 'android-uranus-system/pipeline-app-build'
        queue_item_number = self._server.build_job(app_job_name,
                                                   parameters={'BuildProject': f'{app}',
                                                               'BuildBranch': f'{branch}',
                                                               'MailAddress': 'android@shanbay.com,qa@shanbay.com',
                                                               'MultiChannel': False,
                                                               'CreateTag': False,
                                                               'MergeToMaster': False,
                                                               'PrivateToken':
                                                                   self._sb_config['gitlab']['private_token'],
                                                               'ReleaseNote': f'{release_note}',
                                                               'BizBuild': True,
                                                               'Flavor': 'qa'})
        queue_item = self._server.get_queue_item(queue_item_number)
        build_number = queue_item['executable']['number']

        while True:
            time.sleep(30)
            build_info = self._server.get_build_info(name=app_job_name, number=build_number)
            if not build_info['building']:
                if build_info['result'] == 'SUCCESS':
                    return True
                else:
                    return False

    def build_test_lib(self, lib, branch, release_note):
        """
        编译测试版本lib
        :param jks_server: jenkins服务器
        :param lib: lib名
        :param branch: 分支名
        :param release_note: changelog
        :return: 失败返回False
        """

        lib_info = self._sb_config['libs'][lib]

        lib_job_name = 'Quark-Lib-Build'
        queue_item_number = self._server.build_job(lib_job_name,
                                                   parameters={'BuildGit': lib_info['git'],
                                                               'BuildBranch': f'{branch}',
                                                               'MailAddress': 'jinfu.huang@shanbay.com',
                                                               'ReleaseNote': f'{release_note}',
                                                               'CreateTag': False,
                                                               'PrivateToken':
                                                                   self._sb_config['gitlab']['private_token'],
                                                               'BuildModule': lib_info['module'],
                                                               'MergeToMaster': False})
        queue_item = self._server.get_queue_item(queue_item_number)
        build_number = queue_item['executable']['number']

        while True:
            time.sleep(10)
            build_info = self._server.get_build_info(name=lib_job_name, number=build_number)
            if not build_info['building']:
                if build_info['result'] == 'SUCCESS':
                    return True
                else:
                    return False
