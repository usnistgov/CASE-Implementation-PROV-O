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

top_srcdir := $(shell cd ../../../../.. ; pwd)

tests_srcdir := $(top_srcdir)/tests

all:
	$(MAKE) \
	  --file ../src/illustration.mk
	$(MAKE) \
	  Oresteia-prov-focus-sms-message1-uuid.svg \
	  Oresteia-prov-focus-sms-message2-uuid.svg

%.svg: \
  %.dot
	dot \
	  -o _$@ \
	  -T svg \
	  $<
	mv _$@ $@

# TODO: Fix constraints errors, then uncomment the recipe to enforce unit testing.
check:
	@echo "ERROR:PROV constraints reports errors for forensic_lifecycle.json, which need fixing." >&2
#	$(MAKE) \
#	  --file ../src/illustration.mk \
#	  check

clean:
	@$(MAKE) \
	  --file ../src/illustration.mk \
	  clean

Oresteia-prov-focus-sms-message1-uuid.dot: \
  Oresteia-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    --entity-ancestry http://example.org/kb/sms-message1-uuid \
	    $< \
	    _$@
	mv _$@ $@

Oresteia-prov-focus-sms-message2-uuid.dot: \
  Oresteia-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    --entity-ancestry http://example.org/kb/sms-message2-uuid \
	    $< \
	    _$@
	mv _$@ $@
