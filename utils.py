"""
All the packed universal functions were stored here.
"""
import types;





def isFuncFromModule(func: types.FunctionType, module: str):
    return func.__module__.startswith(module);
# isFuncFromModule(torch.nn.LSTM, "torch")


def getAttributes(module):
    return [i for i in dir(module) if not i.startswith("__") and callable(getattr(module, i)) or isinstance(getattr(module, i), types.ModuleType)];
# getAttributes(torch.optim)


def getAPIName(func):
    if isinstance(func, types.FunctionType) or isinstance(func, types.BuiltinFunctionType):
        apiName = func.__module__ + "." + func.__name__;
        return apiName;
    elif isinstance(func, type):
        apiName = func.__module__;
        if func.__name__[-len(func.__name__)+1:] == apiName[-len(func.__name__)+1:]:
            apiName = apiName[:-len(func.__name__)] + func.__name__;
        return apiName;
    elif isinstance(func, types.ModuleType):
        return func.__name__;
# getAPIName(torch.optim.Adam),getAPIName(torch.mul)



def isDecorated(func):
    return getattr(func, "isDecorated", False);
 # isDecorated(torch.tensor)
