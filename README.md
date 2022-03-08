# uwebdavclient - (Micro) WebDAV client

## About

Minimal WebDAV client in pure Python. Only `GET`, `MKCOL`, `PROPFIND`
and `PUT` are supported. Consider
[webdavclient3](https://pypi.org/project/webdavclient3) for more
extensive support.  The disk (container image) space gain by using
this microscopic library is in the order of 15 MiB.

## Installation

```bash
pip install uwebdavclient --user
```

## Usage

    from uwebdavclient.client import Client
    options = {
        "hostname": "https://example.com",
        "login":    "login",
        "password": "password"
    }
    client = Client(options)
    client.mkdir("test")
	client.upload_sync("test/test.txt", "test.txt")
    client.download_sync("test/test.txt", "test_copy.txt")

## Contributing

All contributions are welcome. Bug reports, suggestions and feature
requests can be reported by creating a new
[issue](https://github.com/ptrktn/uwebdavclient/issues). Code and documentation
contributions should be provided by creating a [pull
request](https://github.com/ptrktn/uwebdavclient/pulls) (here is a good
[tutorial](https://www.dataschool.io/how-to-contribute-on-github/)).
Run `make tidy-sources` before committing and use imperative mood in
commit messages.

## License

Licensed under the GNU General Public License Version 3, refer to the
file [LICENSE](LICENSE) for more information.
