from setuptools import setup, Extension

# 定义模块
module = Extension(
    "linecard_parsing",
    sources=["linecard_parsing.cpp"],
    extra_compile_args=[
        "/std:c++latest",
        "/Ox",
        "/Oi",
        "/Ob2",
    ],
)

# 设置包信息
setup(
    name="linecard_parsing",
    version="1.0",
    description="",
    ext_modules=[module],
)
