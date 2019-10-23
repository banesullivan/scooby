import mock
import numpy
import pytest

import scooby

def test_report():
    report = scooby.Report()
    text = str(report)
    assert len(text) > 0
    assert len(report.packages) > 0
    for pkg, vers in report.packages.items():
        assert isinstance(pkg, str)
        assert isinstance(vers, str)
    report = scooby.Report(core='numpy')
    assert ('numpy' in report.packages)
    html = report._repr_html_()
    assert len(html) > 0
    # Same as what is printed in Travis build log
    report = scooby.Report(additional=['mock', 'foo'])
    report = scooby.Report(additional=['foo',])
    report = scooby.Report(additional=[mock,])
    report = scooby.Report(additional=mock)
    report = scooby.Report(additional=['collections', 'foo', 'aaa'], sort=True)


def test_inheritence_example():
    class Report(scooby.Report):
        def __init__(self, additional=None, ncol=3, text_width=80, sort=False):
            """Initiate a scooby.Report instance."""

            # Mandatory packages.
            core = ['psutil', 'mkl', 'numpy', 'scooby']

            # Optional packages.
            optional = ['your_optional_packages', 'e.g.', 'matplotlib',
                        'foo', ]

            scooby.Report.__init__(self, additional=additional, core=core,
                                   optional=optional, ncol=ncol,
                                   text_width=text_width, sort=sort)

    report = Report(['mock'])
    assert 'psutil' in report.packages
    assert 'mkl' in report.packages
    assert 'numpy' in report.packages


def test_ipy():
    result = scooby.in_ipykernel()


def test_get_version():
    name, version = scooby.get_version(numpy)
    assert version == numpy.__version__
    assert name == "numpy"
    name, version = scooby.get_version("no_version")
    assert version == "Version unknown"
    assert name == "no_version"
    name, version = scooby.get_version("does_not_exist")
    assert version == "Could not import"
    assert name == "does_not_exist"
