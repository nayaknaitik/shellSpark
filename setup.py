from setuptools import setup, find_packages

setup(
    name="shellspark",
    version="1.0.0",
    description="Intelligent bash extension that translates natural English commands into terminal commands",
    author="ShellSpark",
    author_email="naitiknayak009@gmail.com",
    url="https://shellspark.dev",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests>=2.28.0", "rich>=13.0.0"],
    entry_points={
        "console_scripts": [
            "shellspark=shellspark.__main__:main",
            "sx=shellspark.__main__:main",
        ],
    },
    python_requires=">=3.8",
)
