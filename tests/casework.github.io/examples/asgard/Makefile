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

example_srcdir := $(qc_srcdir)/dependencies/casework.github.io/examples/asgard

tests_srcdir := $(top_srcdir)/tests

sparql_files := $(wildcard $(top_srcdir)/case_prov/queries/construct-*.sparql)

all: \
  prov-constraints.log \
  asgard-prov.png \
  asgard-prov-originals.svg

%.png: \
  %.dot
	dot -o _$@ -T png $<
	mv _$@ $@

%.svg: \
  %.dot
	dot -o _$@ -T svg $<
	mv _$@ $@

check: \
  prov-constraints.log

asgard-prov.dot: \
  asgard-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

asgard-prov-focus-extracted-file-uuid-1.dot: \
  asgard-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    --entity-ancestry http://example.org/kb/extracted-file-uuid-1 \
	    $< \
	    _$@
	mv _$@ $@

asgard-prov-originals.dot: \
  asgard-prov.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    --from-empty-set \
	    $< \
	    _$@
	mv _$@ $@

asgard-prov.ttl: \
  $(example_srcdir)/asgard.json \
  $(sparql_files) \
  $(tests_srcdir)/.venv.done.log \
  $(top_srcdir)/case_prov/case_prov_rdf.py
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_rdf \
	    --debug \
	    $(example_srcdir)/asgard.json \
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

clean:
	@rm -f \
	  *.dot \
	  *.png \
	  *.svg \
	  *.ttl \
	  prov-constraints.log

prov-constraints.log: \
  $(top_srcdir)/dependencies/prov-check/provcheck/provconstraints.py \
  asgard-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && python3 $(top_srcdir)/dependencies/prov-check/provcheck/provconstraints.py \
	    --debug \
	    asgard-prov.ttl \
	    > _$@ \
	    2>&1
	mv _$@ $@
