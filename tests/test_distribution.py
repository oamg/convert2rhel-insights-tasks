import pytest
from convert2rhel_insights_tasks.main import ProcessError, check_dist_version


def test_check_dist_version_missing_information():
    assert not check_dist_version(None, None)


@pytest.mark.parametrize(("dist", "version"), (("centos", "8.10"), ("oracle", "7.9")))
def test_check_dist_version_process_error(dist, version):
    with pytest.raises(ProcessError) as execinfo:
        check_dist_version(dist, version)

    # pylint: disable=protected-access
    assert (
        "Conversion is only supported on CentOS 7.9 distributions"
        in execinfo._excinfo[1].message
    )
    assert (
        'Exiting because distribution="%s" and version="%s"' % (dist.title(), version)
        in execinfo._excinfo[1].report
    )
