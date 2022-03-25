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

import typing

import rdflib


def test_chain_of_communication() -> None:
    graph = rdflib.Graph()
    graph.parse("urgent_evidence-prov.ttl", format="turtle")
    expected: typing.Set[str] = set()
    computed: typing.Set[str] = set()
    computed_all = set()
    computed_linked = set()
    query_all = """\
SELECT ?nActivity
WHERE {
  ?nActivity a prov:Activity .
}
"""
    for result in graph.query(query_all):
        computed_all.add(result[0].toPython())
    query_linked = """\
SELECT ?nActivity
WHERE {
  ?nActivity prov:wasInformedBy*/prov:used prov:EmptyCollection .
}
"""
    for result in graph.query(query_linked):
        computed_linked.add(result[0].toPython())
    computed = computed_all - computed_linked
    assert expected == computed


def test_chain_of_derivation() -> None:
    graph = rdflib.Graph()
    graph.parse("urgent_evidence-prov.ttl", format="turtle")
    expected: typing.Set[str] = set()
    computed: typing.Set[str] = set()
    computed_all = set()
    computed_linked = set()
    query_all = """\
SELECT ?nEntity
WHERE {
  ?nEntity a prov:Entity .
}
"""
    for result in graph.query(query_all):
        computed_all.add(result[0].toPython())
    query_linked = """\
SELECT ?nEntity
WHERE {
  ?nEntity prov:wasDerivedFrom* prov:EmptyCollection .
}
"""
    for result in graph.query(query_linked):
        computed_linked.add(result[0].toPython())
    computed = computed_all - computed_linked

    # TODO Correct website example after documenting discovery method.
    computed_known_errors = {"http://example.org/kb/file2-uuid-1"}
    assert (
        len(computed & computed_known_errors) > 0
    ), "One known error not found - has it been corrected already?"
    computed -= computed_known_errors

    assert expected == computed
