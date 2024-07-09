# TorchWarpper
## Introduction
a performance evaluating wrapper for Python module torch.


## User Manual
### import TorchWrapper and torch module
```python
from TorchWrapper import TorchWrapper;
import torch;
```
### set configuration
define a config in the structure below
```python
config = {
    "out_dir": "./output",
    "format": "csv",
    "file_max_size": "10MB",
    "file_name_spec": "timestamp"
};
```
and the default config has been set as:
```python
config = {
    "out_dir": "./output",
    "format": "json",
    "file_max_size": "128MB",
    "file_name_spec": "timestamp"
};
``
### Instantiation
```python
wrapper = TorchWrapper(config);
```
### pack your torch code in a function
e.g. a very simple function myCode:
```python
def myCode():
    a = torch.randn(1, 3);
    b = torch.randn(1, 3);
    c = a + b;
    return c;
```
### runyour code with TorchWrapper decorated:
```python
wrapper.start(myCode);
```
Then your extimation of performance will be saved to path `out_dir` defined in your `config`.
### Some important Data Structures you might like to know
#### callRecords
```
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
```

## Utilities
### 日记板块
#### 2024年7月6日
我不喜欢拖，但如果我没能看到自己进度有多慢，我便做不到再接再厉。
#### 2024年7月7日
今天是七七事变87周年，但是我一天都泡在家里改这个东西，结果还是没有什么进展，因为还是没跑通，就没有上传，现在想想，还是先传一点吧。

#### 2024年7月8日
##### 14:00
好诶！！！有点进度了！！！！！！
##### 18:20
心累了，问题还是很多，已经尝试了：
1. 增加递归深度（但直接溢出）
2. 增加拓扑层数限制（无效）
3. 指定`torch`模组子块（能跑，但没看出明显变化）
4. ......

修复了：
1. config的返回问题
2. 各种self的指定
3. ......

待解决：
1. 装饰对象的类型问题
2. 装饰函数的完整性问题
3. 递归调用的冗余循环问题
4. ......

#### 2024年7月9日
##### 11:55
ChatGPT是用不得的！！！
昨天开始图快用GPT很快的改一些Bugs，结果给我的decorateClass和decorateModules全部搞乱了，现在起我决定全部重新执手，不能再让他扰乱我进度了，可以啊，GPT-4o你小样，脱了我两天的进度。

还有我依然坚持自己写的代码有;结尾，而GPT的代码留空以示区分。
#####16:15
有进展啦！！！！！经过我一下午的修改和debug，result文件里已经可以跑出结果啦！！！！！现在就差对不同的方法类型做进一步的排查啦！！！！！
