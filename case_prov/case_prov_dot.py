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
This script renders PROV-O elements of a graph according to the graphic design elements suggested by the PROV-O documentation page, Figure 1.
"""

# TODO - The label adjustment with "ID - " is a hack.  A hyphen forces
# pydot to quote the label string.  Colons don't.  Hence, if the label
# string is just alphanumeric characters and colons, the string won't
# get quoted.  This turns out to be a dot syntax error.  Need to report
# this upstream to pydot.

__version__ = "0.3.0"

import argparse
import collections
import copy
import hashlib
import logging
import os
import pprint
import textwrap
import typing

import prov.constants  # type: ignore
import prov.dot  # type: ignore
import pydot  # type: ignore
import rdflib.plugins.sparql
from case_utils.namespace import NS_CASE_INVESTIGATION

_logger = logging.getLogger(os.path.basename(__file__))

NS_PROV = rdflib.Namespace("http://www.w3.org/ns/prov#")
NS_RDFS = rdflib.RDFS

# This one isn't among the prov constants.
PROV_COLLECTION = NS_PROV.Collection


def clone_style(prov_constant: rdflib.URIRef) -> typing.Dict[str, str]:
    retval: typing.Dict[str, str]
    if prov_constant == PROV_COLLECTION:
        retval = copy.deepcopy(prov.dot.DOT_PROV_STYLE[prov.constants.PROV_ENTITY])
    else:
        retval = copy.deepcopy(prov.dot.DOT_PROV_STYLE[prov_constant])

    # Adjust shapes and colors.
    if prov_constant == PROV_COLLECTION:
        retval["shape"] = "folder"
        retval["fillcolor"] = "khaki3"
    elif prov_constant == prov.constants.PROV_ENTITY:
        # This appeared to be the closest color name to the hex constant.
        retval["fillcolor"] = "khaki1"
    elif prov_constant == prov.constants.PROV_COMMUNICATION:
        retval["color"] = "blue3"

    return retval


def iri_to_gv_node_id(iri: str) -> str:
    hasher = hashlib.sha256()
    hasher.update(iri.encode())
    return "_" + hasher.hexdigest()


def iri_to_short_iri(iri: str) -> str:
    return iri.replace("http://example.org/kb/", "kb:").replace(
        "http://www.w3.org/ns/prov#", "prov:"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--dash-unqualified",
        action="store_true",
        help="Use dash-style edges for graph nodes not also related by qualifying Influences.",
    )
    parser.add_argument(
        "--query-ancestry",
        help="Visualize the ancestry of the nodes returned by the SPARQL query in this file.  Query must be a SELECT that returns non-blank nodes.",
    )
    parser.add_argument(
        "--entity-ancestry",
        help="Visualize the ancestry of the node with this IRI.  If absent, entire graph is returned.",
    )  # TODO - Add inverse --entity-progeny as well.
    parser.add_argument("--from-empty-set", action="store_true")
    parser.add_argument("--omit-empty-set", action="store_true")
    parser.add_argument(
        "--wrap-comment",
        type=int,
        nargs="?",
        default=60,
        help="Number of characters to have before a line wrap in rdfs:label renders.",
    )
    subset_group = parser.add_argument_group()
    subset_group.add_argument(
        "--activity-informing",
        action="store_true",
        help="Only display Activity nodes and wasInformedBy relationships.",
    )
    subset_group.add_argument(
        "--agent-delegating",
        action="store_true",
        help="Only display Agent nodes and actedOnBehalfOf relationships.",
    )
    subset_group.add_argument(
        "--entity-deriving",
        action="store_true",
        help="Only display Entity nodes and wasDerivedBy relationships.",
    )
    parser.add_argument("out_dot")
    parser.add_argument("in_graph", nargs="+")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    graph = rdflib.Graph()
    for in_graph_filename in args.in_graph:
        graph.parse(in_graph_filename)

    graph.bind("case-investigation", NS_CASE_INVESTIGATION)
    graph.bind("prov", NS_PROV)

    nsdict = {k: v for (k, v) in graph.namespace_manager.namespaces()}

    # Add a few axioms from PROV-O.
    graph.add((NS_PROV.Collection, NS_RDFS.subClassOf, NS_PROV.Entity))
    graph.add((NS_PROV.Person, NS_RDFS.subClassOf, NS_PROV.Agent))
    graph.add((NS_PROV.SoftwareAgent, NS_RDFS.subClassOf, NS_PROV.Agent))

    # An include-list.
    filter_iris: typing.Optional[typing.Set[str]] = None
    if args.from_empty_set:
        filter_iris = set()
        filter_iris.add("http://www.w3.org/ns/prov#EmptyCollection")
        select_query_actions_text = """\
