.PHONY: test style

all: test style

test:
	nosetests --with-coverage --cover-package=node --cover-inclusive

style:
	./checkstyle.sh
