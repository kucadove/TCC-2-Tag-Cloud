from setuptools import setup

setup(
    name='tagcloud',
    packages=['tagcloud'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)