#!/usr/bin/env python3

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

"""
This script executes CONSTRUCT queries, returning a supplemental graph.
"""

__version__ = "0.2.1"

import argparse
import importlib.resources
import logging
import os

import rdflib.plugins.sparql
from case_utils.namespace import (
    NS_CASE_INVESTIGATION,
    NS_UCO_ACTION,
    NS_UCO_CORE,
    NS_UCO_IDENTITY,
)

from . import queries

_logger = logging.getLogger(os.path.basename(__file__))

NS_PROV = rdflib.Namespace("http://www.w3.org/ns/prov#")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--allow-empty-results", action="store_true")
    parser.add_argument("out_file")
    parser.add_argument("in_graph", nargs="+")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    in_graph = rdflib.Graph()
    out_graph = rdflib.Graph()

    for in_graph_filename in args.in_graph:
        in_graph.parse(in_graph_filename)

    # Guarantee prov: and minimal CASE and UCO prefixes are in input and output contexts.
    in_graph.namespace_manager.bind("case-investigation", NS_CASE_INVESTIGATION)
    in_graph.namespace_manager.bind("prov", NS_PROV)
    in_graph.namespace_manager.bind("uco-action", NS_UCO_ACTION)
    in_graph.namespace_manager.bind("uco-core", NS_UCO_CORE)
    in_graph.namespace_manager.bind("uco-identity", NS_UCO_IDENTITY)

    # Inherit prefixes defined in input context dictionary.
    nsdict = {k: v for (k, v) in in_graph.namespace_manager.namespaces()}
    for prefix in nsdict:
        out_graph.namespace_manager.bind(prefix, nsdict[prefix])

    # Resource file loading c/o https://stackoverflow.com/a/20885799
    query_filenames = []
    for resource_filename in importlib.resources.contents(queries):
        if not resource_filename.startswith("construct-"):
            continue
        if not resource_filename.endswith(".sparql"):
            continue
        query_filenames.append(resource_filename)
    assert len(query_filenames) > 0, "Failed to load list of query files."

    # Run all supplementing CONSTRUCT queries.
    tally = 0
    for query_filename in query_filenames:
        _logger.debug("Running query in %r." % query_filename)
        construct_query_text = importlib.resources.read_text(queries, query_filename)
        construct_query_object = rdflib.plugins.sparql.processor.prepareQuery(
            construct_query_text, initNs=nsdict
        )
        # https://rdfextras.readthedocs.io/en/latest/working_with.html
        construct_query_result = in_graph.query(construct_query_object)
        _logger.debug("len(construct_query_result) = %d." % len(construct_query_result))
        for (row_no, row) in enumerate(construct_query_result):
            if row_no == 0:
                _logger.debug("row[0] = %r." % (row,))
            tally = row_no + 1
            out_graph.add(row)
    if tally == 0:
        if not args.allow_empty_results:
            raise ValueError("Failed to construct any results.")

    out_graph.serialize(args.out_file)


if __name__ == "__main__":
    main()
