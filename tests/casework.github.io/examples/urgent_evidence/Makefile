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

qc_srcdir := $(top_srcdir)/dependencies/CASE-Examples-QC

case_srcdir := $(qc_srcdir)/dependencies/CASE-Examples/dependencies/CASE

example_srcdir := $(qc_srcdir)/dependencies/casework.github.io/examples/urgent_evidence

tests_srcdir := $(top_srcdir)/tests

all: \
  prov-constraints.log \
  urgent_evidence-prov-activities.svg \
  urgent_evidence-prov-activities-focus-extracted-file-uuid-1.svg \
  urgent_evidence-prov-agents.svg \
  urgent_evidence-prov-all.svg \
  urgent_evidence-prov-all-focus-extracted-file-uuid-1.svg \
  urgent_evidence-prov-all-initial_investigative_actions.svg \
  urgent_evidence-prov-entities.svg \
  urgent_evidence-prov-entities-focus-extracted-file-uuid-1.svg

%.svg: \
  %.dot
	dot -o _$@ -T svg $<
	mv _$@ $@

check: \
  prov-constraints.log
	source $(tests_srcdir)/venv/bin/activate \
	  && pytest \
	    --log-level=DEBUG

clean:
	@rm -f \
	  *.dot \
	  *.png \
	  *.svg \
	  *.ttl \
	  prov-constraints.log

prov-constraints.log: \
  $(top_srcdir)/dependencies/prov-check/provcheck/provconstraints.py \
  urgent_evidence-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && python3 $(top_srcdir)/dependencies/prov-check/provcheck/provconstraints.py \
	    --debug \
	    urgent_evidence-prov.ttl \
	    > _$@ \
	    2>&1
	mv _$@ $@

urgent_evidence-prov.ttl: \
  $(example_srcdir)/urgent_evidence.json \
  $(tests_srcdir)/.venv.done.log
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_rdf \
	    --debug \
	    $(example_srcdir)/urgent_evidence.json \
	    __$@
	java -jar $(case_srcdir)/lib/rdf-toolkit.jar \
	  -ibi \
	  -ibn \
	  --source __$@ \
	  --source-format turtle \
	  --target _$@ \
	  --target-format turtle
	rm __$@
	mv _$@ $@

urgent_evidence-prov-activities.dot: \
  urgent_evidence-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --activity-informing \
	    --dash-unqualified \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

urgent_evidence-prov-agents.dot: \
  urgent_evidence-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --agent-delegating \
	    --dash-unqualified \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

urgent_evidence-prov-activities-focus-extracted-file-uuid-1.dot: \
  urgent_evidence-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --activity-informing \
	    --dash-unqualified \
	    --debug \
	    --entity-ancestry http://example.org/kb/extracted-file-uuid-1 \
	    $< \
	    _$@
	mv _$@ $@

urgent_evidence-prov-all.dot: \
  urgent_evidence-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --dash-unqualified \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

urgent_evidence-prov-all-focus-extracted-file-uuid-1.dot: \
  urgent_evidence-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --dash-unqualified \
	    --debug \
	    --entity-ancestry http://example.org/kb/extracted-file-uuid-1 \
	    $< \
	    _$@
	mv _$@ $@

urgent_evidence-prov-all-initial_investigative_actions.dot: \
  urgent_evidence-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    --from-empty-set \
	    $< \
	    _$@
	mv _$@ $@

urgent_evidence-prov-entities.dot: \
  urgent_evidence-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --dash-unqualified \
	    --debug \
	    --entity-deriving \
	    $< \
	    _$@
	mv _$@ $@

urgent_evidence-prov-entities-focus-extracted-file-uuid-1.dot: \
  urgent_evidence-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --dash-unqualified \
	    --debug \
	    --entity-deriving \
	    --entity-ancestry http://example.org/kb/extracted-file-uuid-1 \
	    $< \
	    _$@
	mv _$@ $@
