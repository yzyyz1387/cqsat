import io
import sys

import setuptools

with open("README.md", "r", encoding="utf-8", errors="ignore") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nonebot-plugin-cqsat",
    version="0.1.3",
    author="yzyyz1387",
    author_email="youzyyz1384@gmail.com",
    keywords=("ham", "nonebot2", "nonebot", "radio", "nonebot_plugin"),
    description="""nonebot2 业余无线电卫星""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yzyyz1387/cqsat",
    packages=setuptools.find_packages(include=["cqsat", "cqsat.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,

    platforms="any",
    install_requires=["httpx", "pyephem", "python_dateutil", "PyYAML",
                      'nonebot-adapter-onebot>=2.0.0-beta.1', 'nonebot2>=2.0.0-beta.4',
                      'nonebot-plugin-apscheduler'
                      ]
)
