from setuptools import setup, find_packages

setup(
    name="aida-scraper",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # 依赖项会从requirements.txt读取
    ],
    author="AIDA Team",
    author_email="example@example.com",
    description="艺术数据爬虫项目",
    keywords="art, scraper, gallery",
    python_requires=">=3.8",
) 