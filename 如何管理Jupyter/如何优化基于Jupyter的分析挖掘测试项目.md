# 如何优化基于Jupyter的分析/挖掘测试项目

对于一个有软件工程项目基础的程序员而言，我们这群来源「可疑」的Data Scientist最被人诟病的就是期代码质量堪忧到让人崩溃的程度。本篇文章将介绍自己在以`python`/`Jupyter Notebook`为基础的分析/挖掘项目时是如何优化代码使其具有更大的可读性（执行效率不是本文的主要目的）。

## Python语法级别的优化

### 合适的style

当然，这个层面的优化是最简单的，大家熟悉的`PEP`风格和`GOOGLE`风格都是不错的实践。参加下面两个文档:

* [PEP代码风格](https://www.python.org/dev/peps/pep-0008/)
* [GOOGLE代码风格](https://github.com/google/styleguide/blob/gh-pages/pyguide.md)

### 值得一试的命名方案

多年经（踩）验（坑）摸索出一套比较适合的变量命名方案，基本的方法是

```
[具象词](_[操作])(_[介词短语])_[数据结构]
```

**具象词**是描述数据的具体用处的词语，例如一个班级的男生的成绩，可以用`boy_score`来表述。

**操作**则是概括了对数据做过什么处理，如果是个人团队可以维护一个简单的缩略词词库。比如，我们要描述一个班级的成绩做过去空值的处理，可以用`drop_null`或者`rm_na`来表示。在这种情况下，我们可以对上面的对象完整描述成`boy_score_rm_na`。

**介词短语**其实也是操作的一部分，往往以`in`/`over`/`top`（不严谨地归在此类）/`group by`等。比如，我们这里要描述一个班级的学生按性别取前10的成绩并做了去重处理，可以写成`score_unique_groupbysex_top10`，如果长度过长，维护一个简写的映射表当然也是不错的（牺牲部分可读性）。

**数据结构**则是描述数据是存储在什么数据结构中的，常见的比如`list`，`pandas.DataFrame`、`dict`等，在上面的例子里，我们储存在`pandas.DataFrame`则可以写成`score_unique_groupbysex_top10_df`。

而**操作**和**介词短语**在很多场合下可以不写。当然在更加抽象地机器学习训练中时，可以以`test_df`、`train_df`这种抽象描述是更适合的方案。

## Jupyter级别的优化

### 线性执行

这点是容易忽视的一个问题，任何`Jupyter`里面的cell一定要保证，具体的cell中的代码是自上而下执行的。这在工作中，可能由于反复调试，导致在编辑cell的过程中不是线性操作。保证notebook可以线性执行的原因，一部分是方便其他阅读人可以正常执行整个notebook；另一部分，也是为了增加可读性。

```markdown
<!-- 可接受的例子 -->

​```cell 1
import pandas as pd
​```

​```cell 2
df = pd.read_csv('train.csv')
​```

​```cell 3
def sum_ab(row):
	return row['a'] + row['b']
​```

​```cell 4
df.apply(sum_ab, axis=1)
​```
```

```markdown
<!-- 不可接受的例子，不能正常运行 -->

​```cell 1
import pandas as pd
​```

​```cell 2
df = pd.read_csv('train.csv')
​```

​```cell 3
df.apply(sum_ab, axis=1)
​```

​```cell 4
def sum_ab(row):
	return row['a'] + row['b']
​```
```

### 载入模块和读入数据放在开头

在具体分析中，载入模块和数据是非常常见的工作，而放置在notebook开始容易帮助阅读者注意，需要的依赖以及数据。如果零散地出现在notebook任何地方，这样就容易造成困难的路径依赖检查、模块重命名方式和模块依赖检查。

如果有些模块并不常用，但在notebook引用到了，建议在载入模块前的cell中加入一个cell用来安装依赖。`jupyter`可以用`!`来实现临时调用系统的命令行，这个可以很好地利用在这个场景中。

此外，所有数据和自写模块使用相对链接的方式导入是不错的选择。因为，后期可能别人会通过`git`的方法获取你的代码，相对链接可以允许我们不修改链接也能使用`git`项目中的模块和数据。

```markdown
​```cell 1
!pip install scikit-learn
​```

​```cell 2
import panda as pd
from sklearn import metrics
import sys

## 自编模块
sys.path.append('../')
from my_module import my_func
​```

​```cell 3
df = pd.read_csv('./train.csv')
​```
```

### 一个Cell一个功能

我们在具体撰写Jupyter时，无法避免，会反复尝试，并且测试中间输出的结果。因此，很多同行的cell代码往往会呈现以下状态。

```markdown
​```cell 1
df_1 = df.sum(axis = 1)
​```

​```cell 2
df_2 = df_1.fill_na(0)
​```

​```cell 3
ggplot(df_2, aes(x = 'x', y = 'y')) + geom_point()
​```
```

这样的做法无可厚非，且并没有错误，但是，这样的缺点是，读者可能需要run三个cells才能得出最终的结果，而中间的处理过程，在阅读报告中，往往是无关紧要的甚至会影响到可读性，具体查看中间步骤只有复现和纠错时才是必要的。因此，我们要保持一个原则，就是一个Cell理应要承担一个功能需求的要求。具体优化如下：

```
​```cell 1
df_1 = df.sum(axis = 1)
df_2 = df_1.fill_na(0)

## 绘图
ggplot(df_2, aes(x = 'x', y = 'y')) + geom_point()
​```
```

但很多朋友可能会遇到，过程过于复杂，导致一个cell看起来非常的冗余，或者处理过程异常漫长，需要一些中间表的情况，后面的建议中，我会提到如何改善这两个问题。

### 数据（包括中间结果）与运算分离

回到刚才的问题，很多时候，我们会遇到一个中间过程的运行时间过长，如何改变这种状况呢，比如上个例子，我们发现`fillna`的时间很长，如果放在一个cell中，读者在自己重新运行时或者自己测试时就会非常耗时。一个具体的解决方案就是，写出临时结果，并且在自己编辑过程中，维持**小cell**，只在最后呈递时做处理。比如上面的任务，我会如此工作。

```markdown
​```cell 1
df_1 = df.sum(axis = 1)
​```

​```cell 2
df_2 = df_1.fill_na(0)
df_2.to_pickle('../temp/df_2.pickle')
​```

​```cell 3
ggplot(df_2, aes(x = 'x', y = 'y')) + geom_point()
​```
```

最后呈递notebook时改成如下样子

```
​```cell 1
##~~~~ 中间处理 ~~~~##
# df_1 = df.sum(axis = 1)
# df_2 = df_1.fill_na(0)
# df_2.to_pickle('../temp/df_2.pickle')
##~~~~ 中间处理 ~~~~##

df_2 = pd.read_pickle('../temp/df_2.pickle')

## 绘图
ggplot(df_2, aes(x = 'x', y = 'y')) + geom_point()
​```
```

这样做的另外个好处可以实现，数据在notebook之间的交互，我们会在之后提到具体场景。

###抽象以及可复用分离到Notebook外部

我们在撰写notebook时遇到的另一个问题，很多具体地清洗或者特征工程时的方法，过于隆长，而这些方法，可能在别的地方也会复用，此时写在一个cell里就非常不好看，例如下面一个方法。

```markdown
​```cell 1
def func1(x):
	"""add 1
	"""
	return x + 1

def func2(x):
	temp = list(map(func1, x))
	temp.sorted()
	return temp[0] + temp[-1]

df.a.apply(func2, axis)
​```
```

这种情况的解决方案，是独立于notebook之外维护一个文件夹专门存放notebook中会用到的代码。例如，使用如下结构存放模块，具体使用时再载入。

```
--- my_module
  |__ __init__.py
  |__ a.py
___ notebook
  |__ test.ipynb
```

注意使用`sys`模块添加环境来载入模块。

```python
## import cell
import pandas as pd
import sys

sys.path.append('../')
from my_module import *
```

但这种方案，存在一个问题——我们会经常改动模块的内容，特别是在测试时，这时候需要能重载模块，这个时候我们需要反复重载模块，`python`在这方面的原生支持并不友善，甚至重开内核运行所有都比手写这个重载代码快。这时候我们需要一个`ipython`的`magic extension`——`autoreload`，具体的方法参考[这个问答](https://stackoverflow.com/questions/1907993/autoreload-of-modules-in-ipython)。

我们只需要在载入模块的开头写上如下行，这样我们每当修改我们自己编写的module时就会重载模块，实现更新。

```python
%load_ext autoreload
%autoreload 2

import pandas as pd
import sys

sys.path.append('../')
from my_module import *
```

而模块分离最终的好处是，我们最后可以容易的把这些模块最后移植到生产环境的项目中。

## 项目级别的优化

### 一个notebook解决一个问题

为了让项目更加具有可读性，对任务做一个分解是不错的方案，要实现**一个notebook只执行一个问题**。具体，我在工作中会以下列方案来做一个jupyter的notebook分类。其中`0. introduction and contents.ipynb`是必须的，里面要介绍该项目中其他notebook的任务，并提供索引。这种方案，就可以提高一个分析/挖掘项目的可读性。

```markdown
- 0. introduction and contents.ipynb
- eda.1 EDA问题一.ipynb
- eda.2 EDA问题二.ipynb
- eda. ...
- 1.1 方案一+特征工程.ipynb
- 1.2 方案一训练和结果.ipynb
- 2.1 方案二+特征工程.ipynb
- 2.2 方案二训练和结果.ipynb
- 3.1 方案三+特征工程.ipynb
- 3.2 方案三训练和结果.ipynb
- ...
- final.1 结论.ipynb
```

### 对文件进行必要的整理

一个分析、挖掘的项目，经常包括但不限于**数据源**、**中间文件**、**临时文件**、**最终报告**等内容，因此一个好的整理项目文件的习惯是必要的。我在工作中，具体采用下面这个例子来维护整个分析/挖掘项目。当然，初始化这些文件夹是一个非常麻烦的，因此，这里分享一个[初始化脚本](https://github.com/threecifanggen/lambda-and-tau/blob/master/%E5%A6%82%E4%BD%95%E7%AE%A1%E7%90%86Jupyter/tools/initial_jupyter_project.py)（支持python版本3.6+），大家可以根据自己整理习惯稍作修改。

```
-- 项目根目录
  |__ SQL：存储需要用的SQL
  |__ notebook: 存放notebook的地方
     |__ 0. introduction and contents.ipynb
     |__ eda.1 EDA问题一.ipynb
     |__ eda.2 EDA问题二.ipynb
     |__ eda. ...
     |__ 1.1 方案一+特征工程.ipynb
     |__ 1.2 方案一训练和结果.ipynb
     |__ 2.1 方案二+特征工程.ipynb
     |__ 2.2 方案二训练和结果.ipynb
     |__ 3.1 方案三+特征工程.ipynb
     |__ 3.2 方案三训练和结果.ipynb
     |__ ...
     |__ final.1 结论.ipynb
  |__ src: 撰写报告或者文档时需要引用的文件
  |__ data: 存放原始数据
     |__ csv: csv文件
     	|__ train.csv
     	|__ ...
     |__ ...
  |__ temp: 存放中间数据
  |__ output: 最后报告需要的综合分析结果
     |__ *.pptx
     |__ *.pdf
     |__ src
     	|__ example.png
     	|__ ...
  |__ temp_module: 自己写的notebook需要引用的模块
```

## 结语

优化一个Jupyter代码并非不可能，只是看是否具有相关的习惯，增加可读性对自己以及团队的工作和开源社区的声望都会有利，希望上面的建议对大家有所帮助。