SELECT ?nDerivingAction
WHERE {
  # Identify action at end of path.
  ?nDerivingAction
    prov:used prov:EmptyCollection ;
    .
}
"""
        select_query_agents_text = """\
SELECT ?nAgent
WHERE {
  # Identify action at end of path.
  ?nDerivingAction
    prov:used prov:EmptyCollection ;
    .

  # Get each agent involved in the chain.
  ?nDerivingAction prov:wasAssociatedWith ?nAssociatedAgent .
  ?nAssociatedAgent prov:actedOnBehalfOf* ?nAgent .

}
"""
        select_query_entities_text = """\
SELECT ?nEntity
WHERE {
  # Identify all entities in chain.
  ?nEntity prov:wasDerivedFrom prov:EmptyCollection .
}
"""
        for (select_query_label, select_query_text) in [
            ("activities", select_query_actions_text),
            ("agents", select_query_agents_text),
            ("entities", select_query_entities_text),
        ]:
            _logger.debug("Running %s filtering query.", select_query_label)
            select_query_object = rdflib.plugins.sparql.processor.prepareQuery(
                select_query_text, initNs=nsdict
            )
            for record in graph.query(select_query_object):
                (n_include,) = record
                filter_iri = n_include.toPython()
                filter_iris.add(filter_iri)
            _logger.debug("len(filter_iris) = %d.", len(filter_iris))
    elif args.entity_ancestry or args.query_ancestry:
        filter_iris = set()
        terminal_iris: typing.Set[str] = set()
        if args.entity_ancestry:
            filter_iris.add(args.entity_ancestry)
            terminal_iris.add(args.entity_ancestry)
        elif args.query_ancestry:
            query_ancestry_text: typing.Optional[str] = None
            with open(args.query_ancestry, "r") as in_fh:
                query_ancestry_text = in_fh.read(2**22)  # 4KiB
            assert query_ancestry_text is not None
            _logger.debug("query_ancestry_text = %r.", query_ancestry_text)
            query_ancestry_object = rdflib.plugins.sparql.processor.prepareQuery(
                query_ancestry_text, initNs=nsdict
            )
            for result in graph.query(query_ancestry_object):
                for result_member in result:
                    if not isinstance(result_member, rdflib.URIRef):
                        raise ValueError(
                            "Query in file %r must return URIRefs."
                            % args.query_ancestry
                        )
                    terminal_iris.add(str(result_member))
        _logger.debug("len(terminal_iris) = %d.", len(terminal_iris))

        select_query_actions_text = """\
SELECT ?nDerivingAction
WHERE {
  # Identify action at end of path.
  ?nEndIRI
    prov:wasGeneratedBy ?nEndAction ;
    .

  # Identify all actions in chain.
  ?nEndAction prov:wasInformedBy* ?nDerivingAction .
}
"""
        select_query_agents_text = """\
SELECT ?nAgent
WHERE {
  # Identify action at end of path.
  ?nEndIRI
    prov:wasGeneratedBy ?nEndAction ;
    .

  # Identify all actions in chain.
  ?nEndAction prov:wasInformedBy* ?nDerivingAction .

  # Get each agent involved in the chain.
  ?nDerivingAction prov:wasAssociatedWith ?nAssociatedAgent .
  ?nAssociatedAgent prov:actedOnBehalfOf* ?nAgent .

}
"""
        select_query_entities_text = """\
