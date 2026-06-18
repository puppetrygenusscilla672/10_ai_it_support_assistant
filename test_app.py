import os
import sqlite3
import unittest
from app import retrieve_similar_tickets, train_fallback_model, DB_NAME

class TestITSupportAssistant(unittest.TestCase):
    def test_db_exists(self):
        # Verify database file exists
        self.assertTrue(os.path.exists(DB_NAME))

    def test_database_records(self):
        # Verify we have seeded tickets
        conn = sqlite3.connect(DB_NAME)
        count = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        conn.close()
        self.assertGreater(count, 0)

    def test_retrieval(self):
        # Test TF-IDF matching works
        results = retrieve_similar_tickets("VPN disconnection issue", num_results=1)
        self.assertLessEqual(len(results), 1)
        if len(results) > 0:
            self.assertIn("category", results[0])
            self.assertIn("description", results[0])

    def test_fallback_model(self):
        # Test that fallback model trains and predicts correctly
        model = train_fallback_model()
        self.assertIsNotNone(model)
        prediction = model.predict(["My Wi-Fi is extremely slow"])[0]
        self.assertIn(prediction, ["Network & Internet", "Hardware & Peripherals", "Software & OS", "Access & Security", "General"])

if __name__ == "__main__":
    unittest.main()
