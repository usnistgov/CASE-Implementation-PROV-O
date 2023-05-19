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

__version__ = "0.3.1"

import argparse
import importlib.resources
import logging
import os
import typing
import uuid

import case_utils.inherent_uuid
import case_utils.local_uuid
import rdflib.plugins.sparql
from case_utils.namespace import (
    NS_CASE_INVESTIGATION,
    NS_RDF,
    NS_UCO_ACTION,
    NS_UCO_CORE,
    NS_UCO_IDENTITY,
)

from . import queries

_logger = logging.getLogger(os.path.basename(__file__))

NS_PROV = rdflib.PROV


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--allow-empty-results", action="store_true")
    parser.add_argument(
        "--kb-iri",
        default="http://example.org/kb/",
        help="Fallback IRI to use for the knowledge base namespace.",
    )
    parser.add_argument(
        "--kb-prefix",
        default="kb",
        help="Knowledge base prefix for compacted IRI form.  If this prefix is already in the input graph, --kb-iri will be ignored.",
    )
    parser.add_argument(
        "--use-deterministic-uuids",
        action="store_true",
        help="Use UUIDs computed using the case_utils.inherent_uuid module.",
    )
    parser.add_argument("out_file")
    parser.add_argument("in_graph", nargs="+")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    case_utils.local_uuid.configure()

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

    # Determine knowledge base prefix for new inherent nodes.
    if args.kb_prefix in nsdict:
        NS_KB = rdflib.Namespace(nsdict[args.kb_prefix])
    elif args.kb_iri in nsdict.values():
        NS_KB = rdflib.Namespace(args.kb_iri)
    else:
        NS_KB = rdflib.Namespace(args.kb_iri)
        out_graph.bind(args.kb_prefix, NS_KB)

    # Resource file loading c/o https://stackoverflow.com/a/20885799
    query_filenames = []
    for resource_filename in importlib.resources.contents(queries):
        if not resource_filename.startswith("construct-"):
            continue
        if not resource_filename.endswith(".sparql"):
            continue
        query_filenames.append(resource_filename)
    assert len(query_filenames) > 0, "Failed to load list of query files."

    n_activity: rdflib.URIRef
    n_agent: rdflib.URIRef
    n_entity: rdflib.URIRef

    # Generate inherent nodes.
    n_actions: typing.Set[rdflib.URIRef] = set()
    for n_action in in_graph.subjects(
        NS_RDF.type, NS_CASE_INVESTIGATION.InvestigativeAction
    ):
        assert isinstance(n_action, rdflib.URIRef)
        n_actions.add(n_action)
    for n_action in sorted(n_actions):
        assert isinstance(n_action, rdflib.URIRef)
        action_inherence_uuid = case_utils.inherent_uuid.inherence_uuid(n_action)

        # Generate Ends.
        n_end: typing.Optional[rdflib.IdentifiedNode] = None
        for n_value in in_graph.objects(n_action, NS_PROV.qualifiedEnd):
            assert isinstance(n_value, rdflib.term.IdentifiedNode)
            n_end = n_value
        if n_end is None:
            if args.use_deterministic_uuids:
                end_uuid = str(
                    uuid.uuid5(action_inherence_uuid, str(NS_PROV.qualifiedEnd))
                )
            else:
                end_uuid = case_utils.local_uuid.local_uuid()
            n_end = NS_KB["End-" + end_uuid]
            out_graph.add((n_action, NS_PROV.qualifiedEnd, n_end))
            out_graph.add((n_end, NS_RDF.type, NS_PROV.End))
            for l_object in in_graph.objects(n_action, NS_UCO_ACTION.endTime):
                out_graph.add((n_end, NS_PROV.atTime, l_object))

        # Generate Starts.
        n_start: typing.Optional[rdflib.IdentifiedNode] = None
        for n_value in in_graph.objects(n_action, NS_PROV.qualifiedStart):
            assert isinstance(n_value, rdflib.term.IdentifiedNode)
            n_start = n_value
        if n_start is None:
            if args.use_deterministic_uuids:
                start_uuid = str(
                    uuid.uuid5(action_inherence_uuid, str(NS_PROV.qualifiedStart))
                )
            else:
                start_uuid = case_utils.local_uuid.local_uuid()
            n_start = NS_KB["Start-" + start_uuid]
            out_graph.add((n_action, NS_PROV.qualifiedStart, n_start))
            out_graph.add((n_start, NS_RDF.type, NS_PROV.Start))
            for l_object in in_graph.objects(n_action, NS_UCO_ACTION.startTime):
                out_graph.add((n_start, NS_PROV.atTime, l_object))

        qualified_association_uuid_namespace = uuid.uuid5(
            action_inherence_uuid, str(NS_PROV.qualifiedAssociation)
        )
        for n_agency_predicate in [
            NS_UCO_ACTION.instrument,
            NS_UCO_ACTION.performer,
        ]:
            _n_agents: typing.Set[rdflib.URIRef] = set()
            for _n_agent in in_graph.objects(n_action, n_agency_predicate):
                assert isinstance(_n_agent, rdflib.URIRef)
                _n_agents.add(_n_agent)
            for n_agent in sorted(_n_agents):
                if args.use_deterministic_uuids:
                    association_uuid = str(
                        uuid.uuid5(qualified_association_uuid_namespace, str(n_agent))
                    )
                else:
                    association_uuid = case_utils.local_uuid.local_uuid()
                n_association = NS_KB["Association-" + association_uuid]
                out_graph.add((n_action, NS_PROV.qualifiedAssociation, n_association))
                out_graph.add((n_association, NS_RDF.type, NS_PROV.Association))
                out_graph.add((n_association, NS_PROV.agent, n_agent))

        # A uco-action:Action may have at most one performer, and any number of instruments.
        qualified_delegation_uuid_namespace = uuid.uuid5(
            action_inherence_uuid, str(NS_PROV.qualifiedDelegation)
        )
        for n_performer in in_graph.objects(n_action, NS_UCO_ACTION.performer):
            delegation_for_performer_uuid_namespace = uuid.uuid5(
                qualified_delegation_uuid_namespace, str(n_performer)
            )
            for n_instrument in in_graph.objects(n_action, NS_UCO_ACTION.instrument):
                if args.use_deterministic_uuids:
                    delegation_uuid = str(
                        uuid.uuid5(
                            delegation_for_performer_uuid_namespace, str(n_instrument)
                        )
                    )
                else:
                    delegation_uuid = case_utils.local_uuid.local_uuid()
                n_delegation = NS_KB["Delegation-" + delegation_uuid]
                out_graph.add((n_instrument, NS_PROV.qualifiedDelegation, n_delegation))
                out_graph.add((n_delegation, NS_RDF.type, NS_PROV.Delegation))
                out_graph.add((n_delegation, NS_PROV.agent, n_performer))
                out_graph.add((n_delegation, NS_PROV.hadActivity, n_action))

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
        for row_no, row in enumerate(construct_query_result):
            if row_no == 0:
                _logger.debug("row[0] = %r." % (row,))
            tally = row_no + 1
            # TODO: Handle type review with implementation to RDFLib Issue 2283.
            # https://github.com/RDFLib/rdflib/issues/2283
            out_graph.add(row)  # type: ignore
    if tally == 0:
        if not args.allow_empty_results:
            raise ValueError("Failed to construct any results.")

    # Run inherent qualification steps that are dependent on PROV-O properties being present.
    # Store in tmp_triples, to avoid modifying graph while iterating over graph.
    tmp_triples: typing.Set[
        typing.Tuple[rdflib.term.Node, rdflib.term.Node, rdflib.term.Node]
    ] = set()

    # Build Attributions.
    # Modeling assumption over PROV-O: An Attribution inheres in both the Entity and Agent.
    for triple in sorted(out_graph.triples((None, NS_PROV.wasAttributedTo, None))):
        assert isinstance(triple[0], rdflib.URIRef)
        assert isinstance(triple[2], rdflib.URIRef)
        n_entity = triple[0]
        n_agent = triple[2]

        n_attribution: typing.Optional[rdflib.term.IdentifiedNode] = None
        for n_object in in_graph.objects(n_entity, NS_PROV.qualifiedAttribution):
            if (n_object, NS_PROV.agent, n_agent) in in_graph:
                assert isinstance(n_object, rdflib.term.IdentifiedNode)
                n_attribution = n_object
        if n_attribution is not None:
            # No creation necessary.
            continue

        entity_uuid_namespace = case_utils.inherent_uuid.inherence_uuid(n_entity)
        qualifed_attribution_uuid_namespace = uuid.uuid5(
            entity_uuid_namespace, str(NS_PROV.qualifiedAttribution)
        )

        if args.use_deterministic_uuids:
            attribution_uuid = str(
                uuid.uuid5(qualifed_attribution_uuid_namespace, str(n_agent))
            )
        else:
            attribution_uuid = case_utils.local_uuid.local_uuid()

        n_attribution = NS_KB["Attribution-" + attribution_uuid]
        tmp_triples.add((n_entity, NS_PROV.qualifiedAttribution, n_attribution))
        tmp_triples.add((n_attribution, NS_RDF.type, NS_PROV.Attribution))
        tmp_triples.add((n_attribution, NS_PROV.agent, n_agent))

    # Build Communications.
    # Modeling assumption over PROV-O: A Communication inheres in both the informed Activity and informant Activity.
    for triple in sorted(out_graph.triples((None, NS_PROV.wasInformedBy, None))):
        assert isinstance(triple[0], rdflib.URIRef)
        assert isinstance(triple[2], rdflib.URIRef)
        n_informed_activity = triple[0]
        n_informant_activity = triple[2]

        n_communication: typing.Optional[rdflib.term.IdentifiedNode] = None
        for n_object in in_graph.objects(
            n_informed_activity, NS_PROV.qualifiedCommunication
        ):
            if (n_object, NS_PROV.activity, n_informant_activity) in in_graph:
                assert isinstance(n_object, rdflib.term.IdentifiedNode)
                n_communication = n_object
        if n_communication is not None:
            # No creation necessary.
            continue

        informed_activity_uuid_namespace = case_utils.inherent_uuid.inherence_uuid(
            n_informed_activity
        )
        qualifed_communication_uuid_namespace = uuid.uuid5(
            informed_activity_uuid_namespace, str(NS_PROV.qualifiedCommunication)
        )

        if args.use_deterministic_uuids:
            communication_uuid = str(
                uuid.uuid5(
                    qualifed_communication_uuid_namespace, str(n_informant_activity)
                )
            )
        else:
            communication_uuid = case_utils.local_uuid.local_uuid()

        n_communication = NS_KB["Communication-" + communication_uuid]
        tmp_triples.add(
            (n_informed_activity, NS_PROV.qualifiedCommunication, n_communication)
        )
        tmp_triples.add((n_communication, NS_RDF.type, NS_PROV.Communication))
        tmp_triples.add((n_communication, NS_PROV.activity, n_informant_activity))

    # Build Derivations.
    # Modeling assumption over PROV-O: A Derivation inheres in both the input Entity and output Entity.
    for triple in sorted(out_graph.triples((None, NS_PROV.wasDerivedFrom, None))):
        assert isinstance(triple[0], rdflib.URIRef)
        assert isinstance(triple[2], rdflib.URIRef)
        n_action_result = triple[0]
        n_action_object = triple[2]

        n_derivation: typing.Optional[rdflib.term.IdentifiedNode] = None
        for n_object in in_graph.objects(n_action_result, NS_PROV.qualifiedDerivation):
            if (n_object, NS_PROV.entity, n_action_object) in in_graph:
                assert isinstance(n_object, rdflib.term.IdentifiedNode)
                n_derivation = n_object
        if n_derivation is not None:
            # No creation necessary.
            continue

        action_result_uuid_namespace = case_utils.inherent_uuid.inherence_uuid(
            n_action_result
        )
        qualifed_derivation_uuid_namespace = uuid.uuid5(
            action_result_uuid_namespace, str(NS_PROV.qualifiedDerivation)
        )

        if args.use_deterministic_uuids:
            derivation_uuid = str(
                uuid.uuid5(qualifed_derivation_uuid_namespace, str(n_action_object))
            )
        else:
            derivation_uuid = case_utils.local_uuid.local_uuid()

        n_derivation = NS_KB["Derivation-" + derivation_uuid]
        tmp_triples.add((n_action_result, NS_PROV.qualifiedDerivation, n_derivation))
        tmp_triples.add((n_derivation, NS_RDF.type, NS_PROV.Derivation))
        tmp_triples.add((n_derivation, NS_PROV.entity, n_action_object))
        for n_object in out_graph.objects(n_action_result, NS_PROV.wasGeneratedBy):
            tmp_triples.add((n_derivation, NS_PROV.hadActivity, n_object))

    # Build Generations.
    # Modeling assumption over PROV-O: A Generation inheres solely in the Entity.
    for triple in sorted(out_graph.triples((None, NS_PROV.wasGeneratedBy, None))):
        assert isinstance(triple[0], rdflib.URIRef)
        assert isinstance(triple[2], rdflib.URIRef)
        n_entity = triple[0]
        n_activity = triple[2]

        n_generation: typing.Optional[rdflib.term.IdentifiedNode] = None
        for n_object in in_graph.objects(n_entity, NS_PROV.qualifiedGeneration):
            assert isinstance(n_object, rdflib.term.IdentifiedNode)
            n_generation = n_object
        if n_generation is not None:
            # No creation necessary.
            continue

        entity_uuid_namespace = case_utils.inherent_uuid.inherence_uuid(n_entity)
        qualifed_generation_uuid_namespace = uuid.uuid5(
            entity_uuid_namespace, str(NS_PROV.qualifiedGeneration)
        )

        if args.use_deterministic_uuids:
            generation_uuid = str(
                uuid.uuid5(qualifed_generation_uuid_namespace, str(n_activity))
            )
        else:
            generation_uuid = case_utils.local_uuid.local_uuid()

        n_generation = NS_KB["Generation-" + generation_uuid]
        tmp_triples.add((n_entity, NS_PROV.qualifiedGeneration, n_generation))
        tmp_triples.add((n_generation, NS_RDF.type, NS_PROV.Generation))
        tmp_triples.add((n_generation, NS_PROV.activity, n_activity))

    # Build Usages.
    # Modeling assumption over PROV-O: An Attribution inheres in both the Activity and Entity.
    for triple in sorted(out_graph.triples((None, NS_PROV.used, None))):
        assert isinstance(triple[0], rdflib.URIRef)
        assert isinstance(triple[2], rdflib.URIRef)
        n_activity = triple[0]
        n_entity = triple[2]

        n_usage: typing.Optional[rdflib.term.IdentifiedNode] = None
        for n_object in in_graph.objects(n_entity, NS_PROV.qualifiedUsage):
            assert isinstance(n_object, rdflib.term.IdentifiedNode)
            n_usage = n_object
        if n_usage is not None:
            # No creation necessary.
            continue

        activity_uuid_namespace = case_utils.inherent_uuid.inherence_uuid(n_activity)
        qualifed_usage_uuid_namespace = uuid.uuid5(
            activity_uuid_namespace, str(NS_PROV.qualifiedUsage)
        )

        if args.use_deterministic_uuids:
            usage_uuid = str(uuid.uuid5(qualifed_usage_uuid_namespace, str(n_entity)))
        else:
            usage_uuid = case_utils.local_uuid.local_uuid()

        n_usage = NS_KB["Usage-" + usage_uuid]
        tmp_triples.add((n_activity, NS_PROV.qualifiedUsage, n_usage))
        tmp_triples.add((n_usage, NS_RDF.type, NS_PROV.Usage))
        tmp_triples.add((n_usage, NS_PROV.entity, n_entity))

    for tmp_triple in tmp_triples:
        out_graph.add(tmp_triple)

    out_graph.serialize(args.out_file)


if __name__ == "__main__":
    main()
