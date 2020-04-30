from distutils.core import setup

setup(
    name='sempler',
    version='0.1.1',
    author='Juan L Gamella',
    author_email='juangamella@gmail.com',
    packages=['sempler', 'sempler.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/sempler/',
    license='LICENSE.txt',
    description='Sample from general structural causal models (SCMs)',
    long_description=open('README.txt').read(),
    install_requires=['numpy==1.18.3', 'networkx==2.2', 'matplotlib==3.2.1']
)