SELECT ?nPrecedingEntity
WHERE {
  # Identify all objects in chain.
  ?nEndIRI prov:wasDerivedFrom* ?nPrecedingEntity .
}
"""
        for (select_query_label, select_query_text) in [
            ("activities", select_query_actions_text),
            ("agents", select_query_agents_text),
            ("entities", select_query_entities_text),
        ]:
            _logger.debug("Running %s filtering query.", select_query_label)
            select_query_object = rdflib.plugins.sparql.processor.prepareQuery(
                select_query_text, initNs=nsdict
            )

            for terminal_iri in terminal_iris:
                for record in graph.query(
                    select_query_object,
                    initBindings={"nEndIRI": rdflib.URIRef(terminal_iri)},
                ):
                    (n_include,) = record
                    filter_iri = n_include.toPython()
                    filter_iris.add(filter_iri)
            _logger.debug("len(filter_iris) = %d.", len(filter_iris))
    _logger.debug("filter_iris = %s.", pprint.pformat(filter_iris))

    # The nodes and edges dicts need to store information to construct, not constructed objects.  There is a hidden dependency for edges of a parent graph object not available until after some filtering decisions are made.
    # IRI -> (pydot.Node identifier, kwargs)
    nodes = dict()
    nodes_activities = dict()
    nodes_agents = dict()
    nodes_entities = dict()

    # IRI -> IRI -> short predicate -> (pydot.Edge identifier, kwargs)
    EdgesType = typing.DefaultDict[
        str,
        typing.DefaultDict[
            str, typing.Dict[str, typing.Tuple[str, str, typing.Dict[str, typing.Any]]]
        ],
    ]
    edges: EdgesType = collections.defaultdict(lambda: collections.defaultdict(dict))
    edges_deriving: EdgesType = collections.defaultdict(
        lambda: collections.defaultdict(dict)
    )
    edges_delegating: EdgesType = collections.defaultdict(
        lambda: collections.defaultdict(dict)
    )
    edges_informing: EdgesType = collections.defaultdict(
        lambda: collections.defaultdict(dict)
    )

    wrapper = textwrap.TextWrapper(
        break_long_words=True,
        drop_whitespace=False,
        replace_whitespace=False,
        width=args.wrap_comment,
    )

    # Render Agents.
    select_query_text = """\
SELECT ?nAgent ?lLabel ?lComment
WHERE {
  ?nAgent a/rdfs:subClassOf* prov:Agent .

  OPTIONAL {
    ?nAgent rdfs:label ?lLabel .
  }

  OPTIONAL {
    ?nAgent rdfs:comment ?lComment .
  }
}
"""
    select_query_object = rdflib.plugins.sparql.processor.prepareQuery(
        select_query_text, initNs=nsdict
    )
    for record in graph.query(select_query_object):
        (n_agent, l_label, l_comment) = record
        agent_iri = n_agent.toPython()
        dot_label = "ID - " + iri_to_short_iri(agent_iri)
        if l_label is not None:
            dot_label += "\n" + l_label.toPython()
        if l_comment is not None:
            dot_label += "\n\n" + "\n".join(wrapper.wrap((l_comment.toPython())))
        kwargs = clone_style(prov.constants.PROV_AGENT)
        kwargs["label"] = dot_label
        # _logger.debug("Agent %r.", agent_iri)
        record = (iri_to_gv_node_id(agent_iri), kwargs)
        nodes[agent_iri] = record
        nodes_agents[agent_iri] = record
    # _logger.debug("nodes = %s." % pprint.pformat(nodes))

    # Find Collections, to adjust Entity rendering in the next block.
    collection_iris = {"http://www.w3.org/ns/prov#EmptyCollection"}
    select_query_text = """\
