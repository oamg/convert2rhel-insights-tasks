import pytest
from mock import patch

from scripts.conversion_script import _get_last_yum_transaction_id


@pytest.mark.parametrize("mock_return, expected_result", [
    (("8 | install -y convert2rhel | 2023-11-23 16:53 | Install | 6", 0), "8"),
    (("    9 | install -y convert2rhel | 2023-11-23 16:53 | Update | 6", 0), "9"),
    (("| install -y convert2rhel | 2023-11-23 16:53 | Erase | 6", 0), None),
    (("12 | install -y package4 | 2023-11-24 10:30 | Install | 2\n"
      "8 | install -y convert2rhel | 2023-11-23 16:53 | Update | 6", 0), "8"),
    (("", 1), None),
])
def test_get_last_yum_transaction_id(mock_return, expected_result):
    pkg_name = "convert2rhel"

    with patch(
        "scripts.conversion_script.run_subprocess",
        return_value=mock_return
    ) as mock_run_subprocess:
        result = _get_last_yum_transaction_id(pkg_name)

    mock_run_subprocess.assert_called_once()

    assert result == expected_result
