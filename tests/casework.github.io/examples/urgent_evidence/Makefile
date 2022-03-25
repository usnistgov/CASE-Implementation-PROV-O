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

top_srcdir := $(shell cd ../../../.. ; pwd)

tests_srcdir := $(top_srcdir)/tests

all:
	$(MAKE) \
	  --file ../src/example.mk
	$(MAKE) \
	  urgent_evidence-prov-activities-focus-extracted-file-uuid-1.svg \
	  urgent_evidence-prov-all-focus-extracted-file-uuid-1.svg \
	  urgent_evidence-prov-all-initial_investigative_actions.svg \
	  urgent_evidence-prov-entities-focus-extracted-file-uuid-1.svg

%.svg: \
  %.dot
	dot -o _$@ -T svg $<
	mv _$@ $@

check:
	$(MAKE) \
	  --file ../src/example.mk \
	  check
	source $(tests_srcdir)/venv/bin/activate \
	  && pytest \
	    --log-level=DEBUG

clean:
	@$(MAKE) \
	  --file ../src/example.mk \
	  clean

urgent_evidence-prov-activities-focus-extracted-file-uuid-1.dot: \
  urgent_evidence-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --activity-informing \
	    --dash-unqualified \
	    --debug \
	    --entity-ancestry http://example.org/kb/extracted-file-uuid-1 \
	    _$@ \
	    $<
	mv _$@ $@

urgent_evidence-prov-all-focus-extracted-file-uuid-1.dot: \
  urgent_evidence-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --dash-unqualified \
	    --debug \
	    --entity-ancestry http://example.org/kb/extracted-file-uuid-1 \
	    _$@ \
	    $<
	mv _$@ $@

urgent_evidence-prov-all-initial_investigative_actions.dot: \
  urgent_evidence-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --activity-informing \
	    --dash-unqualified \
	    --debug \
	    --from-empty-set \
	    _$@ \
	    $<
	mv _$@ $@

urgent_evidence-prov-entities-focus-extracted-file-uuid-1.dot: \
  urgent_evidence-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --dash-unqualified \
	    --debug \
	    --entity-deriving \
	    --entity-ancestry http://example.org/kb/extracted-file-uuid-1 \
	    _$@ \
	    $<
	mv _$@ $@
