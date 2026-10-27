# 本轮实施命令与临时配置记录（脱敏）

1. 通过 SSH Relay 5.4 的 ssh_list_servers 核验真实主机；ssh_execute 只读列出 E 盘、工具路径及 py -0p；无已安装 Python。
2. 在 E:\xxm 下新建 OmniDispatch/dev、backups、release，保存 DESIGN.md。连接令牌不属于源码，未保存。
3. 源码在隔离云工作目录编写，Python 3.12 虚拟环境安装 requirements.lock.txt；pytest -q；前端 npm ci、npm run build。
4. 使用官方 python.org 目录核验 CPython 3.14.10 Windows embeddable 资产，下载 runtime ZIP；pip download --only-binary=:all: --platform win_amd64 --python-version 314 --implementation cp --abi cp314 安装同版本运行依赖。Windows pytest 另外需要 colorama 0.4.6。
5. build-portable.py 从固定 wheels 构建独立运行环境，保留第三方许可证；release 不包含 pytest。dev 验证工具只用于 Windows 实机测试，不计作自有源码。
6. 使用独立 postgres:17.6 容器、omni_test 数据库和私密随机密码执行同一组并发/幂等/租约测试。测试配置只含临时容器凭据，不交付。测试结束删除该测试容器。
7. Playwright 使用本机 Chromium 测试九个页面、登录、账号创建、无效任务拒绝与窄屏导航。浏览器的临时测试状态独立于用户数据，未进入部署包。
8. Windows 安装脚本在首次部署前压缩备份现有 dev；展开工程包；使用独立 Python 执行测试；install-windows.ps1 创建专用普通账号、限制 state ACL、注册 OmniDispatch-Hub-Agent 启动任务。随机服务密码不打印、不提交。Hub 仅监听 127.0.0.1:8791，管理锁端口 8792。
9. 可选公共测试入口由现有 cloudflared 的 quick tunnel 提供；只由本工程 supervisor 启动和恢复自己的子进程。隧道临时域名随重建变化，稳定生产域名需另行配置 Caddy 或命名隧道。
10. 平台凭证、主密钥、初始密码、Agent token、临时私密下载 URL 一律留在仓库外或远端 state，不上传。

追加：Windows 计划任务初始返回 0xc000015b，实际为专用账号缺少 SeBatchLogonRight。使用 grant-batch-logon.ps1 的 LSA API 仅向 OmniDispatchRun 授予该权利，未加入管理员组。数字 SID 的 icacls 授权使用 *SID 形式，所有关键 ACL 命令检查退出码。TaskScheduler Operational 日志用于定位错误，相关诊断脚本保存在 scripts/diagnostics。

GitHub raw 域名在远端下载超时；最终使用 GitHub API 提供的私有 codeload 归档授权地址成功下载。曾准备的无凭据 Filebin 备用生成包已删除；最终传输使用私有 GitHub。临时授权 URL 未写入源码。未成功上传的空 GitHub draft release 已删除；正式代码及运行环境归档保存在项目分支。

最终补充：停止初版父任务后确认曾残留本应用子进程。stop-windows.ps1 按专用账号及路径范围清理；WindowsJob 使用 kill-on-close 管理新子进程。Windows 原生测试通过后再启动更新后台。临时公网域名的更新由监督进程自动写入 PUBLIC-URL.txt。Cloudflare 云端 403 与远端当前域名 200 分别记录，不将本机 SSH 浏览器验证称为所有地区公网验收。
