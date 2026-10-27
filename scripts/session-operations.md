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
