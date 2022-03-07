import setuptools

githubuser = "ptrktn"
name = "uwebdavclient"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

if __name__ == "__main__":
    setuptools.setup(
        py_modules=[name],
        name=name,
        version="0.0.2",
        author=f"{githubuser}@github",
        author_email="{githubuser}@users.noreply.github.com",
        url=f"https://github.com/{githubuser}/{name}",
        description="Minimal WebDAV client in pure Python",
        long_description=long_description,
        long_description_content_type="text/markdown",
        install_requires=["requests", ],
        scripts=[f"src/bin/{name}", ],
        project_urls={
            "Bug Tracker": f"https://github.com/{githubuser}/{name}/issues",
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent",
        ],
        package_dir={"": "src"},
        packages=setuptools.find_packages(where="src"),
        python_requires=">=3.6",
    )
