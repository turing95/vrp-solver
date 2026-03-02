from setuptools import setup
from Cython.Build import cythonize

if __name__ == "__main__":
    setup(ext_modules=cythonize(['routing/algorithm/*.pyx', 'routing/entity/constant.pyx'],
                                annotate=True,
                                compiler_directives={
                                    'language_level': '3',
                                    'initializedcheck': False,
                                    'boundscheck': False,
                                })
          )
