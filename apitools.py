"""
All the packed universal functions are stored here.
"""
import types;
import typing;

def getAPIName(api: typing.Any) -> str:
    """
    **description**
    Get the fully qualified name of a given API.

    **params**
    api: typing.Any - The API whose name is to be retrieved.

    **returns**
    str - The fully qualified name of the API.
    """
    try:
        # for function type
        if isinstance(api, (types.FunctionType, types.BuiltinFunctionType)):
            apiName = api.__module__ + "." + api.__name__;
            return apiName;

        # for class type
        elif isinstance(api, type):
            apiName = api.__module__;
            if api.__name__[-len(api.__name__) + 1:] == apiName[-len(api.__name__) + 1:]:
                apiName = apiName[:-len(api.__name__)] + api.__name__;
                return apiName;
            apiName = apiName + "." + api.__name__;
            return apiName;

        # for module type
        elif isinstance(api, types.ModuleType):
            return api.__name__;

        # for types from typing
        elif api.__module__ == "typing":
            apiName = api.__module__ + "." + api.__name__;
            return apiName;

        # no more consideration
        else:
            return str(type(api));
    except Exception as e:
        if "" in str(e):
            return "Individual Type: " + str(api.__class__);
        else:
            print(str(e));
            return "";

def isFromModule(api: types.FunctionType, module: str) -> bool:
    """
    **description**
    Check if the given API is from a specified module.

    **params**
    api: types.FunctionType - The API to check.
    module: str - The module name to check against.

    **returns**
    bool - True if the API is from the specified module, False otherwise.
    """
    return getAPIName(api).startswith(module);

def getParent(obj: (type, types.ModuleType, types.FunctionType, types.BuiltinFunctionType)) -> types.ModuleType:
    """
    **description**
    Get the shortest parent module of an object.

    **params**
    obj: (type, types.ModuleType, types.FunctionType, types.BuiltinFunctionType) - The object to get the parent module of.

    **returns**
    types.ModuleType - The parent module of the object.
    """
    apiName = getAPIName(obj);
    return eval(apiName[:apiName.rfind(".")]);

def getAttributes(module: types.ModuleType) -> list:
    """
    **description**
    Get the callable and usable attributes of a module.

    **params**
    module: types.ModuleType - The module to get attributes from.

    **returns**
    list - A list of callable and usable attributes of the module.
    """
    attributes = [];
    try:
        attributes = [i for i in module.__dict__.keys() if not "__" in i and callable(getattr(module, i, None)) or isinstance(getattr(module, i, None), types.ModuleType)];
    except AttributeError as e:
        return attributes;
    return attributes;

def testDirectAttr(obj: (type, types.ModuleType)):
    """
    **description**
    Test the attributes status of an object and print their details.

    **params**
    obj: (type, types.ModuleType) - The object to test attributes of.
    """
    for name in getAttributes(obj):
        try:
            attr = getattr(obj, name);
            print(f"{getAPIName(attr):<70}{name:<65}{isFromModule(attr, getAPIName(obj))}");
        except Exception as e:
            raise NameError(f"The attribution that cause error is {name}") from e;

def testTorch(obj: (type, types.ModuleType)):
    """
    **description**
    Test the attributes status of a torch object and print their details.

    **params**
    obj: (type, types.ModuleType) - The torch object to test attributes of.
    """
    for name in getAttributes(obj):
        try:
            attr = getattr(obj, name);
            print(f"{getAPIName(attr):<70}{name:<65}{isFromModule(attr, 'torch')}");
        except Exception as e:
            raise NameError(f"The attribution that cause error is {name}") from e;

def isDecorated(obj: typing.Any, visited: list = None) -> bool:
    """
    **description**
    Check if an object is decorated.

    **params**
    obj: typing.Any - The object to check.
    visited: list - A list of visited objects to avoid recursion.

    **returns**
    bool - True if the object is decorated, False otherwise.
    """
    if visited is None:
        return getattr(obj, "_isDecorated", False);
    else:
        return getAPIName(obj) in visited;

