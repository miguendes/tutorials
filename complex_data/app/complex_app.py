from typing import Dict, Tuple

from PIL import Image
from pandas import np


def config_data(verbose_desc: str, simple_desc: str) -> dict:
    return {
        "agg_results": {
            "t1": [True, False, True, False],
            "nums": [1.3, 3.4, 23.456, 21.3456],
            "count": 120,
        },
        "sample": {"desc": {"verbose": verbose_desc, "simple": simple_desc}},
    }


def read_from_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def convert_image_to_gray(
    input_path: str, output_path: str, size: Tuple[int, int] = (200, 200)
):
    image = Image.open(input_path)
    gray_image = image.convert("L")
    gray_image.thumbnail(size, Image.ANTIALIAS)
    gray_image.save(output_path, "PNG")


def element_wise_mult(a: np.array, b: np.array) -> Dict[str, np.array]:
    res = a * b
    return {"res": res}


def dict_to_html(data: dict) -> str:
    html = "<table><tr><th>" + "</th><th>".join(data.keys()) + "</th></tr>"

    for row in zip(*data.values()):
        html += "<tr><td>" + "</td><td>".join(row) + "</td></tr>"

    html += "</table>"

    return html
