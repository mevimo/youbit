import os
from distutils.command.build_ext import build_ext

from Cython.Build import cythonize


def build(setup_kwargs):
    extensions = ["youbit/ecc/creedsolo.pyx"]
    os.environ["CFLAGS"] = "-O3"
    setup_kwargs.update(
        {
            "ext_modules": cythonize(
                extensions,
                language_level=3,
                compiler_directives={"linetrace": True},
            ),
            "cmdclass": {"build_ext": build_ext},
        }
    )
