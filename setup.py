from setuptools import setup

setup(
    name='hikeblog',
    packages=['hikeblog'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_wtf',
        'flask_sqlalchemy',
        'flask-admin'
    ],
)
