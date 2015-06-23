from setuptools import setup, find_packages

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CHANGES.txt').read())

tests_require = [
    'pytest >= 2.0',
    'pytest-cov',
    'WebTest >= 2.0.14',
    'mock',
    ]

setup(
    name='bowerstatic',
    version='0.10.dev0',
    description="A Bower-centric static file server for WSGI",
    long_description=long_description,
    author="Martijn Faassen",
    author_email="faassen@startifact.com",
    license="BSD",
    url='http://bowerstatic.readthedocs.org',
    keywords='wsgi bower',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'WebOb',
    ],
    tests_require=tests_require,
    extras_require=dict(
        test=tests_require,
    )
)
