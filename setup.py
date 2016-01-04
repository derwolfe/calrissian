from setuptools import setup

setup(
    name=u"calrissian",
    description=u"static file server for a blog",
    version=u"0.1",
    maintainer=u"Chris Wolfe",
    license=u"MIT",
    zip_safe=True,
    packages=["calrissian"],
    include_package_data=True,
    install_requires=[
        "twisted>=15.5.0",
        "pem",
        "service_identity"
    ],
    package_data={
        "public": ["calrissian/public/*."],
    }
)
