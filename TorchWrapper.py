import functools;
import time;
import types;
import json;
import os;
import operator;
import pandas as pd;
import torch;
import sys;



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
sys.setrecursionlimit(5000);

class TorchWrapper:
    """
    ********************
    Initializing Section
    ********************
    """
    
    # Some const for restoring default or checking steps.
    GOAL_MODULE = "torch";
    DEFAULT_FORMAT = "csv";
    DEFAULT_NAME_EPEC = "timestamp";
    SUPPORTED_FORMATS = ["json", "csv", "html", "xlsx"];
    SUPPORETD_NAME_SPEC = ["timestamp", "datetime", "serial"];

    class ConfigKey:
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
        


    # initialize the wrapper
    def __init__(self, config: dict):
        self.callRecords = {};
        self.config = self.parseConfig(config);

    # restoring default or checking steps.
    def parseConfig(self, config:dict):
        """restoring default or checking steps."""
        # check output directory
        if TorchWrapper.ConfigKey.OUT_DIR not in config:
            raise ValueError("Output directory is required.");
        else:
            assert isinstance(config[TorchWrapper.ConfigKey.OUT_DIR], str);

        # check output format
        if TorchWrapper.ConfigKey.FORMAT in config:
            assert isinstance(config[TorchWrapper.ConfigKey.FORMAT], str);
            format = config[TorchWrapper.ConfigKey.FORMAT];
            if format not in TorchWrapper.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported format {format} for saving result");
        else:
            config[TorchWrapper.ConfigKey.FORMAT] = TorchWrapper.DEFAULT_FORMAT;

        # check output size limits
        if TorchWrapper.ConfigKey.FILE_MAX_SIZE in config:
            assert isinstance(config[TorchWrapper.ConfigKey.FILE_MAX_SIZE], str);
            if config[TorchWrapper.ConfigKey.FILE_MAX_SIZE][-2:] not in ["KB", "MB", "GB"]:
                raise ValueError("maxSize should be defined in the style of `myInt`KB/MB/GB");

        # check output name spec 
        if TorchWrapper.ConfigKey.FILE_NAME_SPEC in config:
            assert isinstance(config[TorchWrapper.ConfigKey.FILE_NAME_SPEC], str);
            name_spec = config[TorchWrapper.ConfigKey.FILE_NAME_SPEC];
            if name_spec not in TorchWrapper.SUPPORETD_NAME_SPEC:
                raise ValueError(f"Unsupported file name spec {name_spec}");
            else:
                config[TorchWrapper.ConfigKey.FILE_NAME_SPEC] = TorchWrapper.DEFAULT_NAME_EPEC;
      
    """
    ******************
    Decorator Section
    ******************
    """
    
    def CountDecorator(self, func: str):
        """
        **Description**
        A decorator that count the call of a function and record it in a dictionary.
        
        **params**
        func(String): the function to be recorded calling times.
        
        **return**
        wrapper: a function that has been counted calling times.
        """
        funcName = getAPIName(func);
        print(f"decorating function {funcName}");
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # initialize the record.            
            record = {
                TorchWrapper.CallRecordKey.ResultKey.CALL_NUMBER: None,
                TorchWrapper.CallRecordKey.ResultKey.START_TIMESTAMP: None,
                TorchWrapper.CallRecordKey.ResultKey.COST_TIME: None,
                TorchWrapper.CallRecordKey.ResultKey.ARGUMENTS: args
            };
            
            # catch the result.
            result, apiName, startTimestamp, costTime = APIDecorator(func)(*args, **kwargs);            
            if apiName in self.callRecords:
                callCount = len(self.callRecords[apiName].keys);
                totalTime = callRecords[apiName][TorchWrapper.CallRecordKey.ResultKey.TOTAL_TIME];
            else:
                callCount = 0;
                totalTime = 0.0;
            
            # Generate the record.
            record[TorchWrapper.CallRecordKey.ResultKey.START_TIMESTAMP] = startTimestamp;
            record[TorchWrapper.CallRecordKey.ResultKey.COST_TIME] = costTime;
            record[TorchWrapper.CallRecordKey.ResultKey.ARGUMENTS] = args;
            totalTime += costTime;
            
            # Saving the record
            self.calRecords[apiName][TorchWrapper.CallRecordKey.ResultKey.TOTAL_TIME] =totalTime;
            self.calRecords[apiName][callCount] = record;
            
            
            return result;
        wrapper.isDecorated = True;
        print(f"{funcName} decorated.");
        return wrapper;
        
    """
    ******************
    Processing Section
    ******************
    """
    
    def decorateClass(self, cls, depth=0, max_depth=30):
        """
        **Description**
        Decorates all the methods of a class with CountDecorator and records the API names.

        **params**
        cls (Class): The class whose methods are to be decorated.
        depth (int): Current recursion depth.
        max_depth (int): Maximum allowed recursion depth.

        **returns**
        cls: The class with its methods decorated.
        """
        clsName = getAPIName(cls);
        if isFromModule(cls,TorchWrapper.GOAL_MODULE):
            if depth > max_depth:
                print(f"Maximum recursion depth {max_depth} exceeded in class {cls.__name__}.");
                return cls;

            try:
                assert isinstance(cls, type), f"`{cls}` must be a class."

                if isDecorated(cls):
                    print(f"module {clsName} has been decorated, out.");
                    return cls;
                cls.isDecorated = True;

                attributes = getAttributes(cls);
                if attributes:
                    print(f"descending into class {cls}, depth={depth}");
                    for name in attributes:
                        print(f"descending into {cls.__name__}.{name}, depth={depth}");
                        method = getattr(cls, name);
                        apiName = getAPIName(method);
                        if isinstance(method, types.FunctionType) and isFromModule(method, TorchWrapper.GOAL_MODULE):
                            print(f"Decorating {apiName}, depth={depth}");
                            setattr(cls, name, self.CountDecorator(method));
                        elif isinstance(method, type) and isFromModule(method, TorchWrapper.GOAL_MODULE) and not isDecorated(method):
                            setattr(cls, name, self.decorateClass(method, depth + 1, max_depth));
