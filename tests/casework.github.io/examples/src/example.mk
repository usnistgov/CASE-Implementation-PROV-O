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

subjectdir_basename := $(shell basename $$PWD)

qc_srcdir := $(top_srcdir)/dependencies/CASE-Examples-QC

case_srcdir := $(qc_srcdir)/dependencies/CASE-Examples/dependencies/CASE-0.3.0/CASE

example_srcdir := $(qc_srcdir)/dependencies/casework.github.io/examples/$(subjectdir_basename)

subject_json := $(example_srcdir)/$(subjectdir_basename).json

sparql_files := $(wildcard $(top_srcdir)/case_prov/queries/construct-*.sparql)

tests_srcdir := $(top_srcdir)/tests

all: \
  $(subjectdir_basename)-prov-activities.svg \
  $(subjectdir_basename)-prov-all.svg \
  $(subjectdir_basename)-prov-agents.svg \
  $(subjectdir_basename)-prov-entities.svg \
  $(subjectdir_basename)-prov-originals.svg \
  prov-constraints.log

%.svg: \
  %.dot
	dot \
	  -o _$@ \
	  -T svg \
	  $<
	mv _$@ $@

$(subjectdir_basename)-prov.ttl: \
  $(subject_json) \
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

$(subjectdir_basename)-prov-activities.dot: \
  $(subjectdir_basename)-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --activity-informing \
	    --dash-unqualified \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

$(subjectdir_basename)-prov-agents.dot: \
  $(subjectdir_basename)-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --agent-delegating \
	    --dash-unqualified \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

$(subjectdir_basename)-prov-all.dot: \
  $(subjectdir_basename)-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --dash-unqualified \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

$(subjectdir_basename)-prov-entities.dot: \
  $(subjectdir_basename)-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --dash-unqualified \
	    --debug \
	    --entity-deriving \
	    $< \
	    _$@
	mv _$@ $@

$(subjectdir_basename)-prov-originals.dot: \
  $(subjectdir_basename)-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --dash-unqualified \
	    --debug \
	    --from-empty-set \
	    $< \
	    _$@
	mv _$@ $@

check: \
  prov-constraints.log
	@test 1 -eq $$(tail -n1 $< | grep 'True' | wc -l) \
	  || (echo "ERROR:example.mk:$(subjectdir_basename):prov-constraints reported a constraint error." >&2 ; exit 1)

clean:
	@rm -f \
	  *.dot \
	  *.svg \
	  *.ttl \
	  prov-constraints.log

prov-constraints.log: \
  $(top_srcdir)/dependencies/prov-check/provcheck/provconstraints.py \
  $(subjectdir_basename)-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && python3 $(top_srcdir)/dependencies/prov-check/provcheck/provconstraints.py \
	    --debug \
	    $(subjectdir_basename)-prov.ttl \
	    > _$@ \
	    2>&1
	mv _$@ $@
