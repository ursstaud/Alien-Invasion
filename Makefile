help:
	@echo "make install to install dependencies"
	@echo "make run to run the game"

install:
	@if [ `python -V | awk '{print int($2)}'` -ge 3 ]; then \
		echo "Python 3 required for this game"; \
		exit 1; \
	fi
	@python -m pip install pygame --user

run:
	@python alien_invasion.py
