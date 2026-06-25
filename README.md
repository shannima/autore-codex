# AutoRE Codex Skill

这是一个给 Codex 使用的通用 RE 题工作流 Skill，目标是把逆向题从“边猜边做”整理成可复用的协作流程。

它适合这些场景：

- CTF 逆向题、crackme、登录/授权绕过题
- PE/ELF/APK 初筛、脱壳、OEP、运行时 dump
- Frida、x64dbg、IDA 辅助分析
- 网络授权链、心跳、设备绑定、加密返回结构分析
- GUI 题中“进入真实主界面”的证明
- 最终 writeup、日志、截图、关键地址整理

## 核心原则

只读分析可以并行，动态调试必须单点控制。

也就是说：

- 静态分析、历史题对比、日志阅读、协议结构分析可以分给多个 subagent。
- 运行程序、attach Frida、x64dbg 调试、点击窗口、清理状态、杀进程、patch 文件，只能由一个执行者负责。
- 如果当前 Codex 环境不能使用 subagent，就由主控 Agent 按相同角色顺序执行。

## 推荐分工

```text
主控 Agent
  ├─ Recon：识别题型、文件、壳、架构、成功条件
  ├─ Static：静态分析字符串、函数、RVA、交叉引用
  ├─ Protocol：分析网络/授权/心跳/本地状态
  ├─ Dynamic：唯一动态执行者
  ├─ Patch：设计 hook、patch、fake response
  ├─ Evidence：验证截图、日志、稳定性
  └─ Writeup：整理最终报告
```

## 标准目录

每道题建议建立一个独立分析目录：

```text
<case>analysis/
  code/
  logs/
  screenshots/
  dumps/
  WRITEUP_<case>.md
```

可以使用内置脚本创建：

```powershell
python <codex_home>\skills\autore-codex\scripts\new_re_case.py `
  --case zidan `
  --root .\relink `
  --target .\relink\zidan\Relink.exe
```

脚本默认只会把目标文件记录为相对路径或文件名，避免把本机用户名、磁盘目录、临时目录等信息写进可上传的 Markdown。

## 使用方式

在 Codex 里可以这样说：

```text
Use $autore-codex 分析这个 RE 题，目标是进入真实主界面并写 writeup。
```

或者：

```text
按 autore-codex 分工做这个题。动态调试只能由主控执行，其他分析可以并行。
```

## 文件说明

- `SKILL.md`：Codex 实际读取和执行的 Skill 说明。
- `references/agent-roles.md`：各角色职责和边界。
- `references/case-checklist.md`：RE 题通用检查表。
- `references/writeup-template.md`：中文 writeup 模板。
- `scripts/new_re_case.py`：创建分析目录、基础 README 和空 writeup。

## 注意事项

这个 Skill 不保证自动解题，它提供的是稳定流程：

- 先定义成功条件。
- 再收集静态和动态证据。
- 然后选择 hook/patch/fake 数据方案。
- 最后用日志和截图证明结果。

对 GUI 主界面题尤其要注意：登录页、启动页、空窗口、单独子模块页面都不能直接算成功，必须证明进入了题目要求的真实主程序界面。
