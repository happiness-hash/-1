# 四川省计算机设计大赛成绩通知监控

这个脚本会监控四川省大学生计算机设计大赛官网的 `大赛公告` 栏目：

`https://www.scjsjds.cn/web/guest/ssgg`

当检测到新的公告，并且标题命中成绩相关关键词时，Windows 会弹出提示框：

`成绩出来了`

## 触发规则

脚本不会监控首页，而是直接监控 `大赛公告` 列表页。

只有同时满足下面两个条件才会弹窗：

1. 最新公告和上一次检查记录相比发生了变化
2. 最新公告标题包含以下任一关键词

- `评审结果`
- `结果名单`
- `获奖`
- `获奖名单`
- `获奖公示`
- `获奖公告`
- `名单公示`
- `名单公告`

这样可以避免把秩序册、预通知、补充通知之类的公告误判成成绩发布。

## 文件说明

- `monitor_scjsjds.py`：主脚本
- `monitor_state.json`：脚本首次运行后自动生成，用来记录上一次看到的最新公告
- `requirements.txt`：依赖文件

## 安装依赖

```bash
pip install -r requirements.txt
```

如果你已经装过 `beautifulsoup4`，可以跳过这一步。

## 使用方法

先进入项目目录，然后执行：

```bash
python monitor_scjsjds.py
```

脚本会每 5 分钟检查一次官网公告。

首次运行时：

- 不会弹窗
- 只会把当前最新公告记录到 `monitor_state.json`

后续运行时：

- 如果官网最新公告没有变化，终端会输出 `[无变化]`
- 如果出现新公告但不是成绩类通知，终端会输出 `[未触发弹窗]`
- 如果出现新的成绩类通知，会弹出窗口 `成绩出来了`

## 只检查一次

如果你想先测试当前最新公告是什么，可以运行：

```bash
python monitor_scjsjds.py --once
```

## 开机自动运行

你可以把下面命令做成 `.bat` 文件，或放进 Windows 任务计划程序：

```bat
cd /d c:\D\codeWorkplace\pythonworkplace\pythonworkplace\爬虫检测出成绩
python monitor_scjsjds.py
```

更稳妥的方式是用“任务计划程序”在开机后或登录后启动。

## 推送到 GitHub

当前目录如果还不是 Git 仓库，可以执行：

```bash
git init
git add .
git commit -m "Add Sichuan competition announcement monitor"
```

然后关联你的 GitHub 仓库并推送：

```bash
git remote add origin <你的仓库地址>
git branch -M main
git push -u origin main
```

如果你把仓库地址发给我，我可以继续帮你把它直接推上去。
