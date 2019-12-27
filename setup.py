from setuptools import setup

setup(name='dslogparser',
      version='1.0.0',
      description='FRC Driver Station logs parser',
      url='http://github.com/ligerbots/dslogparser',
      author='Paul Rensing',
      author_email='prensing@ligerbots.org',
      license='',
      packages=['dslogparser'],
      install_requires=[
          'bitstring',
      ],
      zip_safe=False)
