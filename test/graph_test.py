import unittest
from unittest.mock import patch, MagicMock
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF

from esco.graph import add_module, link_module_teaching_session, link_learning_outcome_skill, EX, add_learning_outcome, \
    add_professor


class TestGraphFunctions(unittest.TestCase):

    @patch('esco.graph.create_uri')
    def test_add_module_creates_correct_triples(self, mock_create_uri):
        g = Graph()
        mock_create_uri.return_value = URIRef("https://imodulebuddy.org/ontology#module1")

        add_module(
            g, "module1", "http://example.com/module1", "Module Title",
            "Module Description", "Type", "Comment", "Competency", "Content"
        )

        module_uri = URIRef("https://imodulebuddy.org/ontology#module1")
        self.assertIn((module_uri, RDF.type, EX.Module), g)
        self.assertIn((module_uri, EX.individualName, Literal("module1")), g)
        self.assertIn((module_uri, EX.moduleLink, Literal("http://example.com/module1")), g)
        self.assertIn((module_uri, EX.moduleTitle, Literal("Module Title")), g)
        self.assertIn((module_uri, EX.moduleDescription, Literal("Module Description")), g)
        self.assertIn((module_uri, EX.moduleType, Literal("Type")), g)
        self.assertIn((module_uri, EX.moduleComment, Literal("Comment")), g)
        self.assertIn((module_uri, EX.competencyToBeAchieved, Literal("Competency")), g)
        self.assertIn((module_uri, EX.moduleContent, Literal("Content")), g)

    @patch('esco.graph.create_uri')
    def test_add_learning_outcome_creates_correct_triples(self, mock_create_uri):
        g = Graph()
        mock_create_uri.return_value = URIRef("https://imodulebuddy.org/ontology#lo1")

        add_learning_outcome(g, "Learning Outcome", "Module Title")

        lo_uri = URIRef("https://imodulebuddy.org/ontology#lo1")
        self.assertIn((lo_uri, RDF.type, EX.LearningOutcome), g)
        self.assertIn((lo_uri, EX.learningOutcome, Literal("Learning Outcome")), g)
        self.assertIn((lo_uri, EX.moduleTitle, Literal("Module Title")), g)

    @patch('esco.graph.create_uri')
    def test_add_professor_creates_correct_triples(self, mock_create_uri):
        g = Graph()
        mock_create_uri.return_value = URIRef("https://imodulebuddy.org/ontology#prof1")

        professor_uuid = add_professor(g, "John", "Doe")

        prof_uri = URIRef("https://imodulebuddy.org/ontology#prof1")
        self.assertIn((prof_uri, RDF.type, EX.Professor), g)
        self.assertIn((prof_uri, EX.professorName, Literal("John")), g)
        self.assertIn((prof_uri, EX.professorSurname, Literal("Doe")), g)
        self.assertIn((prof_uri, EX.uuid, Literal(professor_uuid)), g)

    @patch('esco.graph.create_uri')
    def test_link_module_teaching_session_creates_correct_relationship(self, mock_create_uri):
        g = Graph()
        mock_create_uri.side_effect = [
            URIRef("https://imodulebuddy.org/ontology#module1"),
            URIRef("https://imodulebuddy.org/ontology#ts1")
        ]

        link_module_teaching_session(g, "module1", "ts1")

        module_uri = URIRef("https://imodulebuddy.org/ontology#module1")
        ts_uri = URIRef("https://imodulebuddy.org/ontology#ts1")
        self.assertIn((module_uri, EX.hasSchedule, ts_uri), g)

    @patch('esco.graph.create_uri')
    def test_link_learning_outcome_skill_creates_correct_relationship(self, mock_create_uri):
        g = Graph()
        mock_create_uri.side_effect = [
            URIRef("https://imodulebuddy.org/ontology#lo1"),
            URIRef("https://imodulebuddy.org/ontology#skill1")
        ]

        link_learning_outcome_skill(g, "Module Title", "Learning Outcome", "https://imodulebuddy.org/ontology#skill1")

        lo_uri = URIRef("https://imodulebuddy.org/ontology#lo1")
        skill_uri = URIRef("https://imodulebuddy.org/ontology#skill1")
        self.assertIn((lo_uri, EX.hasSkill, skill_uri), g)
