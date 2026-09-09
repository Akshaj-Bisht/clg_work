import unittest
from pathlib import Path


MIGRATION = Path(__file__).parents[1] / "supabase/migrations/202609090001_initial_schema.sql"


class MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = MIGRATION.read_text(encoding="utf-8")

    def test_declares_resource_and_processing_kinds(self):
        self.assertRegex(self.sql, r"create type public\.resource_kind as enum \([^;]+notebook")
        self.assertRegex(self.sql, r"create type public\.processing_status as enum \([^;]+failed")

    def test_resources_and_files_are_owner_scoped(self):
        self.assertIn("owner_id uuid not null references auth.users(id)", self.sql)
        self.assertIn("resource_id uuid not null references public.resources(id)", self.sql)
        self.assertIn('"users manage own resources"', self.sql)
        self.assertIn('"users manage own files"', self.sql)

    def test_storage_is_private_and_size_limited(self):
        self.assertRegex(self.sql, r"values \('resource-files', 'resource-files', false, 104857600\)")
        self.assertIn("size_bytes bigint not null check (size_bytes > 0 and size_bytes <= 104857600)", self.sql)
        self.assertIn('"users read own resource files"', self.sql)

    def test_subject_resource_relationship_is_authorized(self):
        self.assertIn("subjects.id = subject_id", self.sql)
        self.assertIn("subjects.owner_id = auth.uid()", self.sql)
        self.assertIn("resources.owner_id = auth.uid()", self.sql)


if __name__ == "__main__":
    unittest.main()