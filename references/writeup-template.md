# RE Writeup Template

Copy the sections needed for the case. Replace every placeholder; keep unrun checks explicitly marked as not run.

````markdown
# <Case> Writeup

## 结果

- 状态：in_progress / blocked / verified / failed
- 成功条件与实际观察：
- 未验证内容：

## 目标与环境

- 样本相对路径、大小、SHA256：
- 架构、保护/壳、启动器与子进程：
- OS、工具版本、网络/时间假设：
- 基线 run ID、实验 run ID：

## 分析与证据

| Finding | Evidence IDs | 观察/推断 | 置信度与局限 |
| --- | --- | --- | --- |
| F-001 | E-001 | | |

| 模块 SHA256 | VA / RVA / 文件偏移（注明类型） | 运行时基址 | 用途 | Evidence ID |
| --- | --- | --- | --- | --- |
| | | | | |

## 方法

记录从输入到结果的实际路径，以及选择该方法的证据。
只保留会影响复现或避免重试的失败路径。

## 验证

- 证据完整性检查结果：
- 行为证明：输入、输出、功能操作；GUI 另记 PID/class/title/截图。
- 排除的伪阳性：登录页、启动页、空容器、无关子模块。
- 稳定性：实际时长/心跳周期，或不适用的原因。
- 干净基线复现：已运行的命令与结果，或未运行原因。

```powershell
# 填写实际复现命令
```

## 文件与恢复

- 脚本、日志、截图、dump 的相对链接及 Evidence IDs：
- 修改的资源、原始备份、恢复命令：
- 恢复是否执行及验证结果：
- 后续唯一明确动作或具体阻塞：
````
