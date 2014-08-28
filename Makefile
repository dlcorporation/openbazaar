.PHONY: test style

all: test style

test:
	nosetests

style:
	find . -iname "*.py"|xargs flake8 --select=W291,W601 --exclude=*pybitmessage*
