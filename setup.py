import setuptools

gituser = "ptrktn"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

if __name__ == "__main__":
    setuptools.setup(py_modules=["uwebdavclient"],
          name="uwebdavclient",
          version="0.0.1",
          author=f"{gituser}@github",
          author_email="{gituser}@users.noreply.github.com",
          url=f"https://github.com/{gituser}/{name}",
          description="Minimal WebDAV client in pure Python",
          long_description=long_description,
          project_urls={
              "Bug Tracker": f"https://github.com/{gituser}/{name}/issues",
          },
          classifiers=[
              "Programming Language :: Python :: 3",
              "OSI Approved :: GNU General Public License v3",
              "Operating System :: OS Independent",
          ],
          package_dir={"": "src"},
          packages=setuptools.find_packages(where="src"),
          python_requires=">=3.6",
    )
