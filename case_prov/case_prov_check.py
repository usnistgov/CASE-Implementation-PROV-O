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
This script generates a supplemental graph of CASE-specific provenance review matters.

This script's corresponding shapes file will need community input on how to handle provenance chains expected to be broken, such as in partial data sharing.

This script is an adaptation of `case_validate`, part of the CASE Python Utilities:
https://github.com/casework/CASE-Utilities-Python

`case_validate` is an adaptation of the pySHACL command line tool, available here:
https://github.com/RDFLib/pySHACL

The pySHACL command line interface is further adapted since its adaptations in `case_validate`.
"""

__version__ = "0.1.0"

import argparse
import importlib.resources
import logging
import os
import sys
import typing

import pyshacl  # type: ignore
import rdflib.util

from . import shapes

_logger = logging.getLogger(os.path.basename(__file__))


def main() -> None:
    parser = argparse.ArgumentParser(description="CASE provenance reviewer")

    # Configure debug logging before running parse_args, because there
    # could be an error raised before the construction of the argument
    # parser.
    logging.basicConfig(
        level=logging.DEBUG
        if ("--debug" in sys.argv or "-d" in sys.argv)
        else logging.INFO
    )

    # Add arguments specific to case_prov_check.
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument(
        "--ontology-graph",
        action="append",
        help="Combined ontology (i.e. subclass hierarchy) and shapes (SHACL) file, in any format accepted by rdflib recognized by file extension (e.g. .ttl).  Will supplement ontology selected by --built-version.  Can be given multiple times.",
    )

    # Inherit arguments from pyshacl.  (Sorted by '--' form.)
    parser.add_argument(
        "--abort",
        action="store_true",
        help="(As with pyshacl CLI) Abort on first invalid data.",
    )
    parser.add_argument(
        "-w",
        "--allow-warnings",
        action="store_true",
        help="(As with pyshacl CLI) Shapes marked with severity of Warning or Info will not cause result to be invalid.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=("human", "turtle", "xml", "json-ld", "nt", "n3"),
        default="human",
        help="(ALMOST as with pyshacl CLI) Choose an output format. Default is \"human\".  Difference: 'table' not provided.",
    )
    parser.add_argument(
        "-im",
        "--imports",
        action="store_true",
        help="(As with pyshacl CLI) Allow import of sub-graphs defined in statements with owl:imports.",
    )
    parser.add_argument(
        "-i",
        "--inference",
        choices=("none", "rdfs", "owlrl", "both"),
        default="none",
        help='(As with pyshacl CLI) Choose a type of inferencing to run against the Data Graph before validating. Default is "none".',
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        nargs="?",
        type=argparse.FileType("x"),
        help='(ALMOST as with pyshacl CLI) Send output to a file.  If absent, output will be written to stdout.  Difference: If specified, file is expected not to exist.  Clarification: Does NOT influence --format flag\'s default value of "human".  (I.e., any machine-readable serialization format must be specified with --format.)',
        default=sys.stdout,
    )

    parser.add_argument("in_graph", nargs="+")

    args = parser.parse_args()

    data_graph = rdflib.Graph()
    for in_graph in args.in_graph:
        _logger.debug("in_graph = %r.", in_graph)
        data_graph.parse(in_graph)

    # Resource file loading c/o https://stackoverflow.com/a/20885799
    shape_filenames = []
    for resource_filename in importlib.resources.contents(shapes):
        if resource_filename.endswith(".ttl"):
            shape_filenames.append(resource_filename)
    assert len(shape_filenames) > 0, "Failed to load list of shapes files."

    # Do initial ontology_graph load from any supplementally requested ontology-graph files.
    # Such graphs may be an influence in OWL or RDFS inferencing.
    ontology_graph = rdflib.Graph()
    if args.ontology_graph:
        for arg_ontology_graph in args.ontology_graph:
            _logger.debug("arg_ontology_graph = %r.", arg_ontology_graph)
            ontology_graph.parse(arg_ontology_graph)
    # Load case_prov shapes into ontology_graph.
    for shape_filename in shape_filenames:
        _logger.debug("Loading shapes in %r." % shape_filename)
        shapes_text = importlib.resources.read_text(shapes, shape_filename)
        ontology_graph.parse(data=shapes_text, format="turtle")

    # Determine output format.
    # pySHACL's determination of output formatting is handled solely
    # through the -f flag.  Other CASE CLI tools handle format
    # determination by output file extension.  case_validate deferred
    # to pySHACL behavior, as other CASE tools don't (at the time of
    # this writing) have the value "human" as an output format.
    # case_prov_check continues that pattern.
    validator_kwargs: typing.Dict[str, str] = dict()
    if args.format != "human":
        validator_kwargs["serialize_report_graph"] = args.format

    validate_result: typing.Tuple[
        bool, typing.Union[Exception, bytes, str, rdflib.Graph], str
    ]
    validate_result = pyshacl.validate(
        data_graph,
        shacl_graph=ontology_graph,
        ont_graph=ontology_graph,
        inference=args.inference,
        abort_on_first=args.abort,
        allow_warnings=True if args.allow_warnings else False,
        debug=True if args.debug else False,
        do_owl_imports=True if args.imports else False,
        **validator_kwargs
    )

    # Relieve RAM of the data graph after validation has run.
    del data_graph

    conforms = validate_result[0]
    validation_graph = validate_result[1]
    validation_text = validate_result[2]

    # NOTE: The output logistics code is adapted from pySHACL's file
    # pyshacl/cli.py.  This section should be monitored for code drift.
    if args.format == "human":
        args.output.write(validation_text)
    else:
        if isinstance(validation_graph, rdflib.Graph):
            raise NotImplementedError(
                "rdflib.Graph expected not to be created from --format value %r."
                % args.format
            )
        elif isinstance(validation_graph, bytes):
            args.output.write(validation_graph.decode("utf-8"))
        elif isinstance(validation_graph, str):
            args.output.write(validation_graph)
        else:
            raise NotImplementedError(
                "Unexpected result type returned from validate: %r."
                % type(validation_graph)
            )

    sys.exit(0 if conforms else 1)


if __name__ == "__main__":
    main()
