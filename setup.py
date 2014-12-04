from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

tests_require = [
]

version = '0.0.0'
try:
    import ec2_costs
    version = ec2_costs.__version__
except ImportError:
    pass


setup(
    name='ec2-costs',
    version=version,
    packages=find_packages(),
    install_requires=[
        'boto',
        'click',
        'prettytable',
    ],
    extras_require=dict(
        tests=tests_require,
    ),
    tests_require=tests_require,
    test_suite='nose.collector',
    entry_points="""\
    [console_scripts]
    ec2-costs = ec2_costs.__main__:main
    """,
)
