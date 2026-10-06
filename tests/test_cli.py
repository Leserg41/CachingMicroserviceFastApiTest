import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from pydantic import ValidationError

from app.cli import CliSettings, load_payload, run_requests
from app.schemas import PayloadCreate


class CliSettingsTests(unittest.TestCase):
    def test_shortcut_arguments_parse_and_validate(self) -> None:
        settings = CliSettings(
            _cli_parse_args=[
                "-h",
                "https://example.com/api",
                "-r",
                "3",
                "-j",
                '{"list1":["a"],"list2":["b"]}',
            ]
        )

        self.assertEqual(str(settings.host), "https://example.com/api")
        self.assertEqual(settings.repeat, 3)
        self.assertEqual(load_payload(settings).list1, ["a"])

    def test_help_flag_does_not_require_input(self) -> None:
        settings = CliSettings(_cli_parse_args=["--help"])

        self.assertTrue(settings.help)

    def test_rejects_missing_and_multiple_input_sources(self) -> None:
        with self.assertRaises(ValidationError):
            CliSettings(_cli_parse_args=[])

        with self.assertRaises(ValidationError):
            CliSettings(
                _cli_parse_args=[
                    "--json",
                    '{"list1":[],"list2":[]}',
                    "--input",
                    "payload.json",
                ]
            )

    def test_json_payload_uses_api_schema_validation(self) -> None:
        settings = CliSettings(
            _cli_parse_args=[
                "--json",
                '{"list1":["a"],"list2":[]}',
            ]
        )

        with self.assertRaises(ValidationError):
            load_payload(settings)

    def test_reads_input_file(self) -> None:
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "payload.json"
            input_file.write_text(
                '{"list1":["a"],"list2":["b"]}',
                encoding="utf-8",
            )
            settings = CliSettings(
                _cli_parse_args=["-i", str(input_file)]
            )

            self.assertEqual(load_payload(settings).list2, ["b"])

    def test_reads_stdin_when_input_is_dash(self) -> None:
        settings = CliSettings(_cli_parse_args=["-i", "-"])
        with patch("app.cli.sys.stdin", StringIO('{"list1":[],"list2":[]}')):
            payload = load_payload(settings)

        self.assertEqual(payload.list1, [])

    def test_repeat_submits_and_reads_each_result(self) -> None:
        settings = CliSettings(
            _cli_parse_args=[
                "--json",
                '{"list1":["a"],"list2":["b"]}',
                "--repeat",
                "2",
            ]
        )
        payload = PayloadCreate(list1=["a"], list2=["b"])

        with patch("app.cli.httpx.Client") as client_factory:
            client = client_factory.return_value.__enter__.return_value
            client.post.return_value.json.return_value = 7
            client.get.return_value.json.return_value = {
                "output": "a,b",
            }

            results = run_requests(settings, payload)

        self.assertEqual(len(results), 2)
        self.assertEqual(client.post.call_count, 2)
        self.assertEqual(client.get.call_count, 2)
        client.get.assert_any_call("payloads/7")
        self.assertEqual(results[0]["payload"]["output"], "a,b")


if __name__ == "__main__":
    unittest.main()