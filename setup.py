from setuptools import setup
from io import open

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='json-five',
    version='0.1.0',
    packages=['json5'],
    url='https://github.com/spyoungtech/json-five',
    license='Apache',
    author='Spencer Phillip Young',
    author_email='spencer.young@spyoung.com',
    description='A JSON5 parser that, among other features, supports round-trip preservation of comments',
    long_description=long_description,
    install_requires=['sly'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)