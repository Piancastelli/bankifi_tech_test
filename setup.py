from setuptools import setup, find_packages

install_requires = ["nose == 1.3.7",
					"selenium == 3.141.0"]

setup(
   name="Bankifi Selenium Tests",
   version="1.0.0",
   description="Set of automated tests for https://saucedemo.com",
   author="Rowan Piancastelli",
   author_email="rowan_piancastelli@hotmail.com",
   packages=find_packages(),
   install_requires=install_requires,
)