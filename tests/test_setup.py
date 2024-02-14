import pytest
from mock import Mock
from urllib2 import URLError


from scripts.c2r_script import setup_convert2rhel, ProcessError


class MockRequiredFile(object):
    def __init__(self, path, host):
        self.path = path
        self.host = host

    def create_from_host_url_data(self):
        return

    def backup(self):
        return


def test_setup_calls_backup_and_create_for_every_file():
    # pylint: disable=too-many-arguments
    mocked_required_file = Mock(spec=MockRequiredFile)
    test_file = mocked_required_file("/mock/path/file.txt", "foo.bar")
    required_files = [test_file]

    setup_convert2rhel(required_files)

    test_file.backup.assert_called_once()
    test_file.create_from_host_url_data.assert_called_once()


def test_setup_urlerror():
    # pylint: disable=too-many-arguments
    mocked_required_file = Mock(spec=MockRequiredFile)
    test_file = mocked_required_file("/mock/path/file.txt", "foo.bar")
    test_file.create_from_host_url_data.side_effect = URLError("foo")
    required_files = [test_file]

    with pytest.raises(ProcessError) as error:
        setup_convert2rhel(required_files)
        assert "Download of required file from foo.bar failed with error: foo" in str(
            error
        )

    test_file.backup.assert_called_once()
    test_file.create_from_host_url_data.assert_called_once()
