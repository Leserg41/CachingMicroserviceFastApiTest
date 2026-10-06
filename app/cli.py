import json
import sys
from pathlib import Path
from typing import Annotated

import httpx
from pydantic import Field, HttpUrl, TypeAdapter, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas import PayloadCreate, PayloadOut


class CliSettings(BaseSettings):
    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_implicit_flags=True,
        cli_shortcuts={
            "host": "h",
            "repeat": "r",
            "input": "i",
            "json": "j",
            "output": "o",
        },
        env_prefix="CACHE_CLI_",
        validate_default=True,
    )

    host: HttpUrl = Field(
        default=HttpUrl("http://127.0.0.1:8000"),
        description="Base URL of the service",
    )
    repeat: Annotated[int, Field(ge=1)] = Field(
        default=1,
        description="Number of times to submit the input",
    )
    input: Path | None = Field(
        default=None,
        description='JSON input file, or "-" to read from stdin',
    )
    json_input: str | None = Field(
        default=None,
        alias="json",
        description="JSON input argument",
    )
    output: Path | None = Field(
        default=None,
        description='Output file, or "-" to write to stdout',
    )
    help: bool = Field(
        default=False,
        description="Show this help message and exit",
    )

    @model_validator(mode="after")
    def validate_input_source(self) -> "CliSettings":
        if self.help:
            return self
        if (self.input is None) == (self.json_input is None):
            raise ValueError("provide exactly one of --input or --json")
        return self


def load_payload(settings: CliSettings) -> PayloadCreate:
    if settings.json_input is not None:
        raw_json = settings.json_input
    elif settings.input is not None and str(settings.input) == "-":
        raw_json = sys.stdin.read()
    elif settings.input is not None:
        raw_json = settings.input.read_text(encoding="utf-8")
    else:
        raise ValueError("provide exactly one of --input or --json")

    return TypeAdapter(PayloadCreate).validate_json(raw_json)


def run_requests(settings: CliSettings, payload: PayloadCreate) -> list[dict[str, object]]:
    base_url = f"{str(settings.host).rstrip('/')}/"
    results: list[dict[str, object]] = []

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        for _ in range(settings.repeat):
            created_response = client.post(
                "payloads",
                json=payload.model_dump(mode="json"),
            )
            created_response.raise_for_status()
            created_id = TypeAdapter(int).validate_python(created_response.json())

            payload_response = client.get(f"payloads/{created_id}")
            payload_response.raise_for_status()
            stored_payload = PayloadOut.model_validate(payload_response.json())
            results.append(
                {
                    "created_id": created_id,
                    "payload": stored_payload.model_dump(mode="json"),
                }
            )

    return results


def write_output(settings: CliSettings, results: list[dict[str, object]]) -> None:
    serialized = json.dumps(results, ensure_ascii=False, indent=2) + "\n"
    if settings.output is None or str(settings.output) == "-":
        sys.stdout.write(serialized)
    else:
        settings.output.write_text(serialized, encoding="utf-8")


def main() -> int:
    try:
        settings = CliSettings()
        if settings.help:
            print(_help_text())
            return 0

        payload = load_payload(settings)
        results = run_requests(settings, payload)
        write_output(settings, results)
    except (httpx.HTTPError, OSError, UnicodeError, ValidationError, ValueError) as error:
        print(f"cache-cli: {error}", file=sys.stderr)
        return 1

    return 0


def _help_text() -> str:
    return """usage: cache-cli [-h URL] [-r N] [-i FILE | -j JSON] [-o FILE] [--help]

options:
  -h, --host URL    Base URL of the service (default: http://127.0.0.1:8000)
  -r, --repeat N    Number of iterations (default: 1)
  -i, --input FILE  Read JSON from FILE, or "-" for stdin
  -j, --json JSON   Provide the JSON input directly
  -o, --output FILE Write output to FILE, or "-" for stdout
      --help        Show this help message and exit
"""


if __name__ == "__main__":
    sys.exit(main())
