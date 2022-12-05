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

top_srcdir := $(shell cd ../../.. ; pwd)

examples_srcdir := $(top_srcdir)/dependencies/CASE-Examples-QC/dependencies/casework.github.io/examples

exdirs := $(shell find * -maxdepth 0 -type d | sort | egrep -v '^src$$')

all_targets       := $(foreach exdir,$(exdirs),all-$(exdir))
check_targets     := $(foreach exdir,$(exdirs),check-$(exdir))
clean_targets     := $(foreach exdir,$(exdirs),clean-$(exdir))

all: \
  $(all_targets)

all-%:
	$(MAKE) \
	  --directory $$(echo $@ | sed -e 's/^all-//')

check: \
  $(check_targets)
	@diff \
	  <(ls */prov-constraints.log | while read x; do dirname $$x ; done) \
	  <(cd $(examples_srcdir) ; ls */*.json | while read x; do dirname $$x ; done | sort | uniq) \
	  || (echo "ERROR:Makefile:The illustrations listed above do not have evaluation directories under $(top_srcdir)/tests/casework.github.io/examples." >&2 ; exit 1)

check-%:
	$(MAKE) \
	  --directory $$(echo $@ | sed -e 's/^check-//') \
	  check

clean: \
  $(clean_targets)

clean-%:
	@$(MAKE) \
	  --directory $$(echo $@ | sed -e 's/^clean-//') \
	  clean
