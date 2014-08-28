.PHONY: test style

all: test style

test:
	nosetests

style:
	find . -iname "*.py"|xargs flake8 --ignore=E501,E303,E128,F401,E226,F841,E261,E241,E502,F403,E302,F821,E127,E124,E225,F811,W391,E701,E711,E265 --exclude=*pybitmessage*
