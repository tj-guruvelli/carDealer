"""Behavior tests for health_check.py.

The network is never touched: probe() is stubbed and run() is given a fake env.
What matters here is the redaction guarantee and the pass/skip/fail semantics —
a health check that leaks a key while reporting "OK" is worse than no check.
"""

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import health_check


class Redaction(unittest.TestCase):
    def test_masks_a_key_appearing_in_a_url(self):
        key = "ljx7qt5px_we6641e0n_zc94e4e2c"
        text = "https://api.carsxe.com/specs?vin=X&key=" + key
        self.assertNotIn(key, health_check.redact(text, [key]))

    def test_masks_every_occurrence(self):
        key = "cv_abcdefghijklmnop"
        text = "{} then again {}".format(key, key)
        self.assertEqual(health_check.redact(text, [key]).count("***REDACTED***"), 2)

    def test_leaves_unrelated_text_alone(self):
        self.assertEqual(health_check.redact("2003 Honda Accord", ["k" * 20]), "2003 Honda Accord")

    def test_ignores_short_strings_so_it_cannot_blank_the_whole_message(self):
        """An empty or tiny secret must not turn every character into a marker."""
        self.assertEqual(health_check.redact("HTTP 401", [""]), "HTTP 401")
        self.assertEqual(health_check.redact("HTTP 401", ["a"]), "HTTP 401")


class RunSemantics(unittest.TestCase):
    def setUp(self):
        self._real_probe = health_check.probe

    def tearDown(self):
        health_check.probe = self._real_probe

    def test_missing_key_is_skip_not_failure(self):
        results = health_check.run(selected="carvector", env={})
        self.assertEqual(results[0]["status"], "SKIP")
        self.assertIn("CARVECTOR_API_KEY", results[0]["detail"])
        self.assertEqual(health_check.exit_code(results), 0)

    def test_a_failure_sets_a_nonzero_exit_code(self):
        health_check.probe = lambda name, config, key: ("FAIL", "HTTP 401 (check the key)")
        results = health_check.run(selected="carsxe", env={"CARSXE_API_KEY": "k" * 20})
        self.assertEqual(health_check.exit_code(results), 1)

    def test_all_passing_exits_zero(self):
        health_check.probe = lambda name, config, key: ("OK", "fine")
        results = health_check.run(env={c["env"]: "k" * 20 for c in health_check.SERVICES.values()})
        self.assertEqual(len(results), len(health_check.SERVICES))
        self.assertEqual(health_check.exit_code(results), 0)

    def test_skips_and_passes_together_still_exit_zero(self):
        health_check.probe = lambda name, config, key: ("OK", "fine")
        results = health_check.run(env={"CARVECTOR_API_KEY": "k" * 20})
        statuses = {r["status"] for r in results}
        self.assertEqual(statuses, {"OK", "SKIP"})
        self.assertEqual(health_check.exit_code(results), 0)


class Output(unittest.TestCase):
    def setUp(self):
        self._real_probe = health_check.probe

    def tearDown(self):
        health_check.probe = self._real_probe

    def test_no_key_appears_in_rendered_output(self):
        key = "cv_supersecretvalue123456"
        health_check.probe = self._real_probe  # unused; run() short-circuits below
        health_check.probe = lambda n, c, k: ("OK", health_check.redact("used " + k, [k]))
        results = health_check.run(selected="carvector", env={"CARVECTOR_API_KEY": key})
        rendered = health_check.render(results)
        self.assertNotIn(key, rendered)
        self.assertIn("***REDACTED***", rendered)

    def test_json_mode_is_parseable(self):
        health_check.probe = lambda n, c, k: ("OK", "fine")
        out = io.StringIO()
        with redirect_stdout(out):
            code = health_check.main(["--json", "--service", "cardog"])
        self.assertEqual(code, 0)
        parsed = json.loads(out.getvalue())
        self.assertEqual(parsed[0]["service"], "cardog")

    def test_every_service_probe_declares_an_env_var_and_a_picker(self):
        """Guards against adding a service and forgetting how to read it."""
        for name, config in health_check.SERVICES.items():
            self.assertTrue(config["env"].endswith("_API_KEY"), name)
            self.assertTrue(callable(config["pick"]), name)
            self.assertIn("{key}", config["url"] + str(config["auth"]), name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
