import os;
import importlib;
import logging;

def getCWDClasses(cls: type = None) -> None:
    """
    Import all classes from Python scripts in the current working directory.

    **params**
    cls: type, optional
        If provided, only classes that are subclasses of `cls` will be imported.

    **returns**
    None
    """
    
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s');
    logger = logging.getLogger(__name__);
    
    current_directory: str = os.path.dirname(os.path.abspath(__file__));
    script_files: list = [f for f in os.listdir(current_directory) if f.endswith('.py') and f != '__init__.py'];
    
    for script_file in script_files:
        module_name: str = script_file[:-3];  # Remove the .py extension
        try:
            module = importlib.import_module(f'.{module_name}', package=__package__);
            # logger.debug(f"Successfully imported module {module_name}");
        except Exception as e:
            logger.debug(f"Failed to import module {module_name}: {e}");
            continue;
    
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name);
            if not cls:
                if isinstance(attribute, type):
                    globals()[attribute_name] = attribute;
            elif isinstance(cls, type) and isinstance(attribute, type) and issubclass(attribute, cls):
                globals()[attribute_name] = attribute;
            else:
                assert isinstance(cls, type), f"{cls.__name__} must be a class.";
                # print(type(TorBencherTestCaseBase));
