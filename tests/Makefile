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

PYTHON3 ?= $(shell which python3.9 2>/dev/null || which python3.8 2>/dev/null || which python3.7 2>/dev/null || which python3.6 2>/dev/null || which python3)

top_srcdir := $(shell cd .. ; pwd)

qc_srcdir := $(top_srcdir)/dependencies/CASE-Examples-QC

all: \
  all-CASE-Examples \
  all-casework.github.io

.PHONY: \
  all-CASE-Examples \
  all-casework.github.io \
  check-CASE-Examples \
  check-black \
  check-casework.github.io \
  clean-CASE-Examples \
  clean-casework.github.io \
  format

.venv.done.log: \
  $(qc_srcdir)/deps/requirements.txt \
  $(top_srcdir)/.git_submodule_init.done.log \
  $(top_srcdir)/dependencies/CASE-Utilities-Python/tests/requirements.txt \
  $(top_srcdir)/setup.cfg \
  $(top_srcdir)/setup.py
	rm -rf venv
	$(PYTHON3) -m venv \
	  venv
	source venv/bin/activate \
	  && pip install \
	    --upgrade \
	    pip \
	    setuptools \
	    wheel
	source venv/bin/activate \
	  && pip install \
	    $(top_srcdir)/dependencies/CASE-Utilities-Python
	source venv/bin/activate \
	  && pip install \
	    --requirement $(top_srcdir)/dependencies/CASE-Utilities-Python/tests/requirements.txt
	source venv/bin/activate \
	  && pip install \
	    --editable \
	    $(top_srcdir)
	source venv/bin/activate \
	  && pip install \
	    --requirement $(qc_srcdir)/deps/requirements.txt
	touch $@

all-CASE-Examples: \
  .venv.done.log
	$(MAKE) \
	  --directory CASE-Examples/examples/illustrations

all-casework.github.io: \
  .venv.done.log
	$(MAKE) \
	  --directory casework.github.io/examples

check: \
  check-black \
  check-CASE-Examples \
  check-casework.github.io

check-CASE-Examples: \
  .venv.done.log
	$(MAKE) \
	  --directory CASE-Examples/examples/illustrations \
	  check

check-black: \
  .venv.done.log
	source venv/bin/activate \
	  && black \
	    --check \
	    $(top_srcdir)/case_prov \
	    $$PWD

check-casework.github.io: \
  .venv.done.log
	$(MAKE) \
	  --directory casework.github.io/examples \
	  check

clean: \
  clean-CASE-Examples \
  clean-casework.github.io
	@rm -f \
	  .venv.done.log
	@rm -rf \
	  venv

clean-CASE-Examples:
	@$(MAKE) \
	  --directory CASE-Examples/examples/illustrations \
	  clean

clean-casework.github.io:
	@$(MAKE) \
	  --directory casework.github.io/examples \
	  clean

format: \
  .venv.done.log
	source venv/bin/activate \
	  && black \
	    $(top_srcdir)/case_prov \
	    $$PWD
