from __future__ import annotations

import os
import pathlib

import setuptools

with pathlib.Path('README.md').open('r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='scooby',
    author='Dieter Werthmüller, Bane Sullivan, Alex Kaszynski, and contributors',
    author_email='info@pyvista.org',
    description='A Great Dane turned Python environment detective',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/banesullivan/scooby',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'scooby=scooby.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
    ],
    python_requires='>=3.8',
    extras_require={
        'cpu': ['psutil', 'mkl'],
    },
    use_scm_version={
        'root': '.',
        'relative_to': __file__,
        'write_to': os.path.join('scooby', 'version.py'),  # noqa: PTH118
    },
    setup_requires=['setuptools_scm'],
    package_data={'scooby': ['py.typed']},
)
