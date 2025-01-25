from setuptools import setup, Extension

ext_modules = [
    Extension(
        "clovers_utils.linecard.linecard_parsing",
        sources=["linecard_parsing/linecard_parsing.cpp"],
        extra_compile_args=["/std:c++latest", "/O2", "/Oi", "/Ob2"],
    ),
]

setup(
    name="clovers_utils",
    version="0.1",
    ext_modules=ext_modules,
)
