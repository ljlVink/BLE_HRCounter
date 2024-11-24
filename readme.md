# heartlistener BLE for HRCounter

基于通用手环BLE心率广播协议，对指定mac地址进行连接并抓取实时心率，并同步到BeatSaber [HRCounter](https://github.com/qe201020335/HRCounter),内置obs overlay

## 使用方法

### 安装依赖

```
pip install -r requirements.txt
```

### 手环端

在手环记下手环的mac地址，开启心率广播

### 电脑端

在项目中的`config_example.yaml`的`bleAddr`后填入手环mac地址，大写

本项目的默认端口号为`5652`，在配置中可按需更改。

打开beatsaber的游戏目录，在`/UserData/HRCounter.json`中修改
```
"DataSource": "WebRequest",

"FeedLink": "http://localhost:5652/",
```

此处5652为程序设置的端口号。

运行`heart.py`并启动游戏:

```
python heart.py
```
### 在obs添加overlay

浏览器：http://127.0.0.1:5652/hr


## Q&A

1.搜不到手环mac地址，提示`Target device not found. Retrying in 5 seconds`

将config.yaml的`ScanMode`字段调成true，启动heart.py启动搜索模式。在搜索模式下搜到的手环名称对应mac地址即为广播的mac地址(华为手环)

2.提示`Device does not support heart rate service`:

你的手环不支持BLE原生心率广播

(0000180d-0000-1000-8000-00805f9b34fb:00002a37-0000-1000-8000-00805f9b34fb)
