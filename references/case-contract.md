# Case contract

## 文件与状态

沿用 `<case>analysis/`、`code/`、`logs/`、`screenshots/`、`dumps/` 和 `WRITEUP_<case>.md`；新增：

| 文件 | 用途 | 写入者 |
| --- | --- | --- |
| `case.json` | schema_version=1、case、created_at（UTC）、goal、status、target | 主控 |
| `STATE.md` | 当前阶段、已证实事实、失败假设、controller、下一动作 | 主控 |
| `evidence.json` | schema_version=1、records 数组 | 主控串行登记 |
| `runs/<run-id>.md` | 每轮命令、工具版本、PID、修改项、结果、恢复记录 | 动态控制者 |

`target` 为 null 或 `{path, size, sha256}`；默认只记相对路径/文件名。`status` 为 `in_progress`、`blocked`、`verified` 或 `failed`。初始模板不代表已完成分析。

初始化示例（从本仓库根目录执行，目标文件须已存在）：

```powershell
python scripts/new_re_case.py --case demo --root ./work --target ./samples/demo.exe --goal "打印正确输入对应的结果" --dry-run
python scripts/new_re_case.py --case demo --root ./work --target ./samples/demo.exe --goal "打印正确输入对应的结果"
```

`--force` 只补缺失文件，不重置状态、不覆盖报告。携带 `--target` 复用时必须与原身份一致；目标或目标描述变化需显式维护记录，二进制变更建议新建案件。旧版本目录可用 `--force` 补模板，但迁移时需人工核对原 README 中的目标与新 `case.json`，不能把补模板称为重新验证。

## 证据登记与检查

先保存真实输出到案件目录，再登记；下例假设 `logs/run-001.txt` 已存在：

```powershell
python scripts/case_evidence.py record ./work/demoanalysis --id E-001 --path logs/run-001.txt --run-id run-001 --command "实际执行的命令" --note "观察到的结果及其局限"
python scripts/case_evidence.py check ./work/demoanalysis --strict --format json
```

每条记录含 `id`（E- 加至少三位数字）、`path`（案件内 POSIX 相对路径）、`sha256`、`run_id`、`command`、`note`、`created_at`。命令只保存为文本，工具不会执行它。手工截图可将 command 写为 `manual capture`，并在 note 写出采集方法、PID、时间及未捕获的信息。写入后不要修改原证据；新实验另存新文件、新 ID。

检查会拒绝重复 ID、缺失字段、无效路径、文件不存在、哈希不符；检查 `verified` 状态有目标、目标身份和证据。普通模式允许未完成案件带警告通过；`--strict` 将警告也视为失败。退出码 0 表示检查通过，1 表示证据检查失败；初始化参数或文件错误为 2。

哈希只证明当前文件与登记时一致，不能证明内容真实、因果成立或目标达成。工具不重新定位/读取原始目标，也不解析报告的语义；交付时仍需人工核对样本哈希、Finding→Evidence 引用、run ID、截图、时间顺序与复现结果。保存在同一目录的哈希不是防篡改签名。

元数据采用临时文件替换，避免写出半截 JSON，但没有多写者锁；必须由主控串行调用。案件目录应为本地受控工作目录，不与其他进程同时修改链接或路径。

## 每轮运行与恢复

`runs/<run-id>.md` 至少记录：

- 目标/模块哈希、工具和系统版本、实际命令、PID/子进程、开始时间。
- 基线或实验假设、输入、修改的文件/内存/本地状态；原始备份及其哈希。
- 预期结果、实际结果、Evidence IDs；失败也保留日志。
- 具体恢复步骤以及恢复是否执行、验证；不要把“有备份”写成“已恢复”。

写补丁前确认作用于工作副本，并比较期望原始字节。恢复仅针对本轮已识别的资源；不得按模糊进程名批量结束程序或删除未知状态目录。

## 续接和交付

续接先读身份与状态，确认活跃调试会话归属，再继承证据引用。没有新证据的失败路径只记一次原因与下一假设。环境缺失时写出具体缺失工具/样本/权限和可执行替代步骤。

交付前完成与任务匹配的三项检查：

1. **文件检查**：严格证据校验通过；待完善案件可交付阶段性报告，但明确状态。
2. **行为检查**：真实程序满足 goal，排除伪阳性；需要稳定性的任务记录实际观察时长/周期。
3. **复现检查**：从已知基线复跑，或明确无法复跑的原因；核实恢复步骤与修改范围。

这些是本项目的交付检查，不等同于任何参考仓库的模型评测成绩。
