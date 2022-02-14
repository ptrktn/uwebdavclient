#!/usr/bin/env python3
#
# uwebdavclient - (Micro) WebDAV client
# Copyright (C) 2022  ptrktn@github
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import argparse
import sys
import os
import requests
import time
import hashlib
from requests.packages.urllib3.exceptions import InsecureRequestWarning

cfg = {
    "logger": None,
    "retry": 8
}


class Client(object):
    opt_keys = ['hostname', 'login', 'password', 'token', 'root',
                'cert_path', 'key_path', 'recv_speed', 'send_speed',
                'verbose', 'disable_check', 'override_methods',
                'timeout', 'chunk_size', 'insecure']

    def __init__(self, options):
        self.options = dict()
        self.options["verbose"] = False
        self.options["insecure"] = False
        self.options["root"] = "/"
        for i in self.opt_keys:
            if options.get(i):
                self.options[i] = options[i]
        if self.options["insecure"]:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def get_url(self, path):
        return (
            f"{self.options['hostname']}"
            f"{self.options['root']}/{path}"
        )

    def check(self, remote_path):
        """ True if resource is exist or False otherwise """
        url = self.get_url(remote_path)
        try:
            r = requests.request(
                "PROPFIND",
                url,
                auth=(
                    self.options["login"],
                    self.options["password"]),
                verify=not(self.options["insecure"])
            )
        except requests.exceptions.SSLError as e:
            self.log(f"{e}")
            return False
        except Exception as e:
            self.log(f"{e}")
            return False

        self.log(f"check {url} {r.status_code}")
        if 207 == r.status_code or 200 == r.status_code:
            return True
        return False

    def mkdir(self, remote_path):
        for n in range(1, cfg["retry"]):
            status = self._mkdir(remote_path)
            if True == status:
                return True
            self.log(f"Retry n={n}")
            time.sleep(n**2)
        return False

    def _mkdir(self, remote_path):
        url = self.get_url(remote_path)
        try:
            r = requests.request(
                "MKCOL",
                url,
                auth=(
                    self.options["login"],
                    self.options["password"]),
                verify=not(self.options["insecure"])
            )
        except requests.exceptions.SSLError as e:
            self.log(f"{e}")
            return False
        except Exception as e:
            self.log(f"{e}")
            return False

        self.log(f"check {url} {r.status_code}")
        if 201 == r.status_code or 200 == r.status_code:
            self.log(f"Directory {remote_path} created")
            return True
        elif 401 == r.status_code:
            self.log(
                f"Unauthorized {url} {self.options['login']} {remote_path}")
        elif 405 == r.status_code:
            self.log(f"Directory {remote_path} already exists")
            return True
        elif 409 == r.status_code:
            self.log(f"Parent of directory {remote_path} does not exist")
        else:
            self.log(f"Unhandled status code: {r.status_code}")

        return False

    def log(self, msg):
        if self.options["verbose"]:
            sys.stderr.write(
                f"{time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())} "
                f"{msg}\n"
            )
            sys.stderr.flush()

    def upload_sync(self, remote_path, local_path, *args, **kwargs):
        for n in range(1, cfg["retry"]):
            status = self._upload(remote_path, local_path)
            if True == status:
                return True
            self.log(f"Retry n={n}")
            time.sleep(n**2)
        return False

    def _upload(self, remote_path, local_path, *args, **kwargs):
        url = self.get_url(remote_path)
        filename = os.path.basename(local_path)
        with open(local_path, "rb") as fp:
            data = fp.read()
        try:
            r = requests.put(
                url,
                data=data,
                headers={
                    'Content-type': 'application/octet-stream',
                    'Slug': filename
                },
                auth=(
                    self.options["login"],
                    self.options["password"]),
                verify=not(self.options["insecure"])
            )
        except requests.exceptions.SSLError as e:
            self.log(f"{e}")
            return False

        self.log(f"upload {url} {r.status_code}")
        if r.status_code in [201, 204]:
            if r.headers.get("X-Hash-Md5"):
                md5_orig = md5sum(local_path).lower()
                md5_dest = r.headers.get("X-Hash-Md5").lower()
                if md5_orig == md5_dest:
                    self.log(f"File {filename} uploaded to {url}")
                    return True
                else:
                    self.log(
                        f"File {filename} checksum mismatch: "
                        f"orig={m5d_orig} dest={md5_dest}")
                    return False
            self.log(f"File {filename} uploaded to {url} "
                     "without checksum verification")
            return True
        else:
            self.log(f"File {filename} upload to server {url} failed "
                     "(status_code={r.status_code})")
        return False

    def download_sync(self, remote_path, local_path, *args, **kwargs):
        for n in range(1, cfg["retry"]):
            status = self._download(remote_path, local_path)
            if True == status:
                return True
            self.log(f"Retry n={n}")
            time.sleep(n**2)
        return False

    def _download(self, remote_path, local_path, *args, **kwargs):
        url = self.get_url(remote_path)
        filename = os.path.basename(local_path)
        try:
            r = requests.get(
                url,
                auth=(
                    self.options["login"],
                    self.options["password"]),
                verify=not(self.options["insecure"])
            )
        except requests.exceptions.SSLError as e:
            self.log(f"{e}")
            return False

        self.log(f"download {url} {r.status_code}")
        if 200 == r.status_code:
            with open(local_path, "wb") as fp:
                fp.write(r.content)
            self.log(f"File {url} downloaded to {local_path}")
            return True
        return False


