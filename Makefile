all:
	rm -rf index.html src/*.html
	python3 scripts/generate_pages.py

push: all
	git add .
	git commit -m "build"
	git push origin main