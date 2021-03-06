MYREPO = uwebdavclient
AUTOPEP8 = autopep8 --in-place --aggressive --aggressive --max-line-length 128

.PHONY: all
all: build

.PHONY: test
test:
	/bin/false

.PHONY: build
build: clean
	python3 -m build
	python3 -m twine check dist/*

.PHONY: install
install: build
	pip3 uninstall -y uwebdavclient
	pip3 install `find dist -type f -name '*.whl'` --user

.PHONY: upload
upload:
	python3 -m twine upload  --verbose --repository pypi dist/*

.PHONY: tidy-sources
tidy-sources:
	for i in src/uwebdavclient/client.py ; \
       do echo Checking file $$i ; \
       test -x "$$i" || exit 1 ; \
       python3 -m py_compile $$i || exit 1 ; \
       $(AUTOPEP8) $$i || exit 1 ; \
    done ; rm -fr src/uwebdavclient/__pycache__
	$(AUTOPEP8) setup.py

.PHONY: clean
clean:
	rm -fr ./dist ./src/uwebdavclient.egg-info
