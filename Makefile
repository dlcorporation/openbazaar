.PHONY: test style

all: test style

test:
	nosetests

style:
	find . -iname "*.py"|xargs flake8 --select=W291,W601,E231,E901 --exclude=*pybitmessage*
