import setuptools
import setuptools.command.develop
import setuptools.command.install


class WithCompile:
    def run(self):
        from babel.messages.frontend import compile_catalog

        compiler = compile_catalog(self.distribution)
        option_dict = self.distribution.get_option_dict("compile_catalog")
        compiler.domain = option_dict["domain"][1:]
        compiler.directory = option_dict["directory"][1]
        compiler.run()
        super().run()


class InstallWithCompile(WithCompile, setuptools.command.install.install):
    pass


class DevelopWithCompile(WithCompile, setuptools.command.develop.develop):
    pass


class SDistWithCompile(WithCompile, setuptools.command.sdist.sdist):
    pass


setuptools.setup(
    cmdclass={
        "install": InstallWithCompile,
        "develop": DevelopWithCompile,
        "sdist": SDistWithCompile,
    }
)
