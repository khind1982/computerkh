TAGSDIRS != python -c "import os, sys; \
	print(' '.join('{}'.format(d) for d in sys.path if os.path.isdir(d)))"

tags: $(SRCS) Makefile
	exctags -R --fields=+l --languages=python \
		--python-kinds=-iv -f ./tags . $(TAGSDIRS)
