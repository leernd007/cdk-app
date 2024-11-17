from projen.awscdk import AwsCdkPythonApp

project = AwsCdkPythonApp(
    author_email="leerndeg@gmail.com",
    author_name="Andrii",
    cdk_version="2.1.0",
    module_name="simple_cdk_app",
    name="simple_cdk_app",
    version="0.1.0",
)

project.synth()