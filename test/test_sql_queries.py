import unittest
from unittest import mock
import psycopg2

import sql_queries as SQL

class TestSQLQueries(unittest.TestCase):

    @mock.patch("psycopg2.connect")
    def test_get_species_id(self, connect):
        assert connect is psycopg2.connect

        connect.return_value.cursor.return_value.fetchone.return_value = (0,)
        postgres_connection = connect()
        species_id = SQL.get_species_id(postgres_connection, "Homo sapiens")
    
        assert species_id == 0

        connect.return_value.cursor.return_value.execute.assert_called_once_with("""
        SELECT species_id
        FROM items.species
        WHERE UPPER(compact_name) = UPPER(%s);
        """, ("Homo sapiens",))

if __name__ == "__main__":
    unittest.main()
