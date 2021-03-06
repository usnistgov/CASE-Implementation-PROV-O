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

example_srcdir := $(qc_srcdir)/dependencies/casework.github.io/examples/owl_trafficking

tests_srcdir := $(top_srcdir)/tests

all: \
  prov-constraints.log \
  owl_trafficking-prov.png \
  owl_trafficking-prov-originals.svg

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

clean:
	@rm -f \
	  *.dot \
	  *.png \
	  *.svg \
	  *.ttl \
	  prov-constraints.log

owl_trafficking-prov.dot: \
  owl_trafficking-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    $< \
	    _$@
	mv _$@ $@

owl_trafficking-prov-focus-extracted-file-uuid-1.dot: \
  owl_trafficking-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    --entity-ancestry http://example.org/kb/extracted-file-uuid-1 \
	    $< \
	    _$@
	mv _$@ $@

owl_trafficking-prov-originals.dot: \
  owl_trafficking-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_dot \
	    --debug \
	    --from-empty-set \
	    $< \
	    _$@
	mv _$@ $@

owl_trafficking-prov.ttl: \
  $(example_srcdir)/owl_trafficking.json \
  $(tests_srcdir)/.venv.done.log
	source $(tests_srcdir)/venv/bin/activate \
	  && case_prov_rdf \
	    --debug \
	    $(example_srcdir)/owl_trafficking.json \
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

prov-constraints.log: \
  $(top_srcdir)/dependencies/prov-check/provcheck/provconstraints.py \
  owl_trafficking-prov.ttl
	source $(tests_srcdir)/venv/bin/activate \
	  && python3 $(top_srcdir)/dependencies/prov-check/provcheck/provconstraints.py \
	    --debug \
	    owl_trafficking-prov.ttl \
	    > _$@ \
	    2>&1
	mv _$@ $@
