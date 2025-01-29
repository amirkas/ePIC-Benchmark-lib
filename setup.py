from setuptools import setup, find_packages

setup(
    name='epic_benchmarks',
    version='1.0',
    packages=find_packages(where='.', include=['epic_benchmarks', 'epic_benchmarks.*']),
    package_dir={'': '.'},
    install_requires=[
        'pyyaml',
        'pydantic',
        'mypy',
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
        'matplotlib'
    ],
    include_package_data=True,
)
