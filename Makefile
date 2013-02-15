PREFIX ?= /usr/local
CWD=`pwd` 
all: build
	@echo "Done"
	@echo "Type: 'make install' now"

build:
	python -m compileall librgnome
make-install-dirs: 
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	mkdir -p $(DESTDIR)$(PREFIX)/share/
	mkdir -p $(DESTDIR)$(PREFIX)/share/pixmaps
	mkdir -p $(DESTDIR)$(PREFIX)/share/applications
	mkdir -p $(DESTDIR)$(PREFIX)/share/rgnome
	mkdir -p $(DESTDIR)$(PREFIX)/share/rgnome/resource
	mkdir -p $(DESTDIR)$(PREFIX)/share/rgnome/plugins
	mkdir -p $(DESTDIR)$(PREFIX)/share/rgnome/librgnome/ui
	mkdir -p $(DESTDIR)$(PREFIX)/share/rgnome/po
	mkdir -p $(DESTDIR)$(PREFIX)/share/locale
	mkdir -p $(DESTDIR)$(PREFIX)/share/gconf/schemas
	mkdir -p $(DESTDIR)$(PREFIX)/share/man/man1

install: make-install-dirs
	install -m 644 rgnome.1 $(DESTDIR)$(PREFIX)/share/man/man1
	install -m 755 rgnome $(DESTDIR)$(PREFIX)/bin
	install -m 644 rgnome.py $(DESTDIR)$(PREFIX)/share/rgnome
	install -m 644 resource/*.glade $(DESTDIR)$(PREFIX)/share/rgnome/resource
	install -m 644 resource/rgnome.png $(DESTDIR)$(PREFIX)/share/rgnome/resource
	install -m 644 resource/rgnome.schemas $(DESTDIR)$(PREFIX)/share/gconf/schemas
	install -m 644 po/*.po $(DESTDIR)$(PREFIX)/share/rgnome/po
	install -m 644 librgnome/*.py $(DESTDIR)$(PREFIX)/share/rgnome/librgnome
	install -m 644 librgnome/*.pyc $(DESTDIR)$(PREFIX)/share/rgnome/librgnome
	install -m 644 librgnome/ui/*.py $(DESTDIR)$(PREFIX)/share/rgnome/librgnome/ui
	install -m 644 librgnome/ui/*.pyc $(DESTDIR)$(PREFIX)/share/rgnome/librgnome/ui
	install -m 644 plugins/*.py $(DESTDIR)$(PREFIX)/share/rgnome/plugins
	install -m 644 plugins/*.glade $(DESTDIR)$(PREFIX)/share/rgnome/plugins
	install -m 644 resource/rgnome.png $(DESTDIR)$(PREFIX)/share/pixmaps/rgnome.png
	install -m 644 rgnome.desktop $(DESTDIR)$(PREFIX)/share/applications/
#	cd $(DESTDIR)$(PREFIX)/bin && \
#	ln -sf ../share/rgnome/rgnome.py rgnome && chmod 755 rgnome
	for f in `find po -name rgnome.mo` ; do \
		install -D $$f \
			`echo $$f | sed "s|po|$(DESTDIR)$(PREFIX)/share/locale|"` ; \
		done
clean:
	find . -name "*.pyc" -exec rm {} \;
	find . -name "*.pyo" -exec rm {} \;
	find . -name "*~" -exec rm {} \;

tarball: clean
	tar --exclude .svn -czvf ../rgnome.tar.gz ../rgnome
	
uninstall:
	rm -r $(DESTDIR)$(PREFIX)/share/rgnome
	rm -r $(DESTDIR)$(PREFIX)/bin/rgnome
	rm $(DESTDIR)$(PREFIX)/share/applications/rgnome.desktop
	rm $(DESTDIR)$(PREFIX)/share/pixmaps/rgnome.png
	find $(DESTDIR)$(PREFIX)/share/locale -name rgnome.mo -exec rm {} \;
