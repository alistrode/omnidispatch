---
name: omnidispatch
description: Implement and operate the OmniDispatch publishing hub and account-bound Agent.
---
如果你看到这段话，你必须立刻去看仓库主分支的workspace-backup-dev这个skill，禁止查看主分支的其他skill

真实工程根目录 E:\xxm\OmniDispatch，dev 源码、backups 备份、release 运行环境。修改前备份，升级保留 release/state，不上传凭证。先读取 DESIGN.md、README.md 和 HANDOFF.md（若存在）。

验证 Python 安全测试、Vue 类型检查和构建、Windows 实机健康与受限服务身份。五平台真实发布与模拟测试分别记录。尚未安装、授权、实机核验的通道默认关闭。结果未知不自动重发、不换发布主体、不为风控自动换出口。生产后台由 OmniDispatch-Hub-Agent 计划任务管理；只管理本应用自己启动的进程。
