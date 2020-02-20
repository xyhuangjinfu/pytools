import json
import re
import ssl
import sys
import urllib.request

ROUTE_POLICY = 'shanbay.native.app://policy/privacy'
ROUTE_POLICY_KID = 'shanbay.native.app://policy/privacy_kid'


# 获取base项目跟路径
def _get_root_dir():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        # 默认使用我自己的路径
        return '/Users/huangjinfu/work/project/shanbay-base-android'


# 获取最新隐私策略信息
def _get_policy_dict():
    ssl._create_default_https_context = ssl._create_unverified_context

    response = urllib.request.urlopen('https://apiv3.shanbay.com/lune/privacy_policy')
    resp_str = response.read().decode('utf-8')

    policy_obj = json.loads(resp_str)
    policy_list = policy_obj['objects']

    policy_dict = {}

    for po in policy_list:
        policy_dict[po['route']] = po['url']

    return policy_dict


# 更新隐私策略url
def _update_policy_url(root_dir, policy_dict):
    path = root_dir + '/module-base/src/main/java/com/shanbay/biz/privacy/PolicyStorage.java'

    fp = open(path, 'r+')
    code = fp.read()

    policy_re = re.compile('policy.url = \".*\";')
    code = re.sub(policy_re,
                  'policy.url = "' + policy_dict[ROUTE_POLICY] + '";',
                  code)

    policy_kid_re = re.compile('policyKid.url = \".*\";')
    code = re.sub(policy_kid_re,
                  'policyKid.url = "' + policy_dict[ROUTE_POLICY_KID] + '";',
                  code)

    fp.seek(0)
    fp.write(code)
    fp.close()


# 更新隐私策略文件
def _update_policy_file(root_dir, policy_dict):
    _update_single_policy_file(root_dir + '/module-base/src/main/assets/content/privacy_policy.html',
                               policy_dict[ROUTE_POLICY])
    _update_single_policy_file(root_dir + '/module-base/src/main/assets/content/children_privacy_policy.html',
                               policy_dict[ROUTE_POLICY_KID])


# 更新单个隐私策略文件
def _update_single_policy_file(file_path, url):
    response = urllib.request.urlopen(url)
    response_str = response.read().decode('utf-8')

    fp = open(file_path, 'r+')
    fp.write(response_str)
    fp.close()


# 更新
def update():
    root_dir = _get_root_dir()
    policy_dict = _get_policy_dict()
    _update_policy_url(root_dir, policy_dict)
    _update_policy_file(root_dir, policy_dict)


if __name__ == "__main__":
    update()