SELECT ?nCollection
WHERE {
  ?nCollection a prov:Collection .
}
"""
    select_query_object = rdflib.plugins.sparql.processor.prepareQuery(
        select_query_text, initNs=nsdict
    )
    for record in graph.query(select_query_object):
        (n_collection,) = record
        collection_iri = n_collection.toPython()
        collection_iris.add(collection_iri)
    # _logger.debug("len(collection_iris) = %d.", len(collection_iris))

    # Render Entities.
    # This loop operates differently from the others, to insert prov:EmptyCollection.
    entity_iri_to_label_comment = dict()
    if not args.omit_empty_set:
        entity_iri_to_label_comment["http://www.w3.org/ns/prov#EmptyCollection"] = (
            None,
            None,
            None,
        )
    select_query_text = """\
SELECT ?nEntity ?lLabel ?lComment ?lExhibitNumber
WHERE {
  ?nEntity a/rdfs:subClassOf* prov:Entity .

  OPTIONAL {
    ?nEntity rdfs:label ?lLabel .
  }

  OPTIONAL {
    ?nEntity rdfs:comment ?lComment .
  }

  OPTIONAL {
    ?nEntity case-investigation:exhibitNumber ?lExhibitNumber .
  }
}
"""
    select_query_object = rdflib.plugins.sparql.processor.prepareQuery(
        select_query_text, initNs=nsdict
    )
    for record in graph.query(select_query_object):
        (n_entity, l_label, l_comment, l_exhibit_number) = record
        entity_iri = n_entity.toPython()
        entity_iri_to_label_comment[entity_iri] = (l_label, l_comment, l_exhibit_number)
    for entity_iri in sorted(entity_iri_to_label_comment):
        (l_label, l_comment, l_exhibit_number) = entity_iri_to_label_comment[entity_iri]
        dot_label = "ID - " + iri_to_short_iri(entity_iri)
        if l_exhibit_number is not None:
            dot_label += "\nExhibit - " + l_exhibit_number.toPython()
        if l_label is not None:
            dot_label += "\n" + l_label.toPython()
        if l_comment is not None:
            dot_label += "\n\n" + "\n".join(wrapper.wrap((l_comment.toPython())))
        if entity_iri in collection_iris:
            kwargs = clone_style(PROV_COLLECTION)
        else:
            kwargs = clone_style(prov.constants.PROV_ENTITY)
        kwargs["label"] = dot_label
        # _logger.debug("Entity %r.", entity_iri)
        record = (iri_to_gv_node_id(entity_iri), kwargs)
        nodes[entity_iri] = record
        nodes_entities[entity_iri] = record

    # Render Activities.
    select_query_text = """\
SELECT ?nActivity ?lLabel ?lComment ?lStartTime ?lEndTime
WHERE {
  ?nActivity a prov:Activity .

  OPTIONAL {
    ?nActivity rdfs:label ?lLabel .
  }

  OPTIONAL {
    ?nActivity rdfs:comment ?lComment .
  }

  OPTIONAL {
    ?nActivity prov:startedAtTime ?lStartTime .
  }

  OPTIONAL {
    ?nActivity prov:endedAtTime ?lEndTime .
  }
}
"""
    select_query_object = rdflib.plugins.sparql.processor.prepareQuery(
        select_query_text, initNs=nsdict
    )
    for record in graph.query(select_query_object):
        (n_activity, l_label, l_comment, l_start_time, l_end_time) = record
        activity_iri = n_activity.toPython()
        dot_label = "ID - " + iri_to_short_iri(activity_iri)
        if l_label is not None:
            dot_label += "\n" + l_label.toPython()
        if l_start_time is not None or l_end_time is not None:
            if l_start_time is None:
                dot_label += "\n (..., "
            else:
                dot_label += "\n [%s, " % l_start_time
            if l_end_time is None:
                dot_label += "...)"
            else:
                dot_label += "%s]" % l_end_time
        if l_comment is not None:
            dot_label += "\n\n" + "\n".join(wrapper.wrap((l_comment.toPython())))
        kwargs = clone_style(prov.constants.PROV_ACTIVITY)
        kwargs["label"] = dot_label
        # _logger.debug("Activity %r.", activity_iri)
        record = (iri_to_gv_node_id(activity_iri), kwargs)
        nodes[activity_iri] = record
        nodes_activities[activity_iri] = record

    def _render_edges(
        select_query_text: str,
        short_edge_label: str,
        kwargs: typing.Dict[str, str],
        supplemental_dict: typing.Optional[EdgesType] = None,
    ) -> None:
        select_query_object = rdflib.plugins.sparql.processor.prepareQuery(
            select_query_text, initNs=nsdict
        )
        for record in graph.query(select_query_object):
            (n_thing_1, n_thing_2) = record
            thing_1_iri = n_thing_1.toPython()
            thing_2_iri = n_thing_2.toPython()
            gv_node_id_1 = iri_to_gv_node_id(thing_1_iri)
            gv_node_id_2 = iri_to_gv_node_id(thing_2_iri)
            record = (gv_node_id_1, gv_node_id_2, kwargs)
            edges[thing_1_iri][thing_2_iri][short_edge_label] = record
            if supplemental_dict is not None:
                supplemental_dict[thing_1_iri][thing_2_iri][short_edge_label] = record

    # Render actedOnBehalfOf.
    select_query_text = """\
