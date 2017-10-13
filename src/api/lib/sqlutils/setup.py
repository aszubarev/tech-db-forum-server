from setuptools import setup
from setuptools import find_packages


setup(
    name='sqlutils',
    version='0.0.8',
    author='Russian Telecommunication Equipment Company',
    author_email='info@pkcc.ru',
    description='SQL tools',
    license='1. Restricted Uses /n/t1.1. No Distribution, etc. [Licensee] [You] may not distribute, license, loan, '
            'or sell the Software or other content that is contained or displayed in it./n/t1.2. No Modification. '
            '[Licensee] [You] may not modify, alter, or create any derivative works of the Software./n/t'
            '1.3. No Reverse Engineering. [Licensee] [You] may not reverse engineer, decompile, decode, decrypt, '
            'disassemble, or derive any source code from the Software./n/t1.4. Proprietary Notices. '
            '[Licensee] [You] may not remove, alter, or obscure any copyright, trademark, or other proprietary rights '
            'notice on or in the Software.',
    keywords='SQL database tools',
    packages=find_packages(),
    test_suite='tests',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities"
    ],
)
