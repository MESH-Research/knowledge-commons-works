from setuptools import setup, find_packages

setup(
    name='invenio-subjects-fast',
    version='0.1.0',
    py_modules=find_packages(),
    install_requires=[
        'Click',
        'tqdm',
        'halo'
    ],
    entry_points={
        'console_scripts': [
            'invenio-subjects-fast = invenio_subjects_fast.main:cli',
        ],
    },
)