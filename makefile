all:
	@cat makefile
python-init:
	pip install numpy scipy matplotlib ipdb ipython
publish: # you should not run this command
	git archive --format=tar -o ../bilibili-resources.tar HEAD
	tar -xf ../bilibili-resources.tar -C ../bilibili-resources/