from setuptools import setup

setup(name='dslogparser',
      version='1.0.0',
      description='FIRST FRC Driver Station logs parser',
      url='http://github.com/ligerbots/dslogparser',
      author='Paul Rensing',
      author_email='prensing@ligerbots.org',
      license='MIT',
      download_url='https://github.com/ligerbots/dslogparser/archive/v1.0.0.tar.gz',
      packages=['dslogparser'],
      scripts=['dslog2csv.py'],
      install_requires=[
          'bitstring',
      ],
      zip_safe=False
)
