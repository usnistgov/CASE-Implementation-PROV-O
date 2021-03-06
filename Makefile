#!/usr/bin/make -f

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

SHELL := /bin/bash

all: \
  .git_submodule_init.done.log
	$(MAKE) \
	  --directory tests
	$(MAKE) \
	  --directory figures

.PHONY: \
  clean-figures \
  clean-tests

.git_submodule_init.done.log: \
  .gitmodules
	git submodule init
	git submodule update
	$(MAKE) \
	  --directory dependencies/CASE-Examples-QC \
	  .git_submodule_init.done.log \
	  .lib.done.log
	touch $@

check: \
  .git_submodule_init.done.log
	$(MAKE) \
	  --directory tests \
	  check

clean: \
  clean-figures \
  clean-tests

clean-figures:
	@$(MAKE) \
	  --directory figures \
	  clean

clean-tests:
	@$(MAKE) \
	  --directory tests \
	  clean

distclean: \
  clean
	@rm -rf \
	  build \
	  dist
	@rm -f \
	  *.egg-info