SELECT ?nAgent1 ?nAgent2
WHERE {
  ?nAgent1
    prov:actedOnBehalfOf ?nAgent2 ;
    .
}
"""
    kwargs = clone_style(prov.constants.PROV_DELEGATION)
    if args.dash_unqualified:
        kwargs["style"] = "dashed"
    _render_edges(select_query_text, "actedOnBehalfOf", kwargs, edges_delegating)
    if args.dash_unqualified:
        # Render actedOnBehalfOf, with stronger line from Delegation.
        select_query_text = """\
SELECT ?nAgent1 ?nAgent2
WHERE {
  ?nAgent1
    prov:qualifiedDelegation ?nDelegation ;
    .
  ?nDelegation
    a prov:Delegation ;
    prov:agent ?nAgent2 ;
    .
}
"""
        kwargs = clone_style(prov.constants.PROV_DELEGATION)
        _render_edges(select_query_text, "actedOnBehalfOf", kwargs, edges_delegating)

    # Render hadMember.
    select_query_text = """\
SELECT ?nCollection ?nEntity
WHERE {
  ?nCollection
    prov:hadMember ?nEntity ;
    .
}
"""
    kwargs = clone_style(prov.constants.PROV_MEMBERSHIP)
    _render_edges(select_query_text, "hadMember", kwargs)

    # Render used.
    select_query_text = """\
SELECT ?nActivity ?nEntity
WHERE {
  ?nActivity
    prov:used ?nEntity ;
    .
}
"""
    kwargs = clone_style(prov.constants.PROV_USAGE)
    if args.dash_unqualified:
        kwargs["style"] = "dashed"
    _render_edges(select_query_text, "used", kwargs)
    if args.dash_unqualified:
        # Render used, with stronger line from Usage.
        select_query_text = """\
SELECT ?nActivity ?nEntity
WHERE {
  ?nActivity
    prov:qualifiedUsage ?nUsage ;
    .
  ?nUsage
    a prov:Usage ;
    prov:entity ?nEntity
    .
}
"""
        kwargs = clone_style(prov.constants.PROV_USAGE)
        _render_edges(select_query_text, "used", kwargs)

    # Render wasAssociatedWith.
    select_query_text = """\
SELECT ?nActivity ?nAgent
WHERE {
  ?nActivity
    prov:wasAssociatedWith ?nAgent ;
    .
}
"""
    kwargs = clone_style(prov.constants.PROV_ASSOCIATION)
    if args.dash_unqualified:
        kwargs["style"] = "dashed"
    _render_edges(select_query_text, "wasAssociatedWith", kwargs)
    if args.dash_unqualified:
        # Render wasAssociatedWith, with stronger line from Association.
        select_query_text = """\
SELECT ?nActivity ?nAgent
WHERE {
  ?nActivity
    prov:qualifiedAssociation ?nAssociation ;
    .
  ?nAssociation
    a prov:Association ;
    prov:agent ?nAgent ;
    .
}
"""
        kwargs = clone_style(prov.constants.PROV_ASSOCIATION)
        _render_edges(select_query_text, "wasAssociatedWith", kwargs)

    # Render wasAttributedTo.
    select_query_text = """\
