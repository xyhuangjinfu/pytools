import os
import time
import uuid

import hprof.parser
import hprof.leak_report_writer
import hprof.leak_detector

ROOT_DIR = "/home/shanbay/memory_guard/server"
REPORT_DIR = os.path.join(ROOT_DIR, "report")


def detect(file_path):
    print("start parse")
    t = time.time()
    hprof_parser = hprof.parser.HprofParser(file_path, True)
    print(hprof_parser)
    _h = hprof_parser.get()
    t = time.time() - t
    print(f"end parse {_h} {t} seconds")

    print("start analyse")
    t = time.time()
    leak_detector = hprof.leak_detector.LeakDetector(_h)
    print(leak_detector)
    _leak, _reference_link = leak_detector.detect()
    t = time.time() - t
    print(f"end analyse {t} seconds")

    print(_leak)
    hprof.leak_report_writer.print_console_reverse(_reference_link)

    analyse_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    na = "_".join([analyse_date, str(uuid.uuid1())])
    file_name = ".".join([na, "txt"])
    report_file_path = os.path.join(REPORT_DIR, file_name)

    report_file_dir = os.path.split(report_file_path)[0]
    if not os.path.exists(report_file_dir):
        os.makedirs(report_file_dir)
    hprof.leak_report_writer.write_reverse(report_file_path, _reference_link)

    print(report_file_path)
    return _leak, report_file_path.replace(ROOT_DIR, "")


if __name__ == '__main__':
    pass

