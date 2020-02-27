import base64
import json
import urllib.request

import sb_config


class SBNexus:
    def __init__(self, sb_config: sb_config.SBConfig):
        self._sb_config = sb_config.config
        self._token = None
        self._login()

    def get_next_lib_version(self, lib):
        """
        获取一个库的下一个可用的测试版本号
        :param lib:
        :return: 获取失败返回None
        """
        server_url = self._sb_config['nexus']['server_url']
        group_id = self._sb_config['libs'][lib]['group_id']
        group_path = group_id.replace('.', '/')
        url = f'{server_url}service/local/repositories/releases/content/{group_path}/{lib}/'
        req = urllib.request.Request(url, headers={'Cookie': f'NXSESSIONID={self._token}',
                                                   'Accept': 'application/json'})

        resp = urllib.request.urlopen(req)

        resp_code = resp.getcode()
        if resp_code != 200:
            return None

        resp_body = resp.read().decode('utf-8')

        version_list = []
        obj = json.loads(resp_body)
        li = obj['data']
        for a in li:
            if not a['leaf'] and '-test-hjf' in a['text']:
                version_list.append(a['text'])

        if version_list:
            def sory_key(v):
                seg = v.split('-')
                vseg = seg[0].split('.')
                return len(vseg), vseg, seg[len(seg) - 1]

            version_list.sort(reverse=True, key=sory_key)

            ver = version_list[0]
            seg = ver.split('-')
            test_ver = seg[len(seg) - 1]
            test_ver = str(int(test_ver) + 1)
            ver = ''
            for i in range(len(seg) - 1):
                ver += seg[i]
                ver += '-'
            ver += test_ver
            return ver
        else:
            return '0.0.0.0-test-hjf-1'

    def _login(self):
        """
        登录到nexus服务器
        :return:
        """
        server_url = self._sb_config['nexus']['server_url']
        username = self._sb_config['nexus']['username']
        passsword = self._sb_config['nexus']['password']

        url = f'{server_url}service/local/authentication/login'

        user_pass_base64 = str(base64.b64encode(bytes(f'{username}:{passsword}', encoding='utf-8')), encoding='utf-8')
        req = urllib.request.Request(url, headers={'Accept': 'application/json',
                                                   'Authorization': f'Basic {user_pass_base64}'})
        resp = urllib.request.urlopen(req)
        self._token = resp.headers['Set-Cookie'].split('=')[1].split(';')[0]


if __name__ == '__main__':
    pass
