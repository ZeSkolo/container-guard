import unittest
from core import run

class Tests(unittest.TestCase):

    def test_root(self):
        self.assertGreater(run({'dockerfile': 'FROM python:latest'})['high_count'], 0)

    def test_nonroot(self):
        self.assertTrue(run({'dockerfile': 'FROM scratch\nUSER 10001\nHEALTHCHECK CMD true'})['policy_passed'])

    def test_socket(self):
        self.assertIn('docker_socket', [x['rule'] for x in run({'dockerfile': 'FROM scratch', 'compose': {'services': {'x': {'volumes': ['/var/run/docker.sock:/var/run/docker.sock']}}}})['findings']])

    def test_no_execution(self):
        self.assertIn('base_digest', [x['rule'] for x in run({'dockerfile': 'FROM malicious:latest\nRUN echo never-executed'})['findings']])

    def test_missing_from(self):
        with self.assertRaises(ValueError):
            run({'dockerfile': 'RUN echo hello'})

    def test_final_stage_root(self):
        self.assertGreater(run({'dockerfile': 'FROM python:3.13 AS build\nUSER 10001\nFROM python:3.13'})['high_count'], 0)

    def test_secret_redaction(self):
        self.assertNotIn('test-secret-value', str(run({'dockerfile': 'FROM python:3.13\nENV API_KEY test-secret-value'})))
