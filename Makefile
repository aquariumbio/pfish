PREFIX ?= ~
VERSION = "1.2.0"

all: install

install:
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	install -m 0755 pfish-wrapper $(DESTDIR)$(PREFIX)/bin/pfish

uninstall:
	@$(RM) $(DESTDIR)$(PREFIX)/bin/pfish
	@docker rmi aquariumbio/pfish:$(VERSION)
	@docker rmi aquariumbio/pfish:latest

build:
	@docker build -t aquariumbio/pfish:$(VERSION) . \
	&& docker tag aquariumbio/pfish:$(VERSION) aquariumbio/pfish:latest

.PHONY: all install uninstall build
