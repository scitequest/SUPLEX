from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface


class IncompleteSuplexModule(SuplexModuleInterface):
    @property
    def module_name(self) -> str:
        return "IncompleteModule"

    @property
    def module_version(self) -> str:
        return "0.1.0"

    def some_other_method(self):
        pass
