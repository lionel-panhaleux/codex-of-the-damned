import setuptools
import setuptools.command.develop
import setuptools.command.install


class InstallWithCompile(setuptools.command.install.install):
    def run(self):
        from babel.messages.frontend import compile_catalog

        compiler = compile_catalog(self.distribution)
        compiler.domain = ["messages"]
        compiler.directory = "codex_of_the_damned/translations"
        compiler.run()
        super().run()


class DevelopWithCompile(setuptools.command.develop.develop):
    def run(self):
        from babel.messages.frontend import compile_catalog

        compiler = compile_catalog(self.distribution)
        compiler.domain = ["messages"]
        compiler.directory = "codex_of_the_damned/translations"
        compiler.run()
        super().run()


setuptools.setup(
    cmdclass={"install": InstallWithCompile, "develop": DevelopWithCompile}
)
