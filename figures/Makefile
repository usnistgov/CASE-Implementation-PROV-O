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

top_srcdir := $(shell cd .. ; pwd)

all: \
  readme-activities.svg \
  readme-attribution.svg \
  readme-provenance-records.svg

.PRECIOUS: \
  readme-activities.dot \
  readme-attribution.dot \
  readme-provenance-records.dot

%.svg: \
  %.dot
	dot -o _$@ -T svg $<
	mv _$@ $@

clean:
	@rm -f \
	  *.dot \
	  *.svg

readme-activities.dot: \
  readme-activities.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py \
  $(top_srcdir)/tests/.venv.done.log
	source $(top_srcdir)/tests/venv/bin/activate \
	  && case_prov_dot \
	    --omit-empty-set \
	    $< \
	    _$@
	mv _$@ $@

readme-attribution.dot: \
  readme-attribution.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py \
  $(top_srcdir)/tests/.venv.done.log
	source $(top_srcdir)/tests/venv/bin/activate \
	  && case_prov_dot \
	    --dash-unqualified \
	    --omit-empty-set \
	    $< \
	    _$@
	mv _$@ $@

readme-provenance-records.dot: \
  readme-provenance-records.ttl \
  $(top_srcdir)/case_prov/case_prov_dot.py \
  $(top_srcdir)/tests/.venv.done.log
	source $(top_srcdir)/tests/venv/bin/activate \
	  && case_prov_dot \
	    --omit-empty-set \
	    $< \
	    _$@
	mv _$@ $@