SELECT ?nEntity ?nAgent
WHERE {
  ?nEntity
    prov:wasAttributedTo ?nAgent ;
    .
}
"""
    kwargs = {"color": "pink", "label": "wasAttributedTo"}
    kwargs = clone_style(prov.constants.PROV_ATTRIBUTION)
    if args.dash_unqualified:
        kwargs["style"] = "dashed"
    _render_edges(select_query_text, "wasAttributedTo", kwargs)
    if args.dash_unqualified:
        # Render wasAttributedTo, with stronger line from Attribution.
        select_query_text = """\
SELECT ?nEntity ?nAgent
WHERE {
  ?nEntity
    prov:qualifiedAttribution ?nAttribution ;
    .
  ?nAttribution
    a prov:Attribution ;
    prov:agent ?nAgent ;
    .
}
"""
        kwargs = clone_style(prov.constants.PROV_ATTRIBUTION)
        _render_edges(select_query_text, "wasAttributedTo", kwargs)

    # Render wasDerivedFrom.
    select_query_text = """\
SELECT ?nEntity1 ?nEntity2
WHERE {
  ?nEntity1
    prov:wasDerivedFrom ?nEntity2 ;
    .
}
"""
    kwargs = clone_style(prov.constants.PROV_DERIVATION)
    if args.dash_unqualified:
        kwargs["style"] = "dashed"
    _render_edges(select_query_text, "wasDerivedFrom", kwargs, edges_deriving)
    if args.dash_unqualified:
        # Render wasDerivedFrom, with stronger line from Derivation.
        # Note that though PROV-O allows using prov:hadUsage and
        # prov:hadGeneration on a prov:Derivation, those are not currently
        # used on account of a couple matters.
        # * Some of the new nodes need to be referenced by two subjects. Blank
        #   nodes have been observed by at least one RDF engine to be
        #   repeatedly-defined without a blank-node identifier of the form
        #   "_:foo".  Naming new nodes is possible with a UUID binding
        #   ( c/o https://stackoverflow.com/a/55638001 ), but the UUID used by
        #   at least one RDF engine is UUIDv4 and not configurable (without
        #   swapping an imported library's function definition, which this
        #   project has opted to not do), causing many uninformative changes
        #   in each run on any pre-computed sample data.
        #   - A consistent UUID scheme could probably be implemented using
        #     some SPARQL built-in string-casting and hashing functions, but
        #     this is left for future work.
        # * Generating Usage and Generation nodes at the same time as
        #   Derivation nodes creates a requirement on some links being present
        #   that might not be pertinent to one of the Usage or the Generation.
        #   Hence, generating all qualification nodes at the same time could
        #   generate fewer qualification nodes.
        select_query_text = """\
SELECT ?nEntity1 ?nEntity2
WHERE {
  ?nEntity1
    prov:qualifiedDerivation ?nDerivation ;
    .
  ?nDerivation
    a prov:Derivation ;
    prov:entity ?nEntity2 ;
    .
}
"""
        kwargs = clone_style(prov.constants.PROV_DERIVATION)
        _render_edges(select_query_text, "wasDerivedFrom", kwargs, edges_deriving)

    # Render wasGeneratedBy.
    select_query_text = """\
SELECT ?nEntity ?nActivity
WHERE {
  ?nEntity (prov:wasGeneratedBy|^prov:generated) ?nActivity .
}
"""
    kwargs = clone_style(prov.constants.PROV_GENERATION)
    if args.dash_unqualified:
        kwargs["style"] = "dashed"
    _render_edges(select_query_text, "wasGeneratedBy", kwargs)
    if args.dash_unqualified:
        # Render wasGeneratedBy, with stronger line from Generation.
        select_query_text = """\
