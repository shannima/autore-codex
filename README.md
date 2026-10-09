# AutoRE Codex Skill

面向 Codex 的轻量逆向分析工作流：从样本识别、静态/动态分析，到结果证明和可复现 writeup。适合 CTF、crackme、PE/ELF/APK 初筛、运行时重建与 GUI 状态验证。

**静态分析可以并行，动态操作只有一个控制者；结论必须能追溯到实际证据。** 无 subagent 时按同样的职责顺序执行。Skill 不绑定模型版本，不保证自动解题。

## 本次完善

- 按需读取工具选择、角色分工和案件契约，保持入口简短。
- 用 `STATE.md` 续接任务，保存已证实事实、失败路径和下一动作。
- `case.json` 固定目标身份；`evidence.json` 记录证据文件、命令、run ID 和 SHA256。
- 初始化支持 `--dry-run`；`--force` 只补缺失模板，拒绝混入不同目标。
- 增加标准库证据 CLI、回归测试和 Windows/Linux CI。

设计依据和三个参考仓库的取舍见 [综合分析](references/upstream-analysis.md)。

## 使用

将本仓库作为 `autore-codex` Skill 放入客户端配置的 skills 目录；已有安装先备份再更新，不覆盖个人修改。显式调用示例：

```text
Use $autore-codex 分析这个本地 RE 题，先确定成功条件，再保存证据并写 writeup。
```

```text
使用 $autore-codex 继续已有案件；先读 case.json 和 STATE.md，再进行下一步。
```

本仓库提供 Skill 文件及案件工具，不改写全局 `AGENTS.md`、模型配置、provider 或凭据。只有实际分析需要时才使用已安装的 IDA、Ghidra、Frida 等工具。

## 案件工具

需要 Python 3.8+，无第三方 Python 依赖。以下命令在仓库根目录运行；`--target` 必须指向存在的文件，相对路径基于当前工作目录，而非 `--root`。

```powershell
# 先预览（不创建目录）
python scripts/new_re_case.py --case demo --root ./work --target ./samples/demo.exe --goal "进入真实主界面并完成目标操作" --dry-run

# 创建案件
python scripts/new_re_case.py --case demo --root ./work --target ./samples/demo.exe --goal "进入真实主界面并完成目标操作"

# 续接时只补缺失模板
python scripts/new_re_case.py --case demo --root ./work --force
```

```text
demoanalysis/
  case.json             # 目标身份、目标描述与状态
  STATE.md              # 续接记录
  evidence.json         # 证据索引
  README.md
  code/                 # 分析脚本
  logs/                 # 原始日志
  screenshots/          # 证明截图
  dumps/                # 运行时镜像
  runs/                 # 每轮环境、结果、恢复记录
  WRITEUP_demo.md
```

先保存真实日志，再登记（示例文件不会自动生成）：

```powershell
python scripts/case_evidence.py record ./work/demoanalysis --id E-001 --path logs/run-001.txt --run-id run-001 --command "实际执行命令" --note "实际观察与局限"
python scripts/case_evidence.py check ./work/demoanalysis --strict --format json
```

`PASS` 表示元数据和登记文件的完整性通过，**不代表成功解题**。仍需核对目标状态、功能行为和复现结果。默认不写入目标绝对路径；命令和备注由操作者提供，分享前检查其中的本机路径、令牌和个人信息。案件数据默认放在已忽略的 `work/`，不随 Skill 上传。

## 参考文档

| 文档 | 何时读取 |
| --- | --- |
| [SKILL.md](SKILL.md) | 实际技能入口 |
| [案件契约](references/case-contract.md) | 初始化、证据记录、续接和交付 |
| [工具选择](references/tool-routing.md) | 判断下一步工具或工具缺失 |
| [角色职责](references/agent-roles.md) | 多人/多 agent 协作或控制权交接 |
| [检查表](references/case-checklist.md) | 交付前核查 |
| [Writeup 模板](references/writeup-template.md) | 整理可复现报告 |
| [行为评估场景](tests/behavioral-cases.md) | 手工评估 Skill 决策质量 |

## 验证

```powershell
python -m unittest discover -s tests -v
```

自动测试覆盖初始化复用、无效目标、路径边界、证据篡改与 CLI 返回状态。GitHub Actions 配置 Windows/Linux、Python 3.8/3.12；以实际运行结果为准。行为场景需另行人工评估，不计入脚本单元测试通过率。
