.PHONY: test style

all: test style

test:
	nosetests

style:
	./checkstyle.sh
