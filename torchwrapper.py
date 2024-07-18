import functools;
import time;
import types;
# import json;
import os;
# import operator;
import pandas as pd;
import torch;
# import sys;

from .apitools import *;
from.decorators import APIDecorator;



"""
*****************************
The Structure For callRecords
*****************************
callRecords
│
├── API_1
│   │
│   ├── TotalTime(ms): 150.0
│   │
│   ├── 1
│   │   ├── detailedAPIName: 
│   │   ├── StartTimestamp: 1625150800123456789
│   │   ├── CostTime(ms): 50.0
│   │   └── Arguments: (arg1, arg2, ...)
│   │
│   ├── 2
│   │   ├── detailedAPIName: 
│       ├── StartTimestamp: 1625150860123456789
│       ├── CostTime(ms): 100.0
│       └── Arguments: (arg1, arg2, ...)
│
├── API_2
│   │
│   ├── TotalTime(ms): 200.0
│   │
│   ├── 1
│   │   ├── detailedAPIName: 
│       ├── StartTimestamp: 1625150900123456789
│       ├── CostTime(ms): 200.0
│       └── Arguments: (arg1, arg2, ...)
"""
# sys.setrecursionlimit(500);

class TorchWrapper:
    """
    A wrapper class for torch functions and modules to record API call details.
    """

    """
    ********************
    Initializing Section
    ********************
    """

    GOAL_MODULE = "torch";
    DEFAULT_PATH = "./results"
    DEFAULT_FORMAT = "csv";
    DEFAULT_NAME_SPEC = "timestamp";
    SUPPORTED_FORMATS = ["json", "csv", "html", "xlsx"];
    SUPPORTED_NAME_SPEC = ["timestamp", "datetime", "serial"];

    class ConfigKey:
        GOAL_MODULE = "goal_module";
        OUT_DIR = "out_dir";
        FORMAT = "format";
        FILE_MAX_SIZE = "file_max_size";
        FILE_NAME_SPEC = "file_name_spec";

    class CallRecordKey:
        API_NAME = "APIName";

        class ResultKey:
            TOTAL_TIME = "TotalTime(ms)";
            CALL_NUMBER = "CallNumber";
            START_TIMESTAMP = "StartTimestamp";
            COST_TIME = "CostTime(ms)";
            ARGUMENTS = "Arguments";

    def __init__(self, config: dict):
        """
        **Description**
        Initialize the TorchWrapper with the provided configuration.

        **params**
        config (dict): The configuration dictionary.
        """
        self.callRecords = {};
        self.config = self.parseConfig(config);
        print(f"your wrapper config: {self.getConfig()}");

    def parseConfig(self, config: dict) -> dict:
        """
        **Description**
        Parse and validate the configuration dictionary.

        **params**
        config (dict): The configuration dictionary.

        **returns**
        dict: The parsed and validated configuration.

        **raises**
        ValueError: If any required configuration is invalid.
        """
        if TorchWrapper.ConfigKey.OUT_DIR not in config:
            raise ValueError("Output directory is required.");
        assert isinstance(config[TorchWrapper.ConfigKey.OUT_DIR], str);

        if TorchWrapper.ConfigKey.FORMAT in config:
            assert isinstance(config[TorchWrapper.ConfigKey.FORMAT], str);
            format = config[TorchWrapper.ConfigKey.FORMAT];
            if format not in TorchWrapper.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported format {format} for saving result");
        else:
            config[TorchWrapper.ConfigKey.FORMAT] = TorchWrapper.DEFAULT_FORMAT;

        if TorchWrapper.ConfigKey.FILE_MAX_SIZE in config:
            assert isinstance(config[TorchWrapper.ConfigKey.FILE_MAX_SIZE], str);
            if config[TorchWrapper.ConfigKey.FILE_MAX_SIZE][-2:] not in ["KB", "MB", "GB"]:
                raise ValueError("maxSize should be defined in the style of `myInt`KB/MB/GB");

        if TorchWrapper.ConfigKey.FILE_NAME_SPEC in config:
            assert isinstance(config[TorchWrapper.ConfigKey.FILE_NAME_SPEC], str);
            name_spec = config[TorchWrapper.ConfigKey.FILE_NAME_SPEC];
            if name_spec not in TorchWrapper.SUPPORTED_NAME_SPEC:
                raise ValueError(f"Unsupported file name spec {name_spec}");
        else:
            config[TorchWrapper.ConfigKey.FILE_NAME_SPEC] = TorchWrapper.DEFAULT_NAME_SPEC;

        return config;

    def getConfig(self) -> dict:
        return self.config;

    """
    ******************
    decorating Section
    ******************
    """

    def CountDecorator(self, func: types.FunctionType) -> types.FunctionType:
        """
        **Description**
        A decorator that counts the calls of a function and records it.

        **params**
        func (types.FunctionType): The function to be recorded calling times.

        **returns**
        types.FunctionType: A function that has been counted calling times.
        """
        funcName = getAPIName(func);

        # print(f"decorating function {funcName}");
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            record = {
                TorchWrapper.CallRecordKey.ResultKey.CALL_NUMBER: None,
                TorchWrapper.CallRecordKey.ResultKey.START_TIMESTAMP: None,
                TorchWrapper.CallRecordKey.ResultKey.COST_TIME: None,
                TorchWrapper.CallRecordKey.ResultKey.ARGUMENTS: (args, kwargs)
            };

            result, apiName, startTimestamp, costTime = APIDecorator(func)(*args, **kwargs);
            if apiName in self.callRecords:
                callCount = len(self.callRecords[apiName].keys());
                totalTime = self.callRecords[apiName][TorchWrapper.CallRecordKey.ResultKey.TOTAL_TIME];
            else:
                callCount = 1;
                totalTime = 0.0;

            record[TorchWrapper.CallRecordKey.ResultKey.START_TIMESTAMP] = startTimestamp;
            record[TorchWrapper.CallRecordKey.ResultKey.COST_TIME] = costTime;
            totalTime += costTime;

            self.callRecords.setdefault(apiName, {})[TorchWrapper.CallRecordKey.ResultKey.TOTAL_TIME] = totalTime;
            self.callRecords[apiName][callCount] = record;

            return result;

        wrapper._isDecorated = True;
        # print(f"{funcName} decorated.");
        return wrapper;

    def decorateFunction(self, module: (types.ModuleType, type), name: str, \
                         func: (types.FunctionType, types.BuiltinFunctionType, types.MethodType)):
        setattr(module, name, self.CountDecorator(func));

    def decorateClass(self, cls: type, visitedModules: list = None, visitedClasses: list = None):
        """
        **Description**
        Decorates all methods of a class with CountDecorator and records the API names.

        **params**
        cls (type): The class whose methods are to be decorated with CountDecorator.

        **returns**
        None
        """
        clsName = getAPIName(cls);
        if isFromModule(cls, TorchWrapper.GOAL_MODULE):
            assert isinstance(cls, type), f"`{cls}` must be a class.";

            if isDecorated(cls, visitedClasses) or isDecorated(cls, visitedModules):
                print(f"\t\t[IntoOldClass] Class `{clsName}` has been visited, return.");
                return;  # Stop decoration don't need specific returns
            print(f"\t\t[IntoNewClass] Class `{clsName}` is not visited, visit it.");
            if visitedClasses == None:
                visitedClasses = [];
            if visitedModules == None:
                visitedModules = [];
            visitedClasses.append(clsName);

            attributes = getAttributes(cls);
            if attributes:
                for name in attributes:
                    try:
                        # cls._isDecorated = True;
                        cattr = getattr(cls, name);
                        apiName = getAPIName(cattr);

                        if isinstance(cattr,
                                      (types.FunctionType, types.BuiltinFunctionType, types.BuiltinMethodType)) and \
                                isFromModule(cattr, TorchWrapper.GOAL_MODULE) and not isDecorated(cattr):
                            if clsName not in apiName:
                                print(
                                    f"\t\t[Method] Method `{apiName}` hasn't been decorated, but imported to parent module, decorate later.");
                                continue;
                            else:
                                print(
                                    f"\t\t[Method] Method `{apiName}` hasn't been decorated, \n\t\tdecorating `{apiName}`.");
                                self.decorateFunction(cls, name, cattr);
                                print(f"\t\tMethod `{apiName}` has been decorated.");

                        elif isinstance(cattr, (type, types.ModuleType)) and isFromModule(cattr,
                                                                                          TorchWrapper.GOAL_MODULE) \
                                and not isDecorated(cattr, visitedModules) and not isDecorated(cattr, visitedClasses):
                            print(
                                f"\t\t[SubClass] SubClass `{apiName}` hasn't been decorated, \n\t\tdecorating `{apiName}`.");
                            self.decorateClass(cattr, visitedModules, visitedClasses);
                            print(f"\t\tSubClass `{apiName}` has been decorated.");


                    except TypeError as e:
                        if "immutable type" in str(e):
                            raise TypeError(f"\t[IMU]`{name}` is an immutable type, out.") from e;
                            print(f"\t[IMU]`{name}` is an immutable type, decorate the whole.");
                            continue;
                        raise NameError(f"[decorateClass]The attribute that cause the Error: `{name}`") from e;
        else:
            print(
                f"\t[EXTCLS]Class `{clsName}` is a external class or subclass, not inside `{TorchWrapper.GOAL_MODULE}`, out.");
            return;

    def decorateModule(self, module: types.ModuleType, visitedModules: list = None, visitedClasses: list = None):
        """
        **Description**
        Decorates all functions and classes of a module with CountDecorator.

        **params**
        module (types.ModuleType): The module to be decorated.

        **returns**
        None
        """
        moduleName = getAPIName(module);
        if isFromModule(module, TorchWrapper.GOAL_MODULE):
            assert isinstance(module, types.ModuleType), f"`{module}` must be a module.";
            if isDecorated(module, visitedModules):
                print(f"[OldModule] Module `{moduleName}` has been visited, return.");
                return;  # Stop the decoration, no specific return.
            print(f"\t[NewModule] Module `{moduleName}` is not visited, visit it.");
            # module._isDecorated = True;
            if visitedClasses == None:
                visitedClasses = [];
            if visitedModules == None:
                visitedModules = [];
            visitedModules.append(moduleName);

            for name in getAttributes(module):
                try:
                    mattr = getattr(module, name);
                    apiName = getAPIName(mattr);

                    if isinstance(mattr, types.ModuleType) and isFromModule(mattr, TorchWrapper.GOAL_MODULE):

                        print(
                            f"\t[SubModule]Submodule `{apiName}` of {moduleName} hasn't been decorated, \n\tdecorating {name}.");
                        self.decorateModule(mattr, visitedModules, visitedClasses);
                        if isDecorated(mattr, visitedModules):
                            print(f"\t[SubModule]Submodule `{apiName}` has been decorated.");

                    elif isinstance(mattr, (types.FunctionType, types.BuiltinFunctionType, types.BuiltinMethodType)) \
                            and isFromModule(mattr, TorchWrapper.GOAL_MODULE) and not isDecorated(mattr):

                        print(f"\t[Operator]Operator `{apiName}` hasn't been decorated, \n\tdecorating {apiName}.");
                        self.decorateFunction(module, name, mattr);
                        if isDecorated(mattr):
                            print(f"\t[Operator]Opertator `{apiName}` has been decorated.");

                    elif isinstance(mattr, type) and isFromModule(mattr, TorchWrapper.GOAL_MODULE) and not isDecorated(
                            mattr, visitedClasses):

                        print(
                            f"\t[SubClass]SubClass `{apiName}` of {moduleName} hasn't been decorated, \n\tdecorating {apiName}.");
                        self.decorateClass(mattr, visitedModules, visitedClasses);
                        if isDecorated(mattr, visitedClasses):
                            print(f"\t[SubClass]SubClass `{apiName}` has been decorated.");
                    elif isDecorated(mattr) or isDecorated(mattr, visitedModules) or isDecorated(mattr, visitedClasses):
                        print(f"\t[Decorated]Attribute `{apiName}` of {moduleName} has been decorated, out.");

                    elif not isFromModule(mattr, TorchWrapper.GOAL_MODULE):
                        print(
                            f"[EXTATTR]`{apiName}` is a external attribute, not inside `{TorchWrapper.GOAL_MODULE}`, out.");

                    else:
                        print(
                            f"\t[SkipDecoration]Attribute `{apiName}` of {moduleName} skiped decoration, for unknow reason.");



                except Exception as e:
                    raise NameError(f"[decorateModule]The attribute that cause Error: `{name}`") from e;
                    print(f"The attribute that cause Error: `{name}`");
                    continue;


        else:
            print(f"[EXTMOD]module {moduleName} is a external module, not in {TorchWrapper.GOAL_MODULE}, out.");

    """
    ******************
    Processing Section
    ******************
    """

    def getFileMaxSize(self, config: dict) -> int:
        """
        **Description**
        Parse the max file size limit from the configuration.

        **params**
        config (dict): The configuration dictionary.

        **returns**
        int: The max file size in bytes.

        **raises**
        ValueError: If the max size format is invalid.
        """
        if TorchWrapper.ConfigKey.FILE_MAX_SIZE in config:
            maxSize = config[TorchWrapper.ConfigKey.FILE_MAX_SIZE];
            if maxSize.endswith("KB"):
                return int(maxSize[:-2]) * 1024;
            elif maxSize.endswith("MB"):
                return int(maxSize[:-2]) * (1024 ** 2);
            elif maxSize.endswith("GB"):
                return int(maxSize[:-2]) * (1024 ** 3);
            else:
                raise ValueError("maxSize should be defined in the style of `myInt`KB/MB/GB(e.g.'64MB')");
        return None;

    def getFileNameSuffix(self) -> str:
        """
        **Description**
        Get the file name suffix based on the configuration.

        **returns**
        str: The file name suffix.

        **raises**
        NotImplementedError: If the file name specification is not implemented.
        """
        file_name_spec = self.config[TorchWrapper.ConfigKey.FILE_NAME_SPEC];
        if file_name_spec == "timestamp":
            return str(time.time_ns());
        elif file_name_spec == "datetime":
            return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime());
        elif file_name_spec == "serial":
            raise NotImplementedError("Serial file name specification is not implemented.");
        return ""

    def setPath(self, path: str) -> str:
        """
        **Description**
        Prepare the result saving directory.

        **params**
        path (str): The directory path.

        **returns**
        str: The validated directory path.

        **raises**
        ValueError: If the path is not a directory.
        """
        if os.path.exists(path):
            if not os.path.isdir(path):
                raise ValueError(f"Path {path} is not a directory");
        else:
            os.makedirs(path);
        return path;

    def getFileName(self, config: dict) -> str:
        """
        **Description**
        Get the file name for saving the results.

        **returns**
        str: The file name.
        """
        suffix = self.getFileNameSuffix();
        return f"TorchWrapper_Result_{suffix}";

    def getDFFormattedCallRecords(self) -> pd.DataFrame:
        """
        **Description**
        Formats the call records as a pandas DataFrame.

        **returns**
        pd.DataFrame: The formatted call records.
        """
        records = []
        for apiName, calls in self.callRecords.items():
            totalTime = calls.pop(TorchWrapper.CallRecordKey.ResultKey.TOTAL_TIME, 0);
            for callNumber, call in calls.items():
                record = {
                    TorchWrapper.CallRecordKey.API_NAME: apiName,
                    TorchWrapper.CallRecordKey.ResultKey.TOTAL_TIME: totalTime,
                    TorchWrapper.CallRecordKey.ResultKey.CALL_NUMBER: callNumber,
                    TorchWrapper.CallRecordKey.ResultKey.START_TIMESTAMP: call[
                        TorchWrapper.CallRecordKey.ResultKey.START_TIMESTAMP],
                    TorchWrapper.CallRecordKey.ResultKey.COST_TIME: call[
                        TorchWrapper.CallRecordKey.ResultKey.COST_TIME],
                    TorchWrapper.CallRecordKey.ResultKey.ARGUMENTS: call[TorchWrapper.CallRecordKey.ResultKey.ARGUMENTS]
                };
                records.append(record);
        return pd.DataFrame(records);

    def saveRecords(self, config: dict):
        """
        **Description**
        Save the call records to a file based on the configuration.

        **params**
        config (dict): The configuration dictionary.
        """

        # define saving function
        def saveToJson(data: pd.DataFrame, path: str, fileName: str):
            data.to_json(f"{path}/{fileName}.json", orient='records', lines=True);
            return f"{path}/{fileName}.json";

        def saveToCSV(data: pd.DataFrame, path: str, fileName: str):
            data.to_csv(f"{path}/{fileName}.csv", index=False);

        def saveToExcel(data: pd.DataFrame, path: str, fileName: str):
            data.to_excel(f"{path}/{fileName}.xlsx", index=False);

        def saveToHTML(data: pd.DataFrame, path: str, fileName: str):
            data.to_html(f"{path}/{fileName}.html", index=False);

        # prepare saving content
        fileName = self.getFileName(config);
        data = self.getDFFormattedCallRecords();
        outputPath = self.setPath(config[TorchWrapper.ConfigKey.OUT_DIR]);

        # save to file
        if config[TorchWrapper.ConfigKey.FORMAT] == "json":
            saveToJson(data, outputPath, fileName);
            return f"{outputPath}/{fileName}.json";
        elif config[TorchWrapper.ConfigKey.FORMAT] == "csv":
            saveToCSV(data, outputPath, fileName);
            return f"{outputPath}/{fileName}.csv";
        elif config[TorchWrapper.ConfigKey.FORMAT] == "xlsx":
            saveToExcel(data, outputPath, fileName);
            return f"{outputPath}/{fileName}.xlsx";
        elif config[TorchWrapper.ConfigKey.FORMAT] == "html":
            saveToHTML(data, outputPath, fileName);
            return f"{outputPath}/{fileName}.html";

    """
    **************
    Usable Section
    **************
    """

    def start(self, func: types.FunctionType):
        """
        **Description**
        Starts the wrapping and recording process.

        **params**
        func (types.FunctionType): The function to be executed and recorded.

        **returns**
        Any: The result of the executed function.
        callRecords: the DataFrameFormatted callRecords.

        **raises**
        ValueError: If there is an error executing the goal function.
        """

        # decorate the module to be evaluated
        print(f"Starts decorating torch module.");
        self.decorateModule(torch);
        print("torch module decorating complete.");

        # run the codes to be evaluated.
        try:
            print(f"Starts evaluating {func.__name__}");
            result = func();

        except Exception as e:
            path = self.saveRecords(self.config);
            print(f"Error executing the function: {e}");
            print(f"But your running Status up to now has been saved to {path}");
            raise ValueError("Error executing the function, check your code first.") from e;

        # saving the results
        print("start saving results.");
        path = self.saveRecords(self.config);
        print(f"results file saved to `{path}`");
        return result, self.getDFFormattedCallRecords();
