from .platform_specs import PLATFORM_SPECS
PLATFORMS={'bilibili':'B站','xiaohongshu':'小红书','tencent':'视频号','youtube':'YouTube','x':'X'}
PLATFORMS.update({key:value['label'] for key,value in PLATFORM_SPECS.items()})
SOURCES={
'sau':'dreammis/social-auto-upload','xhsmcp':'xpzouying/xiaohongshu-mcp',
'biliup':'biliup/biliup','ytuploader':'porjo/youtubeuploader','spreado':'BadKid90s/Spreado',
'postiz':'gitroomhq/postiz-app','mixpost':'inovector/mixpost','matrixmedia':'hanliang97/MatrixMedia',
'postbot':'gitcoffee-os/postbot','resin':'Resinat/Resin','tweepy':'tweepy/tweepy','patchright':'Kaliiiiiiiiii-Vinyzu/patchright'}
COVERAGE={'sau':['bilibili','xiaohongshu','tencent','youtube'],'xhsmcp':['xiaohongshu'],'biliup':['bilibili'],'ytuploader':['youtube'],'spreado':['xiaohongshu','tencent'],'postiz':['x','youtube'],'mixpost':['x','youtube'],'matrixmedia':['bilibili','xiaohongshu','tencent'],'postbot':['bilibili','xiaohongshu','tencent'],'xapi':['x'],'xbrowser':['x']}
COVERAGE['desktopweb']=list(PLATFORM_SPECS)
COVERAGE['spreado']+=['douyin','kuaishou']
COVERAGE['sau']+=['douyin','kuaishou','baijiahao','weibo','zhihu']
IMPLEMENTED={'desktopweb','sau','xhsmcp','biliup','ytuploader','xapi','matrixmedia','spreado'}
def seed(s):
    from .db import Channel
    for engine,platforms in COVERAGE.items():
        for platform in platforms:
            key=f'{engine}-{platform}'
            if engine=='desktopweb':
                if not s.get(Channel,key):
                    p=PLATFORM_SPECS[platform]
                    s.add(Channel(id=key,engine=engine,platform=platform,priority=20,capabilities={'media':list(dict.fromkeys(p['media']+(['text'] if 'comment' in p['actions'] else []))),'actions':p['actions'],'implemented':True,'execution_mode':'desktop_confirmation','fault_domain':platform+'-browser','egress_modes':['direct'],'note':'本机浏览器填写与账号确认；尚未进行真实账号验收'}))
                continue
            if not s.get(Channel,key):
                s.add(Channel(id=key,engine=engine,platform=platform,priority=80 if engine in {'xhsmcp','ytuploader','xapi'} else 50,
                  capabilities={'media':['text','video'] if engine=='sau' and platform=='zhihu' else ['text'] if engine=='xapi' else ['video','images'] if engine=='xhsmcp' else ['video'],
                  'fault_domain':'x-official-api' if engine in {'xapi','postiz','mixpost'} and platform=='x' else 'biliup-upload' if platform=='bilibili' and engine in {'sau','biliup'} else f'{platform}-browser' if engine in {'sau','spreado','matrixmedia','postbot','xbrowser','xhsmcp'} else f'{platform}-official-api',
                  'implemented':engine in IMPLEMENTED,'egress_modes':['direct'],
                  'note':'候选；需安装、授权、实机核验后启用。Mixpost Lite 能力待核实；biliup 用途限制待澄清。'}))

    for cid in ['xapi-x','xhsmcp-xiaohongshu']:
        channel=s.get(Channel,cid)
        if channel:channel.capabilities={**channel.capabilities,'actions':['publish','comment','reply'],'media':list(dict.fromkeys(channel.capabilities.get('media',[])+['text']))}
