
def update_proteins_and_action(graph, params):
    """
    For an existing protein - protein pair, create / update (merge) the given
    action associated with the given pathway.

    If the action's "mode" is the same, the action is updated only if the current
    provided score is higher than the previous.
    """
    
    query = """
        MATCH (protein1:Protein {
            id: {id1}
        })

        MATCH (protein2:Protein {
            id: {id2}
        })

        MERGE (action:Action {
            mode: {mode},
            id1: {id1},
            id2: {id2}
        }) ON CREATE SET action.score = {score}
           ON MATCH SET action.score = CASE action.score
                                       WHEN {score} > action.score
                                       THEN action.score = {score}
                                       ELSE action.score
                                       END

        MERGE (protein1)-[:IN]->(action)
        MERGE (protein2)-[:IN]->(action)

        MERGE (pathway:Pathway {
            set_id: {set_id},
            collection_id: {collection_id},
            comment: {comment},
            title: {title}
        })

        MERGE (protein1)-[:IN]->(pathway)
        MERGE (protein2)-[:IN]->(pathway)

    """
    graph.run(query, params)

def get_protein_subgraph(graph, preferred_name):
    """
    For the given protein, return the Neo4j subgraph
    of the protein and all other associated proteins.
    """

    query_no_actions = """
        MATCH (protein:Protein {
            preferred_name: {preferred_name}
        })-[association:ASSOCIATION]-(other:Protein)
        WHERE NOT (protein)-[:IN]-()
              OR NOT (other)-[:IN]-()
        RETURN protein, other, association
    """

    query_actions = """
        MATCH (protein:Protein {
            preferred_name: {preferred_name}
        })-[association:ASSOCIATION]-(other:Protein)
        MATCH (protein)-[:IN]-(action:Action)
        MATCH (other)-[:IN]-(action:Action)
        MATCH (action)-[:IN]-(pathway:Pathway)
        RETURN protein, other, association, action, pathway
    """

    param_dict = dict(
        preferred_name = preferred_name
    )

    data_no_actions = graph.data(query_no_actions, param_dict)
    data_actions = graph.data(query_actions, param_dict)

    return data_no_actions + data_actions

def update_associations(graph, params):
    """
    For a given protein - protein pair, create / update (merge) the proteins
    and the association between them.
    """

    query = """
        MERGE (protein1:Protein {
            id: {id1},
            external_id: {external_id1},
            annotation: {annotation1},
            preferred_name: {preferred_name1}
        })

        MERGE (protein2:Protein {
            id: {id2},
            external_id: {external_id2},
            annotation: {annotation2},
            preferred_name: {preferred_name2}
        })

        CREATE (protein1)-[a:ASSOCIATION {
            experiments: {experiments},
            database: {database},
            textmining: {textmining},
            coexpression: {coexpression},
            neighborhood: {neighborhood},
            fusion: {fusion},
            cooccurence: {cooccurence},
            combined: {combined_score}
        }]->(protein2)
    """
    graph.run(query, params)

def remove_redundant_properties(graph):
    """
    Remove redundant properties of nodes or edges that have been previously
    used to correctly construct the graph.
    """

    query = """
        MATCH (action:Action)
        REMOVE action.id1, action.id2
    """
    graph.run(query)

def delete_all(graph):
    """
    Delete all nodes and edges from a Neo4j graph.
    """

    query = "MATCH (n) DETACH DELETE (n)"
    graph.run(query)
