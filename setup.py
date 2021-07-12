from setuptools import setup

setup(name='qsuite',
      version='0.4.14',
      description='A CLI to submit and retrieve large-scale jobs/results to and from HPC clusters.',
      url='https://github.com/benmaier/qsuite',
      author='Benjamin F. Maier',
      author_email='benjaminfrankmaier@gmail.com',
      license='MIT',
      packages=['qsuite'],
      include_package_data = True,
      install_requires=[
        'numpy>=1.17',
        'paramiko>=2.7.2',
        'pathos>=0.2.7',
        'tabulate>=0.8.7',
      ],
      dependency_links=[
          ],
      entry_points = {
            'console_scripts': [
                    'qsuite = qsuite.qsuite_binary:main',
                ],
          },
      zip_safe=False)