#                         elif isinstance(method, types.ModuleType):
#                             setattr(cls, name, self.decorateModule(method));
                            

            except TypeError as e:
                if "immutable type" in str(e):
                    print(f"{cls} is an immutable type, out.");
                    return cls;

            return cls;
        else:
            print(f"class {clsName} is not from module {TorchWrapper}, out.");
            return cls;

    
    
    def decorateModule(self, module: types.ModuleType):
        """
        **Description**
        a function that can wrap the hole module with CountDecorator.

        **params**
        module(String): The name of module to be decorated.
        visited(Set): the module name that has been decorated.

        **returns**
        a module that has been fully decorated.
        """
        moduleName = getAPIName(module);
        if isFromModule(module, TorchWrapper.GOAL_MODULE):
            assert isinstance(module, types.ModuleType), f"`{module}`must be a module.";
            if isDecorated(module):
                print(f"module {moduleName} has been decorated, out.");
                return module;
            module.isDecorated = True;


            for name in getAttributes(module):
                func = getattr(module, name);
                if isinstance(func, types.ModuleType) and isFromModule(func, TorchWrapper.GOAL_MODULE):
                    setattr(module, name, self.decorateModule(func));
                elif isinstance(func, types.FunctionType) and isFromModule(func, TorchWrapper.GOAL_MODULE):
                    if not getattr(func, 'isDecorated', False):
                        print(f"{name} hasn't been decorated, decorate {name}.");
                        decoratedFunc = self.CountDecorator(func);
                        setattr(module, name, decoratedFunc);
                        print(f"{name} hasn't been decorated.")
                elif isinstance(func, type) and isFromModule(func, TorchWrapper.GOAL_MODULE) and not isDecorated(func):
                    setattr(module, name, self.decorateClass(func));
        else:
            print(f"module {moduleName} is a external module, not in {TorchWrapper.GOAL_MODULE}.");
            return module;
    
    """
    **************
    Saving Section
    **************
    """
    
    # parse the usable value from config
    # parse max file size limit;
    def getFileMaxSize(self, config: dict):
        """Though I don't think this is necessary.-- Frankie"""
        if TorchWrapper.ConfigKey.FILE_MAX_SIZE in config:
            maxSize = config[TorchWrapper.ConfigKey.FILE_MAX_SIZE];
            if maxSize.endwith("KB"):
                maxSize = int(maxSize[:-2]) * 1024;
            elif maxSize.endwith("MB"):
                maxSize = int(maxSize[:-2]) * (1024 ** 2);
            elif maxSize.endwith("GB"):
                maxSize = int(maxSize[:-2]) * (1024 ** 3);
            return maxSize;
  
    # get the name of file to save
    def getFileNameSuffix(self):
        file_name_spec = config[TorchWrapper.ConfigKey.FILE_NAME_SPEC];
        if file_name_spec == "timestamp":
            return time.time_ns();
        elif file_name_spec == "datetime":
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime());
        elif file_name_spec == "serial":
            raise NotImplementedError;
                          
    # Prepare the result saving directory
    def setPath(self, path):
        if os.path.exists(path):
            if not os.path.isdir(path):
                raise ValueError(f"Path {path} is not a directory");
        else:
            os.makedirs(path);
        return path;
    
    # get the name of file to save
    def getFileName(self, config: dict) -> str:
        """TODO: parse filename from config dictionary."""
        suffix = self.getFileNameSuffix();
        fileName = f"TorchWrapper_Result_{suffix}";
        return fileName;
    
    # get the name of DataFrame formatted callRecords to save
    def getDFFormattedCallRecords(self):
        """Formats the call records as a pandas DataFrame."""
        records = []
        for apiName, calls in self.callRecords.items():
            totalTime = calls.pop(TorchWrapper.CallRecordKey.ResultKey.TOTAL_TIME, 0);
            for callNumber, call in calls.items():
                record = {
                    TorchWrapper.CallRecordKey.API_NAME: apiName,
                    TorchWrapper.CallRecordKey.ResultKey.TOTAL_TIME: totalTime,
                    TorchWrapper.CallRecordKey.ResultKey.CALL_NUMBER: callNumber,
                    TorchWrapper.CallRecordKey.ResultKey.START_TIMESTAMP: call[TorchWrapper.CallRecordKey.ResultKey.START_TIMESTAMP],
                    TorchWrapper.CallRecordKey.ResultKey.COST_TIME: call[TorchWrapper.CallRecordKey.ResultKey.COST_TIME],
                    TorchWrapper.CallRecordKey.ResultKey.ARGUMENTS: call[TorchWrapper.CallRecordKey.ResultKey.ARGUMENTS]
                };
                records.append(record);
        return pd.DataFrame(records);
    
    # Save the result to specific file
    def saveRecord(self, config: dict):
        def saveToJson(data, path: str, fileName: str):
            """Save DataFrame formatted call records to a .json file."""
            data.to_json(f"{path}/{fileName}.json", orient='records', lines=True);
            
        def saveToCSV(data, path: str, fileName: str):
            """Save DataFrame formatted call records to a .csv file."""
            data.to_csv(f"{path}/{fileName}.csv", index=False);
            
        def saveToExcel(data, path: str, fileName: str):
            """Save DataFrame formatted call records to a .xlsx file."""
            data.to_excel(f"{path}/{fileName}.xlsx", index=False);
            
        def saveToHTML(data, path: str, fileName: str):
            """Save DataFrame formatted call records to a .html file."""
            data.to_html(f"{path}/{fileName}.html", index=False);
            
        fileName = self.getFileName(config);
        data = self.getDFFormattedCallRecords();
        outputPath = self.setPath(config[TorchWrapper.ConfigKey.OUT_DIR]);
        if config[TorchWrapper.ConfigKey.FORMAT] == "json":
            saveToJson(data, outputPath, fileName);
        elif config[TorchWrapper.ConfigKey.FORMAT] == "csv":
            saveToCSV(data, outputPath, fileName);
        elif config[TorchWrapper.ConfigKey.FORMAT] == "xlsx":
            saveToExcel(data, outputPath, fileName);
        elif config[TorchWrapper.ConfigKey.FORMAT] == "html":
            saveToHTML(data, outputPath, fileName);

    """
    ******************
    Main Usage Section
    ******************
    """
    
    def start(self, func: types.FunctionType):
        """
        **Description**
        Starts the wrapping and recording process.

        **params**
        func(FunctionType): The function to be executed and recorded.
        
        **raises**
        ValueError: If there is an error executing the function.
        """
        print(f"Starts decorating torch module.");
        self.decorateModule(torch);
        print("torch module decorating complete.");
        try:
            print(f"Starts evaluating {func.__name__}");
            func();
            
        except Exception as e:
            raise ValueError("Error executing the function.") from e;
        print("start saving results.");
        self.saveRecord(config);
        print(f"results file saved.");
