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

# This Makefile was adapted from UCO's ontology repository.

SHELL := /bin/bash

top_srcdir := $(shell cd ../.. ; pwd)

ttl_basenames := $(shell find *.ttl -type f | sort)

# These are reference files, named with a leading dot.
check_reference_basenames := $(foreach ttl_basename,$(ttl_basenames),.$(ttl_basename)-check)

# These are recipe targets, not intended to be created files.
check_targets := $(foreach ttl_basename,$(ttl_basenames),check-$(ttl_basename))

all: \
  $(check_reference_basenames)

.%.ttl-check: \
  %.ttl \
  $(top_srcdir)/.git_submodule_init.done.log
	java -jar $(top_srcdir)/dependencies/CASE-Examples-QC/dependencies/CASE-Examples/dependencies/UCO-develop/lib/rdf-toolkit.jar \
	  --inline-blank-nodes \
	  --source $< \
	  --source-format turtle \
	  --target _$@ \
	  --target-format turtle
	mv _$@ $@

check: \
  $(check_targets)

# Reminder: diff exits non-0 on finding any differences.
# Reminder: The $^ automatic Make variable is the name of all recipe prerequisites.
check-%.ttl: \
  %.ttl \
  .%.ttl-check
	diff \
	  $< \
	  .$<-check \
	  || (echo "ERROR:caseprov/shapes/Makefile:The local $< does not match the normalized version. If the above reported changes look fine, run 'cp .$<-check $<' while in the sub-folder case_prov/shapes/ to get a file ready to commit to Git." >&2 ; exit 1)

clean:
	@rm -f $(check_reference_basenames)
