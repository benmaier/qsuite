from setuptools import setup

setup(name='qsuite',
      version='0.2',
      description='',
      url='https://bitbucket.org/bfmaier/rocs-queueing-suite',
      author='Benjamin F. Maier',
      author_email='benjaminfrankmaier@gmail.com',
      license='MIT',
      packages=['qsuite'],
      install_requires=[
          'numpy',
      ],
      dependency_links=[
          ],
      entry_points = {
            'console_scripts': [
                    'qsuite = qsuite.qsuite_binary:main',
                ],
          },
      zip_safe=False)