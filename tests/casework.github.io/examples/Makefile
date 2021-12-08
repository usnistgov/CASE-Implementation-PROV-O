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

all: \
  all-asgard \
  all-crossover \
  all-owl_trafficking \
  all-urgent_evidence

.PHONY: \
  all-asgard \
  all-crossover \
  all-owl_trafficking \
  all-urgent_evidence \
  check-asgard \
  check-crossover \
  check-owl_trafficking \
  check-urgent_evidence \
  clean-asgard \
  clean-crossover \
  clean-owl_trafficking \
  clean-urgent_evidence

all-asgard:
	$(MAKE) \
	  --directory asgard

all-crossover:
	$(MAKE) \
	  --directory crossover

all-owl_trafficking:
	$(MAKE) \
	  --directory owl_trafficking

all-urgent_evidence:
	$(MAKE) \
	  --directory urgent_evidence

check: \
  check-asgard \
  check-crossover \
  check-owl_trafficking \
  check-urgent_evidence

check-asgard:
	$(MAKE) \
	  --directory asgard \
	  check

check-crossover:
	$(MAKE) \
	  --directory crossover \
	  check

check-owl_trafficking:
	$(MAKE) \
	  --directory owl_trafficking \
	  check

check-urgent_evidence:
	$(MAKE) \
	  --directory urgent_evidence \
	  check

clean: \
  clean-asgard \
  clean-crossover \
  clean-owl_trafficking \
  clean-urgent_evidence

clean-asgard:
	@$(MAKE) \
	  --directory asgard \
	  clean

clean-crossover:
	@$(MAKE) \
	  --directory crossover \
	  clean

clean-owl_trafficking:
	@$(MAKE) \
	  --directory owl_trafficking \
	  clean

clean-urgent_evidence:
	@$(MAKE) \
	  --directory urgent_evidence \
	  clean
