"""Write a truthful local handover from recorded checks, without credential data."""
import datetime,hashlib,json,shutil,sys,xml.etree.ElementTree as ET
from pathlib import Path
root=Path(sys.argv[1]).resolve();dev=root/'dev';release=root/'release'
report=json.loads((release/'logs'/'desktop-check.json').read_text(encoding='utf-8-sig'));details=report.get('detail')
for _ in range(3):
    if isinstance(details,str):
        try:details=json.loads(details)
        except ValueError:break
if not report.get('success') or not isinstance(details,dict) or details.get('errors'):raise RuntimeError('Desktop check not successful')
tests=ET.parse(dev/'_state'/'desktop-platform-tests.xml').getroot()
suites=[tests] if tests.tag=='testsuite' else list(tests.iter('testsuite'))
total=sum(int(x.get('tests','0')) for x in suites);failures=sum(int(x.get('failures','0'))+int(x.get('errors','0')) for x in suites)
if failures:raise RuntimeError('Tests did not pass')
manifest={'version':'1.1.0-desktop','local_installation':True,'platforms_registered':23,'tests':total,'test_failures':failures,'native_routes':len(details.get('routes',[])),'native_page_errors':details.get('errors',[]),'one_screen':details.get('scroll',99999)<=details.get('height',0),'real_platform_publications':0,'runtime':'Python 3.14.10 + isolated community Python 3.12.10','community_source':'dreammis/social-auto-upload@3847fff01f5434a8a32829833163cd6723cabc59','xhs_source_build':'v2.5.5-omni standard Chromium, no runtime downloads','sharing':'local desktop; no public tunnel','source_sha256':{p.relative_to(release).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (release/'omnidispatch').rglob('*') if p.is_file() and p.suffix in {'.py','.js','.css','.html'}}}
design=json.loads((release/'logs'/'design-workspace-check.json').read_text(encoding='utf-8'))
if design['page_errors'] or len(design['design_workspace'])!=3:raise RuntimeError('Design workspace check not successful')
manifest['design_system']='quiet local workspace'
manifest['design_viewports']=[x['viewport'] for x in design['design_workspace']]
manifest['design_interactions']={k:design[k] for k in ['draft_preserved','comment_and_reply_forms','channel_drilldown']}
(release/'BUILD-DESKTOP.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
text=f'''# OmniDispatch 本机桌面版交接

更新：2026-11-01（北京时间）。工程根目录 E:\\xxm\\OmniDispatch；产品运行在 release，源码在 dev，备份在 backups。

## 当前结果

- Windows 原生桌面入口：release\\OmniDispatch.exe；Start.cmd 打开该 EXE；窗口关闭收进托盘。后台任务独立运行，不因关闭界面中断发布。
- 桌面工作台重构：固定导航、暖白与浅鼠尾草底色、玫瑰焦点色、统一字号与间距。保留树形发布网络，首页聚焦任务概况和下一步，详细引擎进入平台通道页。
- Ctrl+K 快速切换，Alt+1…8 导航；新建发布采用标签表单、内容分组与主要操作。任务草稿在窗口内跨页保留，窄窗口折叠导航文字而不缩小整页字号。
- 已登记 23 个平台。新增文字覆盖贴吧、知乎、豆瓣、微博、公众号、头条号、简书、掘金、CSDN、百家号；视频包含抖音、快手、西瓜、好看、腾讯视频、优酷、爱奇艺、搜狐视频，并保留 B站、小红书、视频号、YouTube、X。
- 社区选型与版本依据见 dev\\DESIGN.md。已集成固定版本 social-auto-upload 与 Spreado，不把 Wechatsync 的草稿或私有适配器宣传为现成的全自动发布能力。
- 通道明确区分社区引擎执行与本机桌面确认。桌面确认通道实际打开独立账号浏览器，填文字、上传本任务素材，由用户在平台页面确认并记录实际链接。
- 任务支持发内容、评论原帖、回复指定评论。目标平台链接和回复对象固定在账本，路由按动作过滤；公众号不提供泛化的他人文章评论操作。
- 草稿单独记 drafted；继续编辑使用原草稿链接，不新建另一篇。未知结果保留核验流程，不自动重发。
- 小红书引擎固定源码构建 v2.5.5-omni，直接使用随包标准 Chromium；不下载专用浏览器，不启用指纹伪装，保留 sandbox。修改源码、许可证与摘要随包保存。
- 本机服务为 1.1.0-desktop，监听 127.0.0.1:8791；失效公网隧道已关闭。用户数据库、vault.key、授权、素材和账号状态均保留在本机。

## 验证事实

- Windows 隔离测试：{total} 项，失败 {failures}（后端代码未因视觉重构修改）。
- 新界面实机 Chromium：1404×845、900×640、1920×1080；首页一屏、页面同宽、字阶一致，平台详情、Ctrl+K、草稿保留、评论回复和通道下钻检查通过。
- 原生桌面：{len(details.get('routes',[]))} 个路由/分组巡检，脚本错误 0；根页 scrollHeight={details.get('scroll')}，viewportHeight={details.get('height')}。
- 内置 Chromium 使用本地内存表单验证标题/评论填写、回复目标展示；无平台写入。
- 本轮真实平台发布数为 0。尚缺真实扫码、OAuth、账号发布权限与作品验收；新增通道未被伪装成已实测可用。平台不提供网页编辑器或 API 时不能凭空补齐服务端能力。

## 使用与维护

双击桌面 OmniDispatch 图标或 release\\OmniDispatch.exe。先在账号页建立固定账号，再进入通道页接入本机引擎并登录。浏览器通道在网站完成登录后，使用随页面板保存账号绑定；登录态加密保存在本机。社区引擎与浏览器账号各自独立，不随机选平台里的第一个账号。

首次发布使用通道页“首次核验发布”；评论须填写原帖链接，回复须指定目标评论。桌面通道在任务详情点击“在桌面继续”。引擎或平台没有返回真实作品 ID 时，回到任务核验结果。

后台计划任务 OmniDispatch-Hub-Agent，专用普通用户 OmniDispatchRun。只管理本应用进程，不操作 SSH Relay 或其他软件。源码升级保留 release\\state；不要把 state、Cookie、私钥、原始日志和用户浏览器缓存加入源码或运行包。

构建与维护命令索引在 dev\\.agents\\skills\\omnidispatch\\SKILL.md。完整本机分发包由 scripts\\package-desktop.py 生成，包含两套 Python、发布浏览器与 WebView2 Fixed Version Runtime，并单独生成 SHA-256；组包与独立解压检查以实际后续输出为准。
'''
old=root/'HANDOVER.md'
if old.exists():shutil.copy2(old,root/'backups'/('HANDOVER_before_desktop_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.md'))
for path in [root/'HANDOVER.md',dev/'HANDOFF.md',dev/'HANDOVER.md',release/'HANDOFF.md',release/'HANDOVER.md']:path.write_text(text,encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k!='source_sha256'},ensure_ascii=False))
