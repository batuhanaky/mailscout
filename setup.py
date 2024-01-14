from setuptools import find_packages, setup

setup(
    name='mailscout',
    packages=find_packages(include = ["mailscout"]),
    version='0.1.0',
    description='MailScout is a Python library designed for finding business email addresses and simple email validation. It offers a range of tools for email validation, SMTP checks, email normalization, and generating potential business email addresses based on common naming conventions/employee name combinations.',
    author='Batuhan Akyazı',
    install_requires=["dnspython", "unidecode"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)