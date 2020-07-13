PREFIX ?= ~
VERSION = "0.0.2"

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

publish: build
	@docker push aquariumbio/pfish:$(VERSION) \
	&& docker push aquariumbio/pfish:latest

.PHONY: all install uninstall build publish