import functools;
import time;
import types;
import json;
import os;
import operator;
import pandas as pd;
import torch;
from .utils import *;
from .decorators import *;

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
│   │   ├── StartTimestamp: 1625150800123456789
│   │   ├── CostTime(ms): 50.0
│   │   └── Arguments: (arg1, arg2, ...)
│   │
│   ├── 2
│       ├── StartTimestamp: 1625150860123456789
│       ├── CostTime(ms): 100.0
│       └── Arguments: (arg1, arg2, ...)
│
├── API_2
│   │
│   ├── TotalTime(ms): 200.0
│   │
│   ├── 1
│       ├── StartTimestamp: 1625150900123456789
│       ├── CostTime(ms): 200.0
│       └── Arguments: (arg1, arg2, ...)
"""

class TorchWrapper:
    """
    ********************
    Initializing Section
    ********************
    """
    
    # Some const for restoring default or checking steps.
    DEFAULT_FORMAT = "csv";
    DEFAULT_NAME_EPEC = "timestamp";
    SUPPORTED_FORMATS = ["json", "csv", "html"];
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
    def CountDecorator(func: str):
        """
        **Description**
        A decorator that count the call of a function and record it in a dictionary.
        
        **params**
        func(String): the function to be recorded calling times.
        
        **return**
        wrapper: a function that has been counted calling times.
        """
        @functools.warps(func)
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
        return wrapper;
        
    """
    ******************
    Processing Section
    ******************
    """
    
    def decorateModule(self, module: types.ModuleType, visited=None: set):
        """
        **Description**
        a function that can wrap the hole module with CountDecorator.

        **params**
        module(String): The name of module to be decorated.
        visited(Set): the module name that has been decorated.

        **returns**
        a module that has been fully decorated.
        """
        assert isinstance(module), "`module`must be a module.";
        
        if visited = None:
            visited = None;
        elif module in visited:
            return;
        visited.add(getAPIName(module))
            
        
        for name in getAttribututes(module):
            print("descending into {} from ")
            func = getattr(module, name);
            if isinstance(func, types.ModuleType):
                setattr(module, func.__name__, decorateModule(func, visited));
            elif isinstance(func, types.FunctionType):
                decoratedFunc = CountDecorator(func);
                setattr(module, func.__name__, decoratedFunc);
    
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
  
                          
    def getFileNameSuffix(self, file_name_spec: str):
        if file_name_spec == "timestamp":
            return time.time_ns();
        elif file_name_spec == "datetime":
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime());
        elif file_name_spec == "serial":
            raise NotImplementedError;
                          
    # Prepare the result saving directory
    def setPath(path):
        if os.path.exists(path):
            if not os.path.isdir(path):
                raise ValueError(f"Path {path} is not a directory");
        else:
            os.makedirs(path);
        return path;
    
        
        
    # 
    def saveRecord(config: dict, fileName: str):
        def getFileName():
            
        def saveToJson(fileName: str):
            """TODO: save DataFrame formatted callRecorded to a .json file."""
            
        def saveToCSV(fileName: str):
            """TODO: save DataFrame formatted callRecorded to a .csv file."""
            
        def saveToExcel(fileName: str):
            """TODO: save DataFrame formatted callRecorded to a .excel file."""
            
        def saveToHTML(fileName: str):
            """TODO: save DataFrame formatted callRecorded to a .html file"""
            
        def getFileName(config: dict) -> str:
        
        
        getFileName(config);
        data = self.getDFFormattedCallRecords();

    """
    ******************
    Main Usage Section
    ******************
    """
    
        def start(self, func):
            """
            **Description**
            """
            config = self.parseConfig(config);
            self.decorateModule(torch);
            func()
            
            fileName = self.getFileNameSuffix(config);
            #  self.saveReport(self.callRecords);
        
