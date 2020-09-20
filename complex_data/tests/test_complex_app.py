from pathlib import Path

import numpy as np

from app.complex_app import (
    config_data,
    read_from_file,
    convert_image_to_gray,
    element_wise_mult,
    dict_to_html,
)


def test_config_data():
    actual = config_data(verbose_desc="first experiment", simple_desc="first")
    assert actual["agg_results"]["t1"] == [True, False, True, False]
    assert actual["agg_results"]["nums"] == [1.3, 3.4, 23.456, 21.3456]
    assert actual["agg_results"]["count"] == 120

    assert actual["sample"]["desc"]["verbose"] == "first experiment"
    assert actual["sample"]["desc"]["simple"] == "first"


def test_config_data_with_pytest_regressions(data_regression):
    actual = config_data(verbose_desc="first experiment", simple_desc="first")
    data_regression.check(actual)


def test_read_from_file(file_regression, datadir):
    contents = read_from_file("tests/resources/data.bin")
    file_regression.check(contents, binary=True, extension=".bin")


def test_convert_image_to_gray(image_regression):
    output_file = Path("tests/resources/python_logo_gray.png")
    convert_image_to_gray(
        "tests/resources/python_logo.png", str(output_file), size=(100, 100)
    )
    image_regression.check(output_file.read_bytes(), diff_threshold=1.0)


def test_elemwise_multi_calculation(num_regression):
    np.random.seed(0)
    a = np.random.randn(6)
    b = np.random.randn(6)
    result = element_wise_mult(a, b)
    num_regression.check(result)


def test_dict_to_html(file_regression):
    data = {
        "Heights": ["30", "12", "12"],
        "IDs": ["XXDDUBAB", "LOPSKSKSS", "KIOTGGAGA"],
        "Download Count": ["123", "34", "2"],
    }

    html = dict_to_html(data)
    file_regression.check(html, extension=".html")
