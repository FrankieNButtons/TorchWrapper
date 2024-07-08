"""
All the packed universal functions were stored here.
"""
import types;

def getAPIName(func):
    if isinstance(func, types.FunctionType) or isinstance(func, types.BuiltinFunctionType):
        apiName = func.__module__;
        apiName = apiName + "." + func.__name__;
        return apiName;
    elif isinstance(func, type):
        apiName = func.__module__;
        if func.__name__[-len(func.__name__)+1:] == apiName[-len(func.__name__)+1:]:
            apiName = apiName[:-len(func.__name__)] + func.__name__;
        return apiName;
    elif isinstance(func, types.ModuleType):
        return func.__name__;
# getAPIName(torch.optim.Adam),getAPIName(torch.mul)

def isFromModule(func: types.FunctionType, module: str):
    return getAPIName(func).startswith(module);
# isFuncFromModule(torch.nn.LSTM, "torch")


def getAttributes(module):
    attributes = [];
    for i in dir(module):
        if not i.startswith("__"):
            try:
                attr = getattr(module, i);
                if callable(attr) or isinstance(attr, types.ModuleType):
                    attributes.append(i);
            except AttributeError:
                continue;
            except Exception as e:
                print(f"Error accessing attribute {i} of {module}: {e}");
                continue;
    return attributes;
# getAttributes(torch.optim)



def isDecorated(obj: (types.FunctionType, types.ModuleType, type)):
    return getattr(obj, "isDecorated", False);
# isDecorated(torch.tensor)
