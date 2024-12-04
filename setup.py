from setuptools import setup, find_packages

setup(
    name='epic_benchmarks',
    version='1.0',
    packages=find_packages(where='.', include=['epic_benchmarks', 'epic_benchmarks.*']),
    package_dir={'': '.'},
    install_requires=[
        'pyyaml',
        'lxml',
        'jupyter',
        'numpy',
        'pandas',
        'scipy',
        'seaborn',
        'uproot',
        'uncertainties',
        'parsl',
        'lmfit',
        'fsspec-xrootd',
        'matplotlib'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'run-benchmark = eicbenchmark.main:main'
        ]
    }
)