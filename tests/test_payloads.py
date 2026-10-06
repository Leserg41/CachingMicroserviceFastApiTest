import unittest
from types import SimpleNamespace

from app.schemas import PayloadOut


class PayloadResponseSchemaTests(unittest.TestCase):
    def test_maps_model_text_attribute_to_output(self) -> None:
        response = PayloadOut.model_validate(SimpleNamespace(text="a,b"))

        self.assertEqual(response.output, "a,b")
        self.assertEqual(response.model_dump(), {"output": "a,b"})

    def test_accepts_serialized_output_field(self) -> None:
        response = PayloadOut.model_validate({"output": "a,b"})

        self.assertEqual(response.output, "a,b")


if __name__ == "__main__":
    unittest.main()