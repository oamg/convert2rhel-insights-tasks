from mock import patch
import pytest
from convert2rhel_insights_tasks.main import update_insights_inventory, ProcessError


def test_update_insights_inventory_successfully():
    with patch(
        "convert2rhel_insights_tasks.main.run_subprocess", return_value=(b"", 0)
    ) as mock_popen:
        update_insights_inventory()

    mock_popen.assert_called_once_with(cmd=["/usr/bin/insights-client"])


def test_update_insights_inventory_non_success():
    with patch(
        "convert2rhel_insights_tasks.main.run_subprocess", return_value=(b"output", 1)
    ) as mock_popen:
        with pytest.raises(
            ProcessError, match="insights-client execution exited with code '1'"
        ):
            update_insights_inventory()

    mock_popen.assert_called_once_with(cmd=["/usr/bin/insights-client"])
