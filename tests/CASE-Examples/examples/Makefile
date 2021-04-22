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

qc_srcdir := $(top_srcdir)/dependencies/CASE-Examples-QC

case_srcdir := $(qc_srcdir)/dependencies/CASE-Examples/dependencies/CASE

example_srcdir := $(qc_srcdir)/dependencies/CASE-Examples/examples

tests_srcdir := $(top_srcdir)/tests

sparql_files := $(wildcard $(top_srcdir)/case_prov/queries/construct-*.sparql)

json_files := $(wildcard $(top_srcdir)/dependencies/CASE-Examples-QC/dependencies/CASE-Examples/examples/*.json)

ttl_files := $(foreach json_file,$(json_files),$(subst .json,-prov.ttl,$(shell basename $(json_file))))

substantive_svg_files := \
  Oresteia-prov-activities.svg \
  Oresteia-prov-agents.svg \
  Oresteia-prov-all.svg \
  Oresteia-prov-entities.svg \
  accounts-prov-all.svg \
  exif_data-prov-all.svg \
  forensic_lifecycle-prov-all.svg \
  network_connection-prov-all.svg \
  reconstructed_file-prov-all.svg

all: \
  Oresteia-prov-focus-sms-message1-uuid.svg \
  Oresteia-prov-focus-sms-message2-uuid.svg \
  Oresteia-prov-originals.svg \
  exif_data-prov-originals.svg \
  forensic_lifecycle-prov-originals.svg \
  network_connection-prov-originals.svg \
  prov-constraints.log \
  reconstructed_file-prov-originals.svg \
  $(substantive_svg_files)

.PRECIOUS: \
  %-all.dot \
  %-originals.dot \
  %-prov.ttl \
  %.dot \
  %.ttl

%.png: \
  %.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && rdf2dot -f turtle $< > __$@
	dot -o _$@ -T png __$@
	rm __$@
	mv _$@ $@

%.svg: \
  %.dot
	dot -o _$@ -T svg $<
	mv _$@ $@

%-all.dot: \
  %.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

%-originals.dot: \
  %.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    --from-empty-set \
	    $< \
	    _$@
	mv _$@ $@

%-prov.ttl: \
  $(example_srcdir)/%.json \
  $(sparql_files) \
  $(tests_srcdir)/.venv.done.log \
  $(top_srcdir)/case_prov/case_prov_rdf.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_rdf \
	    --allow-empty-results \
	    --debug \
	    $< \
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

Oresteia-prov.dot: \
  Oresteia-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

Oresteia-prov-activities.dot: \
  Oresteia-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --activity-informing \
	    --dash-unqualified \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

Oresteia-prov-agents.dot: \
  Oresteia-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --agent-delegating \
	    --dash-unqualified \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

Oresteia-prov-entities.dot: \
  Oresteia-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --entity-deriving \
	    --dash-unqualified \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

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

check: \
  prov-constraints.log

clean:
	@rm -f \
	  *.dot \
	  *.png \
	  *.svg \
	  *.ttl \
	  prov-constraints.log

prov-constraints.log: \
  $(top_srcdir)/dependencies/prov-check/provcheck/provconstraints.py \
  $(ttl_files)
	source $(tests_srcdir)/venv/bin/activate \
	  && python3 $(top_srcdir)/dependencies/prov-check/provcheck/provconstraints.py \
	    --debug \
	    $(ttl_files) \
	    > _$@ \
	    2>&1
	mv _$@ $@