SELECT ?nEntity ?nActivity
WHERE {
  ?nEntity
    prov:qualifiedGeneration ?nGeneration ;
    .
  ?nGeneration
    a prov:Generation ;
    prov:activity ?nActivity
    .
}
"""
        kwargs = clone_style(prov.constants.PROV_GENERATION)
        _render_edges(select_query_text, "wasGeneratedBy", kwargs)

    # Render wasInformedBy.
    select_query_text = """\
SELECT ?nActivity1 ?nActivity2
WHERE {
  ?nActivity1
    prov:wasInformedBy ?nActivity2 ;
    .
}
"""
    kwargs = clone_style(prov.constants.PROV_COMMUNICATION)
    if args.dash_unqualified:
        kwargs["style"] = "dashed"
    _render_edges(select_query_text, "wasInformedBy", kwargs, edges_informing)
    if args.dash_unqualified:
        # Render wasInformedBy, with stronger line from Communication.
        select_query_text = """\
SELECT ?nActivity1 ?nActivity2
WHERE {
  ?nActivity1
    prov:qualifiedCommunication ?nCommunication ;
    .
  ?nCommunication
    a prov:Communication ;
    prov:activity ?nActivity2
    .
}
"""
        kwargs = clone_style(prov.constants.PROV_COMMUNICATION)
        _render_edges(select_query_text, "wasInformedBy", kwargs, edges_informing)

    dot_graph = pydot.Dot("PROV-O render", graph_type="digraph", rankdir="BT")

    _logger.debug("len(nodes) = %d.", len(nodes))
    _logger.debug("len(edges) = %d.", len(edges))
    _logger.debug("len(nodes_activities) = %d.", len(nodes_activities))
    _logger.debug("len(edges_informing) = %d.", len(edges_informing))
    _logger.debug("len(nodes_agents) = %d.", len(nodes_agents))
    _logger.debug("len(edges_delegating) = %d.", len(edges_delegating))
    _logger.debug("len(nodes_entities) = %d.", len(nodes_entities))
    _logger.debug("len(edges_deriving) = %d.", len(edges_deriving))

    if args.activity_informing:
        restricted_nodes = nodes_activities
        restricted_edges = edges_informing
    elif args.agent_delegating:
        restricted_nodes = nodes_agents
        restricted_edges = edges_delegating
    elif args.entity_deriving:
        restricted_nodes = nodes_entities
        restricted_edges = edges_deriving
    else:
        restricted_nodes = nodes
        restricted_edges = edges

    iris_used = set()
    if filter_iris is None:
        for iri in sorted(restricted_nodes):
            iris_used.add(iri)
        for iri_1 in sorted(restricted_edges.keys()):
            for iri_2 in sorted(restricted_edges[iri_1].keys()):
                iris_used.add(iri_1)
                iris_used.add(iri_2)
    else:
        for iri_1 in sorted(restricted_edges.keys()):
            for iri_2 in sorted(restricted_edges[iri_1].keys()):
                if not (iri_1 in filter_iris and iri_2 in filter_iris):
                    continue
                iris_used.add(iri_1)
                iris_used.add(iri_2)
    _logger.debug("len(iris_used) = %d.", len(iris_used))

    for iri in sorted(iris_used):
        node_id = nodes[iri][0]
        kwargs = nodes[iri][1]
        dot_node = pydot.Node(node_id, **kwargs)
        dot_graph.add_node(dot_node)
    for iri_1 in sorted(iris_used):
        for iri_2 in sorted(edges[iri_1].keys()):
            if iri_2 not in iris_used:
                continue
            for short_edge_label in sorted(edges[iri_1][iri_2]):
                # short_edge_label is intentionally not used aside from as a selector.  Edge labelling is left to pydot.
                record = edges[iri_1][iri_2][short_edge_label]
                node_id_1 = record[0]
                node_id_2 = record[1]
                kwargs = record[2]
                dot_edge = pydot.Edge(node_id_1, node_id_2, **kwargs)
                dot_graph.add_edge(dot_edge)

    dot_graph.write_raw(args.out_dot)


if __name__ == "__main__":
    main()
