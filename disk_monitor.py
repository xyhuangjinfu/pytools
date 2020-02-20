import sched
import ssl
import subprocess
import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context


def file_system_used(file_system):
    call_df = subprocess.Popen(['df', file_system], stdout=subprocess.PIPE)
    call_awk = subprocess.check_output(['awk', '{if(NR==2) print $5}'], stdin=call_df.stdout)
    used = int(call_awk.decode('utf-8').replace('%', ''))
    return used


def warning(file_system, disk_used):
    request = urllib.request.Request(
        'https://oapi.dingtalk.com/robot/send?access_token=36c372e0cf9bf9952af28e7b8e90f5203921d2037d0afde7e93c6beecceeecf0')
    request.add_header('Content-Type', 'application/json')
    data = {'msgtype': 'text', 'text': {'content': f'file system : {file_system}, used : {disk_used}%'}}
    request.data = bytes(str(data), 'utf-8')
    urllib.request.urlopen(request)


def check():
    file_system = '/dev/vdb'  # 要检测的文件系统
    water_line = 90  # 报警线
    used = file_system_used(file_system)
    if used > water_line:
        warning(file_system, used)


def check_periodic():
    run_periodic(check)


def run_periodic(action):
    period = 60 * 60  # 检查周期，单位秒
    scheduler = sched.scheduler()

    def action_wrapper():
        action()
        scheduler.enter(period, 0, action=action_wrapper)

    scheduler.enter(period, 0, action=action_wrapper)
    scheduler.run()


if __name__ == '__main__':
    check_periodic()
