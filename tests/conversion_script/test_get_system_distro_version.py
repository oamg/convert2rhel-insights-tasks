from mock import patch, mock_open
from scripts.conversion_script import get_system_distro_version


@patch("__builtin__.open", mock_open(read_data="CentOS Linux release 7.9.0 (Core)\n"))
def test_get_system_distro_version_with_existing_file():
    distribution_id, version_id = get_system_distro_version()

    assert distribution_id == "centos"
    assert version_id == "7.9"


@patch("__builtin__.open", mock_open(read_data="CentOS Linux release 1 (Core)\n"))
def test_get_system_distro_version_no_matching_version():
    distribution_id, version_id = get_system_distro_version()

    assert distribution_id == "centos"
    assert version_id is None


@patch("__builtin__.open")
def test_get_system_distro_version_with_missing_file(mock_open_file):
    mock_open_file.side_effect = IOError("Couldn't read /etc/os-release")

    distribution_id, version_id = get_system_distro_version()

    assert distribution_id is None
    assert version_id is None
