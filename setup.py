from setuptools import setup

from pywechatpay.constants import VERSION

with open("README.md", "r", encoding="utf8") as f:
    long_description = f.read()

setup(
    name="pywechatpay",
    version=VERSION,
    author="dust8",
    description="Python SDK for WechatPay V3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    keywords="python sdk wechatpay v3",
    url="https://github.com/dust8/pywechatpay",
    packages=["pywechatpay"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=["cryptography", "requests"],
)
