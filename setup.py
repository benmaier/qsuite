from setuptools import setup

setup(name='qsuite',
      version='0.4.12',
      description='',
      url='https://github.com/benmaier/qsuite',
      author='Benjamin F. Maier',
      author_email='benjaminfrankmaier@gmail.com',
      license='MIT',
      packages=['qsuite'],
      include_package_data = True,
      install_requires=[
          'numpy',
          'paramiko',
          'tabulate',
          'pathos',
      ],
      dependency_links=[
          ],
      entry_points = {
            'console_scripts': [
                    'qsuite = qsuite.qsuite_binary:main',
                ],
          },
      zip_safe=False)
