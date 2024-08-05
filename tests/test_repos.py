import pytest
from convert2rhel_insights_tasks import main


def test_repos_are_accessible(monkeypatch, caplog):
    monkeypatch.setattr(main, "run_subprocess", lambda cmd: ("", 0))
    main.check_repos_are_valid()

    assert "System repositories are acessible." in caplog.records[-1].message


@pytest.mark.parametrize(
    ("output_error", "expected_msg"),
    (
        (
            """
Loaded plugins: fastestmirror, product-id, search-disabled-repos, subscription-manager
Loading mirror speeds from cached hostfile
http://vasadsadault.centos.org/7.9.2009/os/x86_64/repodata/repomd.xml: [Errno 14] curl#6 - "Could not resolve host: vasadsadault.centos.org; Unknown error"
Trying other mirror.


 One of the configured repositories failed (CentOS-7 - Base),
 and yum doesn't have enough cached data to continue. At this point the only
 safe thing yum can do is fail. There are a few ways to work "fix" this:

     1. Contact the upstream for the repository and get them to fix the problem.

     2. Reconfigure the baseurl/etc. for the repository, to point to a working
        upstream. This is most often useful if you are using a newer
        distribution release than is supported by the repository (and the
        packages for the previous distribution release still work).

     3. Run the command with the repository temporarily disabled
            yum --disablerepo=base ...

     4. Disable the repository permanently, so yum won't use it by default. Yum
        will then just ignore the repository until you permanently enable it
        again or use --enablerepo for temporary usage:

            yum-config-manager --disable base
        or
            subscription-manager repos --disable=base

     5. Configure the failing repository to be skipped, if it is unavailable.
        Note that yum will try to contact the repo. when it runs most commands,
        so will have to try and fail each time (and thus. yum will be be much
        slower). If it is a very temporary problem though, this is often a nice
        compromise:

            yum-config-manager --save --setopt=base.skip_if_unavailable=true

failure: repodata/repomd.xml from base: [Errno 256] No more mirrors to try.
http://vasadsadault.centos.org/7.9.2009/os/x86_64/repodata/repomd.xml: [Errno 14] curl#6 - "Could not resolve host: vasadsadault.centos.org; Unknown error"
""",
            'failure: repodata/repomd.xml from base: [Errno 256] No more mirrors to try.\nhttp://vasadsadault.centos.org/7.9.2009/os/x86_64/repodata/repomd.xml: [Errno 14] curl#6 - "Could not resolve host: vasadsadault.centos.org; Unknown error"',
        ),
        (
            """
Loaded plugins: fastestmirror, ovl
Determining fastest mirrors
Could not retrieve mirrorlist http://mirrorlist.centos.org/?release=7&arch=x86_64&repo=os&infra=container error was
14: curl#6 - "Could not resolve host: mirrorlist.centos.org; Unknown error"


 One of the configured repositories failed (Unknown),
 and yum doesn't have enough cached data to continue. At this point the only
 safe thing yum can do is fail. There are a few ways to work "fix" this:

     1. Contact the upstream for the repository and get them to fix the problem.

     2. Reconfigure the baseurl/etc. for the repository, to point to a working
        upstream. This is most often useful if you are using a newer
        distribution release than is supported by the repository (and the
        packages for the previous distribution release still work).

     3. Run the command with the repository temporarily disabled
            yum --disablerepo=<repoid> ...

     4. Disable the repository permanently, so yum won't use it by default. Yum
        will then just ignore the repository until you permanently enable it
        again or use --enablerepo for temporary usage:

            yum-config-manager --disable <repoid>
        or
            subscription-manager repos --disable=<repoid>

     5. Configure the failing repository to be skipped, if it is unavailable.
        Note that yum will try to contact the repo. when it runs most commands,
        so will have to try and fail each time (and thus. yum will be be much
        slower). If it is a very temporary problem though, this is often a nice
        compromise:

            yum-config-manager --save --setopt=<repoid>.skip_if_unavailable=true

Cannot find a valid baseurl for repo: base/7/x86_64
""",
            "Cannot find a valid baseurl for repo: base/7/x86_64",
        ),
        (
            """
Loaded plugins: fastestmirror, ovl
Determining fastest mirrors
Could not retrieve mirrorlist http://mirrorlist.centos.org/?release=7&arch=x86_64&repo=os&infra=container error was
14: curl#6 - "Could not resolve host: mirrorlist.centos.org; Unknown error"


 One of the configured repositories failed (Unknown),
 and yum doesn't have enough cached data to continue. At this point the only
 safe thing yum can do is fail. There are a few ways to work "fix" this:

     1. Contact the upstream for the repository and get them to fix the problem.

     2. Reconfigure the baseurl/etc. for the repository, to point to a working
        upstream. This is most often useful if you are using a newer
        distribution release than is supported by the repository (and the
        packages for the previous distribution release still work).

     3. Run the command with the repository temporarily disabled
            yum --disablerepo=<repoid> ...

     4. Disable the repository permanently, so yum won't use it by default. Yum
        will then just ignore the repository until you permanently enable it
        again or use --enablerepo for temporary usage:

            yum-config-manager --disable <repoid>
        or
            subscription-manager repos --disable=<repoid>

     5. Configure the failing repository to be skipped, if it is unavailable.
        Note that yum will try to contact the repo. when it runs most commands,
        so will have to try and fail each time (and thus. yum will be be much
        slower). If it is a very temporary problem though, this is often a nice
        compromise:

            yum-config-manager --save --setopt=<repoid>.skip_if_unavailable=true

Cannot find a valid baseurl for repo: base/7/x86_64
Cannot find a valid baseurl for repo: base/7/x86_64
""",
            "Cannot find a valid baseurl for repo: base/7/x86_64\nCannot find a valid baseurl for repo: base/7/x86_64",
        ),
        (
            "yum-config-manager --save --setopt=base.skip_if_unavailable=true\n\nerror repo",
            "error repo",
        ),
    ),
)
def test_repos_are_not_accessible(monkeypatch, output_error, expected_msg):
    monkeypatch.setattr(main, "run_subprocess", lambda cmd: (output_error, 1))

    with pytest.raises(main.ProcessError) as execinfo:
        main.check_repos_are_valid()

    # pylint: disable=protected-access
    assert (
        "Failed to verify accessibility of system repositories."
        in execinfo._excinfo[1].message
    )
    assert (
        "The following repositories are not accessible: %s.\n\nFor more information, please visit https://access.redhat.com/solutions/7077708."
        % expected_msg
        in execinfo._excinfo[1].report
    )


def test_clean_yum_cache(monkeypatch, caplog):
    monkeypatch.setattr(main, "run_subprocess", lambda cmd: ("", 0))

    main.clean_yum_cache()

    assert (
        "Cached repositories metadata cleaned successfully."
        in caplog.records[-1].message
    )


def test_failed_to_clean_yum_cache(monkeypatch, caplog):
    monkeypatch.setattr(
        main, "run_subprocess", lambda cmd: ("error cleaning metadata", 1)
    )

    main.clean_yum_cache()

    assert (
        "Failed to clean yum metadata:\nerror cleaning metadata"
        in caplog.records[-1].message
    )
