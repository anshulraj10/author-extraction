import os

from grobid_client.grobid_client import GrobidClient
from backend.app.config import GROBID_CONFIG_PATH


def get_data_from_gorbid(pdf_path):
    try:
        client = GrobidClient(config_path=GROBID_CONFIG_PATH)

        client.process(
            service="processReferences",
            input_path=pdf_path,
            # output_path=".",
            json_output=True,
            n=1,
        )

        json_path = ""

        for (_, _, filenames) in os.walk(pdf_path):
            json_path = [filename for filename in filenames if filename.endswith(".json")][0]

        return json_path
    except Exception as err:
        raise RuntimeError("grobid extraction failed") from err