# https://stackoverflow.com/a/3431838
def md5sum(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", default=False)
    parser.add_argument('--download', action="store_true", default=False)
    parser.add_argument('--hostname', default=os.getenv("WEBDAV_HOSTNAME"))
    parser.add_argument(
        '--insecure', action="store_true",
        default=bool(
            os.getenv("WEBDAV_INSECURE", 0)))
    parser.add_argument('--login', default=os.getenv("WEBDAV_LOGIN"))
    parser.add_argument('--password', default=os.getenv("WEBDAV_PASSWORD"))
    parser.add_argument('--prefix', default=os.getenv("WEBDAV_PREFIX"))
    parser.add_argument('--root', default=os.getenv("WEBDAV_ROOT"))
    parser.add_argument('--upload', action="store_true", default=False)
    parser.add_argument(
        '--verbose',
        action="store_true",
        default=bool(os.getenv(
            "WEBDAV_VERBOSE",
            False)))
    parser.add_argument(
        "input",
        nargs="+",
        metavar="INPUT",
        type=str,
        help="input file or dir name(s)")
    args, unknown = parser.parse_known_args()

    options = {
        "login": args.login,
        "password": args.password,
        "hostname": args.hostname,
        "verbose": args.verbose,
        "root": args.root,
        "insecure": args.insecure
    }

    client = Client(options)

    client.log(f"INPUT {args.input}")
    client.log(f"PREFIX {args.prefix}")

    if args.check:
        for i in args.input:
            client.log(f"CHECK {i}")
            print(client.check(i))
        return

    if args.download:
        for i in args.input:
            # cp FILE .
            dst = os.path.basename(i)
            client.log(f"DOWNLOAD {i}")
            client.download_sync(i, dst)
        return

    if not(args.upload):
        return

    xfiles = []
    xdirs = []

    for i in args.input:
        if os.path.isfile(i):
            # cp FILE .
            xfiles.append((os.path.realpath(i), os.path.basename(i)))
        elif os.path.isdir(i):
            # cp -r DIR .
            basedir = os.path.basename(i)
            xdirs.append(basedir)
            cwd = os.path.realpath(os.getcwd())
            os.chdir(os.path.realpath(i))
            for root, subdirs, files in os.walk("."):
                for subdir in subdirs:
                    xdirs.append(
                        os.path.normpath(
                            os.path.join(
                                basedir,
                                os.path.join(
                                    root,
                                    subdir))))
                for fname in files:
                    xfiles.append(
                        (os.path.realpath(
                            os.path.join(
                                root, fname)), os.path.normpath(
                            os.path.join(
                                basedir, root, fname))))
            os.chdir(cwd)
        else:
            client.log(f"WARNING: argument {i} is not a file or a directory")

    if args.prefix:
        pdirs = []
        xdir = ""
        for i in os.path.normpath(args.prefix).split(os.path.sep):
            xdir = os.path.join(xdir, i)
            pdirs.append(xdir)
        xdirs = [os.path.join(args.prefix, i) for i in xdirs]
        pdirs.extend(xdirs)
        xdirs = pdirs
        xfiles = [(i, os.path.join(args.prefix, x)) for i, x in xfiles]

    for xdir in xdirs:
        client.log(f"DIR {xdir}")
        client.mkdir(xdir)

    for src, xfile in xfiles:
        client.log(f"FILE {src} {xfile}")
        client.upload_sync(xfile, src)

    return 0
