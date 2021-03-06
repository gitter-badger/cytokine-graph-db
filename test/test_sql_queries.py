import unittest

import database
import sql_queries as SQL

class TestSQLQueries(unittest.TestCase):

    def test_get_species_id(self):

        postgres_connection, _ = database.connect("test/credentials.test.json")
        species_id = SQL.get_species_id(postgres_connection, "Mus musculus")
    
        self.assertEqual(species_id, 10090)

        postgres_connection.close()

    def test_get_associations(self):

        postgres_connection, _ = database.connect("test/credentials.test.json")

        associations = list(SQL.get_associations(postgres_connection, species_id = 10090, protein1 = "ccl5", protein2 = "ccr5"))

        self.assertEqual(len(associations), 1)

        association = associations[0]

        self.assertEqual(association["id1"], 2100220)
        self.assertEqual(association["id2"], 2111533)
        self.assertEqual(association["external_id1"], "10090.ENSMUSP00000039600")
        self.assertEqual(association["external_id2"], "10090.ENSMUSP00000107069")
        self.assertEqual(association["preferred_name1"], "Ccl5")
        self.assertEqual(association["preferred_name2"], "Ccr5")
        self.assertEqual(
            association["annotation1"],
            "Chemokine (C-C motif) ligand 5; "
            "Chemoattractant for blood monocytes, memory T-helper cells and eosinophils. Causes "
            "the release of histamine from basophils and activates eosinophils. May activate "
            "several chemokine receptors including CCR1, CCR3, CCR4 and CCR5. May also be an "
            "agonist of the G protein-coupled receptor GPR75. Together with GPR75, may play a "
            "role in neuron survival through activation of a downstream signaling pathway "
            "involving the PI3, Akt and MAP kinases. By activating GPR75 may also play a role in "
            "insulin secretion by islet cells"
        )
        self.assertEqual(
            association["annotation2"],
            "Chemokine (C-C motif) receptor 5; Receptor for a number of inflammatory CC-chemokines "
            "including MIP-1-alpha, MIP-1-beta and RANTES and subsequently transduces a signal "
            "by increasing the intracellular calcium ion level. May play a role in the control of "
            "granulocytic lineage proliferation or differentiation (By similarity)"
        )
        self.assertEqual(association["combined_score"], 993)
        self.assertEqual(
            association["evidence_scores"],
            [
                [6, 92],   # array_score
                [7, 52],   # array_score_transferred
                [9, 111],  # experimental_score_transferred
                [10, 900], # database_score
                [12, 906], # textmining_score
                [13, 278]  # textmining_score_transferred
            ]
        )

        postgres_connection.close()

    def test_get_actions_and_pathways(self):

        postgres_connection, _ = database.connect("test/credentials.test.json")

        actions_and_pathways = list(SQL.get_actions_and_pathways(postgres_connection, species_id = 10090, protein1 = "ccr5", protein2 = "ccl5"))

        self.assertTrue(len(actions_and_pathways) >= 5)

        for ap in actions_and_pathways:
            if ap["mode"] == "activation":
                self.assertEqual(ap["score"], 849)
                # self.assertEqual(ap["title"], "annotated pathway (KEGG)")
                # self.assertEqual(ap["comment"], "Name: Cytokine-cytokine receptor interaction")
            elif ap["mode"] == "binding":
                self.assertEqual(ap["score"], 849)
                # self.assertEqual(ap["title"], "annotated pathway (KEGG)")
                # self.assertEqual(ap["comment"], "Name: Chemokine signaling pathway")
            elif ap["mode"] == "catalysis":
                self.assertEqual(ap["score"], 278)
            elif ap["mode"] == "ptmod":
                self.assertEqual(ap["score"], 171)
            elif ap["mode"] == "reaction":
                self.assertIn(ap["score"], (922, 278))
                # self.assertEqual(ap["title"], "curated pathway")
                # self.assertEqual(ap["comment"], "Biochemical Reaction: The Ligand:GPCR:Gi complex dissociates")

        postgres_connection.close()

if __name__ == "__main__":
    unittest.main()
