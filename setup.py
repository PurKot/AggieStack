from setuptools import setup, find_packages

setup(
    name='aggiestack',
    version='0.1',
    packages=['aggiestack', 'aggiestack.commands'],
    #packages=find_packages(),
    # py_modules=['aggiestack'],
    include_package_data=True,
    install_requires=[
        'Click',
        'pymongo',
        'mongoengine',
        'datetime'
    ],
    entry_points='''
        [console_scripts]
        aggiestack = aggiestack.cli:cli
        '''
)
