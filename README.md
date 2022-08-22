
<p align="center">
  <a href="#"><img src="img/cqsat.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">  
  
**你的star是我的动力**  
**↓**  
<img src="https://img.shields.io/github/stars/yzyyz1387/cqsat.svg?style=social">  
# HAM助手  
  
  _✨ NoneBot2 业余无线电插件✨ _    
</div>

## 安装
### 直接安装
**暂拉取仓库放入机器人文件夹**
**然后安装本项目依赖**
```bash
pip install -r requirements.txt
```
### pip安装
先安装包
```bash
pip install nonebot-plugin-cqsat
```
再进入`bot.py` 
加入以下代码
```python
nonebot.load_plugin("cqsat")
```

### nb-cli安装  [ 推荐 ]
打开机器人项目文件夹（bot.py同级目录）
执行
```bash
nb plugin install nonebot-plugin-cqsat
```


## 说明
### 数据来源
- 目前只支持来自[http://www.cmse.gov.cn/gfgg/zgkjzgdcs/](http://www.cmse.gov.cn/gfgg/zgkjzgdcs/)的数据
- 还支持中国空间站，中国空间站TLE数据来自[中国载人航天官方](http://www.cmse.gov.cn/gfgg/zgkjzgdcs/)
### 使用时
**- 对于中国空间站，在使用时建议用`天宫`**
- 目前每次查询都是从在线获取数据
- 每分钟检测一次
  - 检测当前时间10分钟后，用户所定阅卫星的情况
  - 如果十分钟后入境，并且从入境到出境期间出现的最高仰角大于用户设定的最低仰角，将在群内@用户并提示
- 在执行输入操作时，输入`取消` 或者 `算了` 可取消当前操作
## 功能
- 追星
  - 提示示例：
<details>
  <summary> <h3>点击查看截图</h3></summary>  

[](img/readme/at_user.png)

</details>

## 指令
### 绑定QTH:  [ 群内、私聊 ]
- 绑定时发送：`绑定位置`  
- 更改位置时同样发送：`绑定位置`    
- 需要输入`经度 纬度 海拔`(以空格分隔)
  - 例如：  75.8656 39.3809 1330.0

<details>
  <summary> <h3>点击查看截图</h3></summary>  

[](img/readme/qth.gif)

</details>
  

### 订阅卫星：  [ 群内 ]
订阅时发送：`订阅卫星`  
期间会让用户输入：
- `卫星名称`:  大小写不敏感(多卫星用空格分隔)
  - 例如：SO-50 ISS ao-92  
- `最低仰角`:  输入数字（1, 90] （允许输入`xx度`或`xx°`）
  - 例如 10

<details>
  <summary> <h3>点击查看截图</h3></summary>  

[](img/readme/sat_sub.gif)

</details>

### 查询订阅的卫星 [ 群内 ]
- 发送  `查询订阅`
<details>
  <summary> <h3>点击查看截图</h3></summary>  

[](img/readme/refer_sub.gif)

</details>

### 查询支持的卫星列表 [ 群内、私聊 ]
- 发送`卫星列表`

<details>
  <summary> <h3>点击查看截图</h3></summary>  

[](img/readme/sat_list.gif)

</details>

### 查询某卫星在指定分钟后的状态 [ 群内、私聊 ]
- 发送  `查询卫星+卫星名+ +分钟数`  卫星名和分钟数用空格分隔
  - 例如 查询卫星SO-50 50  （查询so-50在50分钟后的状态）

<details>
  <summary> <h3>点击查看截图</h3></summary>  

[](img/readme/refer_sat_byTime.gif)

</details>

### 取消订阅卫星  [ 群内 ]
- 发送`取消订阅+卫星名称` 多颗卫星用空格分隔
  - 例如：取消订阅 SO-50 ISS ao-92
<details>
  <summary> <h3>点击查看截图</h3></summary>  

[](img/readme/sat_unsub.gif)

</details>

### 取消当前操作
- 在问答过程中发送`取消` 或者 `算了` 可取消当前操作

<details>
  <summary> <h3>点击查看截图</h3></summary>  

[](img/readme/cancel.gif)

</details>


## 日志
本插件`debug`级别日志输出到了机器`人文件夹/cqsat/log.log`中

## TODO
- [x] 追星
- [ ] 卫星状态、卫星列表加入图片支持
- [ ] 刷题
- [ ] 相关计算
- [ ] ....



## 参考资料

[PyEphem Home Page — PyEphem home page (rhodesmill.org)](https://rhodesmill.org/pyephem/)

刁宁辉,刘建强,孙从容,等. 基于SGP4模型的卫星轨道计算[J]. 遥感信息,2012,27(4):64-70. DOI:10.3969/j.issn.1000-3177.2012.04.011.
