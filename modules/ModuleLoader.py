import os
import sys
import importlib
import pkgutil
import inspect
import ast
from .SuplexModuleInterface import SuplexModuleInterface

def loadOperationModules():
    dirPath = os.path.dirname(os.path.abspath(__file__))
    modules = []
    getModulesOfDir(dirPath, modules)
    return modules

def getModulesOfDir(searchDir, modules):
    for item in os.listdir(searchDir):
        dirPath = os.path.join(searchDir, item)
        
        if os.path.isdir(dirPath):
            if '.ipynb_checkpoints' not in dirPath:
                getModulesOfDir(dirPath, modules)

        elif item.endswith('.py') and '.ipynb_checkpoints' not in dirPath:
            modules += getCompatibleModules(dirPath, item)                          

def getCompatibleModules(path, moduleName):
    moduleObjects = []

    with open(path, "r") as file:
        node = ast.parse(file.read(), filename=path)
    
    loadModule = False
    for item in node.body:
        if isinstance(item, ast.ClassDef):
            loadModule = True
            break
    
    if loadModule:
        spec = importlib.util.spec_from_file_location(moduleName, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, SuplexModuleInterface) and obj is not SuplexModuleInterface:
                moduleObjects.append(obj())
                # Import the class into the current namespace.
                globals()[name] = obj

    return moduleObjects