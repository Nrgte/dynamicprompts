import pytest
from unittest import mock

from prompts.generators import FeelingLuckyGenerator
class TestFeelingLucky:
    def test_generate(self):
        results = ["ABC", "XYZ"]
        with mock.patch("prompts.generators.feelinglucky.requests") as mock_response:
            with mock.patch("prompts.generators.feelinglucky.random") as mock_random:
                m = mock.Mock()
                m.json.return_value = {"images": results}
                mock_response.get.return_value = m
                mock_random.choices.return_value = ["ABC"]

                generator = FeelingLuckyGenerator("This is a test")
                generator.generate(1)
                mock_random.choices.assert_called_with(results, k=1)