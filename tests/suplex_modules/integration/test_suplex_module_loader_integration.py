import logging
from pathlib import Path

from suplex.suplex_modules.module_constants import SEARCH_MODE
from suplex.suplex_modules.module_loader import load_modules
from suplex.suplex_modules.suplex_module_interface import SuplexModuleInterface


class TestModuleLoadingIntegration:
    def test_load_modules_recursive(self, caplog):
        with caplog.at_level(logging.WARNING):
            test_modules_path = Path(__file__).parent.parent.parent / "test_data" / "test_modules"
            modules = load_modules(dir_path=test_modules_path, mode=SEARCH_MODE.RECURSIVE)

            assert modules
            assert len(modules) == 3

            valid_module_names = [
                "ValidTestModule",
                "AdvancedMultiInheritanceModule",
                "ValidTestModuleAlias",
            ]
            module_names = [module.module_name for module in modules]
            assert set(valid_module_names) == set(module_names)

            # Should trigger an error log for incomplete_suplex_module
            assert len(caplog.records) > 0
            warning_logs = [
                record for record in caplog.records if record.levelno == logging.WARNING
            ]
            assert len(warning_logs) == 1
            assert (
                "Can't instantiate abstract class IncompleteSuplexModule" in warning_logs[0].message
            )

            assert all(isinstance(module, SuplexModuleInterface) for module in modules)

    def test_load_modules_iterative(self, caplog):
        with caplog.at_level(logging.WARNING):
            test_modules_path = Path(__file__).parent.parent.parent / "test_data" / "test_modules"
            modules = load_modules(dir_path=test_modules_path, mode=SEARCH_MODE.ITERATIVE_UNBOUND)

            assert modules
            assert len(modules) == 3

            valid_module_names = [
                "ValidTestModule",
                "AdvancedMultiInheritanceModule",
                "ValidTestModuleAlias",
            ]
            module_names = [module.module_name for module in modules]
            assert set(valid_module_names) == set(module_names)

            # Should trigger an error log for incomplete_suplex_module
            assert len(caplog.records) > 0
            warning_logs = [
                record for record in caplog.records if record.levelno == logging.WARNING
            ]
            assert len(warning_logs) == 1
            assert (
                "Can't instantiate abstract class IncompleteSuplexModule" in warning_logs[0].message
            )
            assert all(isinstance(module, SuplexModuleInterface) for module in modules)
