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

sparql_files := $(wildcard $(top_srcdir)/case_prov/queries/construct-*.sparql)

all: \
  all-CASE-Examples \
  all-casework.github.io

.PHONY: \
  all-CASE-Examples \
  all-casework.github.io \
  check-CASE-Examples \
  check-casework.github.io \
  clean-CASE-Examples \
  clean-casework.github.io

.venv.done.log: \
  $(qc_srcdir)/deps/requirements.txt \
  $(sparql_files) \
  $(top_srcdir)/case_prov/__init__.py \
  $(top_srcdir)/case_prov/case_prov_dot.py \
  $(top_srcdir)/case_prov/case_prov_rdf.py \
  $(top_srcdir)/setup.cfg \
  $(top_srcdir)/setup.py \
  requirements.txt
	rm -rf venv
	$(PYTHON3) -m virtualenv \
	  --python=$(PYTHON3) \
	  venv
	source venv/bin/activate \
	  && pip install \
	    --upgrade \
	    pip \
	    setuptools
	source venv/bin/activate \
	  && cd $(top_srcdir) \
	    && python3 setup.py install
	source venv/bin/activate \
	  && pip install \
	    --requirement $(qc_srcdir)/deps/requirements.txt
	source venv/bin/activate \
	  && pip install \
	    --requirement requirements.txt
	touch $@

all-CASE-Examples: \
  .venv.done.log
	$(MAKE) \
	  --directory CASE-Examples/examples

all-casework.github.io: \
  .venv.done.log
	$(MAKE) \
	  --directory casework.github.io/examples

check: \
  check-CASE-Examples \
  check-casework.github.io

check-CASE-Examples: \
  .venv.done.log
	$(MAKE) \
	  --directory CASE-Examples/examples \
	  check

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
	  --directory CASE-Examples/examples \
	  clean

clean-casework.github.io:
	@$(MAKE) \
	  --directory casework.github.io/examples \
	  clean
