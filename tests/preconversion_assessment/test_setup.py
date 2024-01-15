from mock import Mock

from scripts.preconversion_assessment_script import setup_convert2rhel


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
