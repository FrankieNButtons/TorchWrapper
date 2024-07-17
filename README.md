# TorchWarpper
## Introduction
a performance evaluating wrapper for Python module torch.


## User Manual
### TorchWrapper
#### import TorchWrapper and torch module
```python
from TorchWrapper import TorchWrapper;
import torch;
```
#### set configuration
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
```
#### Instantiation
```python
wrapper = TorchWrapper(config);
```
#### pack your torch code in a function
e.g. a very simple function myCode:
```python
def myCode():
    a = torch.randn(1, 3);
    b = torch.randn(1, 3);
    c = a + b;
    return c;
```
#### run your code with TorchWrapper decorated:
```python
wrapper.start(myCode);
```
Then your extimation of performance will be saved to path `out_dir` defined in your `config`.
#### Some important Data Structures you might like to know
##### callRecords
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
│   │   └── Arguments: ((arg1, arg2, ...), {"kwarg1": val1, "kwarg2": val2, ...})
│   │
│   ├── 2
│   │   ├── detailedAPIName: 
│       ├── StartTimestamp: 1625150860123456789
│       ├── CostTime(ms): 100.0
│       └── Arguments: ((arg1, arg2, ...), {"kwarg1": val1, "kwarg2": val2, ...})
│
├── API_2
│   │
│   ├── TotalTime(ms): 200.0
│   │
│   ├── 1
│   │   ├── detailedAPIName: 
│       ├── StartTimestamp: 1625150900123456789
│       ├── CostTime(ms): 200.0
│       └── Arguments: ((arg1, arg2, ...), {"kwarg1": val1, "kwarg2": val2, ...})
```
##### DataFrame Formatted callRecords
| API Name | Total Time (ms) | Call Number | Start Timestamp     | Cost Time (ms) | Arguments                                                  |
|----------|-----------------|-------------|---------------------|----------------|------------------------------------------------------------|
| API_1    | 150.0           | 1           | 1625150800123456789 | 50.0           | ((arg1, arg2, ...), {"kwarg1": val1, "kwarg2": val2, ...}) |
| API_1    | 150.0           | 2           | 1625150860123456789 | 100.0          |n((arg1, arg2, ...), {"kwarg1": val1, "kwarg2": val2, ...}) |
| API_2    | 200.0           | 1           | 1625150900123456789 | 200.0          | ((arg1, arg2, ...), {"kwarg1": val1, "kwarg2": val2, ...}) |

### apitools
#### getAPIName(get the Shortest callable name of an API)
```python
import torch
import torch.optim as optim
getAPIName(optim.Adam) # rather than Adam or torch.
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



#### 2024年7月10日
##### 14:10
今天又折腾了一上午，在关于getAttributes和getAPIName函数里对不同类型做逐一排查，同时也对所有需要debug的print处进行了格式化和缩进对齐，目前已经进入几乎能跑通的阶段了，然后刚刚出现了一个新问题：

此前我一直认为Python中的各种类都是可以任意添加属性的所谓“第一公民”，但之后遇到了`immutable type`，我就想着：“这些可能跟数字、字符串一样特殊吧，应该直接忽略就好了”就把他们作为TypeError直接捕获了。

没想到经过一个上午的调整后，我注意到add、randn、mm、matmul等算子也被标注为所谓`immutable type`，于是我的兴奋劲一扫而空，准备继续“任重而道远”了，看看今天能不能改出一版可能可用的吧。我可能需要回到基于`visiteList`的技术路线了。

不过，我终于算完善好了getAttributes和getAPIName两个工具性函数了，基本上已经没遇到过无法读出某对象下所有可供调用的API以及记录调用某API的准确调用方法了，即使作为一个单独的工具，我认为他也是合格的了。

##### 15:40
我总算把visitedModules和visitedClasses机制给实现好了，至于为什么不用

#### 2024年7月11日
##### 00:00
刚刚试着把两个自己设置的`raise NameError`报错注释掉了，竟然跑出了结果！！！！！！！！！！！！！！！！！！！

查看以后感觉并不如想象中的记录那么复杂，其实randn就是独立的可调用模块，没有那么多杂七杂八的子模块的，所以记录还是挺简洁的。不过啊，后续我又那自己写的简单MLP做了测试，结果报错依然出现在了`optimizer`处，我想自动微分这么精密的模块也确实是比较难搞吧。

##### 11:20
啊啊啊啊啊啊，在加入了对于父类对子方法引用存在的判断机制后，他竟然跑通了！！！！！！！！！！！！！！！！！

待会儿再进行进一步的测试看看我写的和他们之前写的有什么区别，今天起码会传一个版本吧。不过下午项目负责的老师也要来看看进度和简单交流，浅浅期待一下吧。

#### 2024年7月12日
##### 11:30
今天《卑鄙的我4》上映啦，有机会要去看一看，刚刚提交了第一版可以跑起来的版本，我就称之为**0.1.0beta**了！！！！！Yeah!!!

不过`Optimizer`的存在依旧会导致一些`callRecords`的记录问题，还有时间，可以继续修改，Yeah!!!

##### 16:30
不过今天没做出什么新花样，在尝试着做昨天团队布置的`testcase`的全盘测试，总体进展不大吧，就是上传和完善了昨天的成果。



#### 2024年7月15日
##### 10:00
实在是被家里的事情折腾了两天没更新进度了，我今天必须要把Torbencher的debugger倒腾出来了，这个TorchWrapper可能不会更新的那么快吧。XD


#### 2024年7月16日
###### 10:20
其实昨天那个import的结构和可用的debugger已经搞出来了，但就是莫名其妙那个`globals()[name] = cls`的映射出问题了，无法映射成功，没想到今天重新改了两下就可以实现了，本来昨天就应该有成果的。

#### 2024年7月17日
##### 17:20
今天还在继续折腾和完善`bencherdebugger`，现在感觉已经到了可以正式使用的阶段了，今天加入了两个新参数：
1. `num_epoches`：可以对所有用例进行多轮测试并保留所有报错的情况
2. `including_success`可以对测试结果是否保留测试通过的用例进行保存
而且还对`bencherdebugger`的代码进行了基于我的编程风格的重构，所以多花了些时间！！！！！

还有，刚刚我加入了Torbencher项目，可以直接修改啦！！！！！

不错不错，收获满满啊！！！！！！！
