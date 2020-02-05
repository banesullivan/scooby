from bs4 import BeautifulSoup
import mock
import numpy
import pytest
import re
import sys

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
    assert version == scooby.report.VERSION_NOT_FOUND
    assert name == "no_version"
    name, version = scooby.get_version("does_not_exist")
    assert version == scooby.report.MODULE_NOT_FOUND
    assert name == "does_not_exist"


def test_plain_vs_html():
    report = scooby.Report()
    text_html = BeautifulSoup(report._repr_html_()).get_text()
    text_plain = report.__repr__()

    text_plain = " ".join(re.findall("[a-zA-Z1-9]+", text_plain))
    text_html = " ".join(re.findall("[a-zA-Z1-9]+", text_html))

    # Plain text currently starts with `Date :`;
    # we should remove that, or add it to the html version too.
    assert text_html == text_plain[5:]



def test_extra_meta():
    report = scooby.Report(extra_meta=("key", "value"))
    assert "value : key" in report.__repr__()
    report = scooby.Report(extra_meta=(("key", "value"),))
    assert "value : key" in report.__repr__()
    report = scooby.Report(extra_meta=(("key", "value"), ("another", "one")))
    assert "value : key" in report.__repr__()
    assert "one : another" in report.__repr__()
    with pytest.raises(TypeError):
        report = scooby.Report(extra_meta=(("key", "value"), "foo"))
    with pytest.raises(TypeError):
        report = scooby.Report(extra_meta="foo")
    with pytest.raises(TypeError):
        report = scooby.Report(extra_meta="fo")


@pytest.mark.skipif(sys.version_info.major < 3, reason="Tracking not supported on Python 2.")
def test_tracking():
    scooby.track_imports()
    from scipy.constants import mu_0 # a float value
    report = scooby.TrackedReport()
    scooby.untrack_imports()
    import no_version
    assert "numpy" in report.packages
    assert "scipy" in report.packages
    assert "no_version" not in report.packages
    assert "pytest" not in report.packages
    assert "mu_0" not in report.packages


def test_version_compare():
    assert scooby.meets_version('2', '1')
    assert not scooby.meets_version('1', '2')

    assert scooby.meets_version('1', '1')
    assert scooby.meets_version('0.1', '0.1')
    assert scooby.meets_version('0.1.0', '0.1.0')

    assert scooby.meets_version('1.0', '0.9')
    assert not scooby.meets_version('0.9', '1.0')

    assert scooby.meets_version('0.2.5', '0.1.8')
    assert not scooby.meets_version('0.1.8', '0.2.5')

    assert not scooby.meets_version('0.25.1', '0.25.2')
    assert scooby.meets_version('0.26.0', '0.25.2')
    assert scooby.meets_version('0.25.2', '0.25.2')

    assert not scooby.meets_version('0.25.2', '0.26')

    with pytest.raises(ValueError):
        scooby.meets_version('0.25.2.0', '0.26')
