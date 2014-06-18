import os
from setuptools import setup, find_packages

# long_description = (
#     open('README.rst').read()
#     + '\n' +
#     open('CHANGES.txt').read())

tests_require = [
    'pytest >= 2.0',
    'pytest-cov'
    ]

setup(name='bowerstatic',
      version='0.1.dev0',
      description="A Bower-centric static file server",
      author="Martijn Faassen",
      author_email="faassen@startifact.com",
      license="BSD",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        ],
      tests_require=tests_require,
      extras_require = dict(
        test=tests_require,
        )
      )
