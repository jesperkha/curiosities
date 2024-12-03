all:
	rm -rf index.html src/*.html
	python3 scripts/generate_pages.py