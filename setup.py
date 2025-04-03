from setuptools import setup, find_packages

setup(
    name='ePIC_benchmarks',
    version='2.0-alpha',
    packages=find_packages(where='.', include=['ePIC_benchmarks', 'ePIC_benchmarks.*']),
    package_dir={'': '.'},
    install_requires=[
        'pyyaml',
        'pydantic',
        'pydantic-xml',
        'pydantic-settings',
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
