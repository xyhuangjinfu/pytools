import os
import threading
import uuid
import zipfile
from http.server import HTTPServer, BaseHTTPRequestHandler

import ding
import hprof.hprof_helper

HOST = ('192.168.1.145', 7777)

ROOT_DIR = "/home/shanbay/memory_guard/server"
HPROF_DIR = os.path.join(ROOT_DIR, "hprof")
REPORT_DIR = os.path.join(ROOT_DIR, "report")


class Resquest(BaseHTTPRequestHandler):

    def do_GET(self):
        print("do_get")
        relative_path = self.path
        if relative_path.startswith("/"):
            relative_path = relative_path[1:]
        file_absolute_path = os.path.join(ROOT_DIR, relative_path)

        if os.path.exists(file_absolute_path):
            fd = open(file_absolute_path)
            file_length = os.path.getsize(file_absolute_path)

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(file_length))
            self.end_headers()

            read_count = 0
            read_length = 1024 * 1024
            while read_count < file_length:
                buffer = fd.read(read_length)
                read_count += read_length
                self.wfile.write(bytes(buffer, encoding="utf-8"))

            fd.close()
            # self.wfile.close()
        else:
            data = "file not found"
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(bytes(data, encoding="utf-8"))
            # self.wfile.close()

    def do_POST(self):
        print("do_post")
        file_length = int(self.headers.get("Content-Length"))
        app = self.headers.get("APP")
        version = self.headers.get("VERSION")

        zip_file_name = ".".join([str(uuid.uuid1()), "zip"])
        # relative_path = "/".join([app, version, file_name])
        zip_file_path = os.path.join(HPROF_DIR, zip_file_name)

        file_dir = os.path.split(zip_file_path)[0]
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        fd = open(zip_file_path, "wb+")
        read_count = 0
        read_length = 1024 * 1024
        while read_count < file_length:
            remain_length = file_length - read_count
            read_length = min(remain_length, read_length)
            buffer = self.rfile.read(read_length)
            fd.write(buffer)
            read_count += read_length
            print(f"{read_count} / {file_length}")
        # self.rfile.close()
        print(f"write {zip_file_path}")

        data = "file upload success"
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(bytes(data, encoding="utf-8"))
        # self.wfile.close()

        t = threading.Thread(target=self._async_process, args=(zip_file_path, app, version))
        t.start()

    def _async_process(self, zip_file_path, app, version):
        print(f"async process {threading.current_thread().name}")
        # unzip
        hprof_file_path = None
        zf = zipfile.ZipFile(zip_file_path, 'r')
        for f in zf.namelist():
            zf.extract(f, HPROF_DIR)
            hprof_file_path = os.path.join(HPROF_DIR, f)
            break
        os.remove(zip_file_path)

        print("detect")
        leak, report_path = hprof.hprof_helper.detect(hprof_file_path)
        if report_path.startswith("/"):
            report_path = report_path[1:]
        print(leak)
        print("notify")
        ding.report_leak(app, version, leak, f"http://{HOST[0]}:{HOST[1]}/{report_path}")


if __name__ == '__main__':
    server = HTTPServer(HOST, Resquest)
    print("Starting memory guard http server, listen at: %s:%s" % HOST)
    server.serve_forever()

    # p = "/Users/huangjinfu/work/project/memory-guard/server/hprof/MGDemo/1.2.301/d260d4b6-b1e9-11ea-99e6-6c96cfd9f3cb.hprof"
    # os.makedirs(os.path.split(p)[0])
