PLATFORMS={'bilibili':'B站','xiaohongshu':'小红书','tencent':'视频号','youtube':'YouTube','x':'X'}
SOURCES={
'sau':'dreammis/social-auto-upload','xhsmcp':'xpzouying/xiaohongshu-mcp',
'biliup':'biliup/biliup','ytuploader':'porjo/youtubeuploader','spreado':'BadKid90s/Spreado',
'postiz':'gitroomhq/postiz-app','mixpost':'inovector/mixpost','matrixmedia':'hanliang97/MatrixMedia',
'postbot':'gitcoffee-os/postbot','resin':'Resinat/Resin','tweepy':'tweepy/tweepy','patchright':'Kaliiiiiiiiii-Vinyzu/patchright'}
COVERAGE={'sau':['bilibili','xiaohongshu','tencent','youtube'],'xhsmcp':['xiaohongshu'],'biliup':['bilibili'],'ytuploader':['youtube'],'spreado':['xiaohongshu','tencent'],'postiz':['x','youtube'],'mixpost':['x','youtube'],'matrixmedia':['bilibili','xiaohongshu','tencent'],'postbot':['bilibili','xiaohongshu','tencent'],'xapi':['x'],'xbrowser':['x']}
IMPLEMENTED={'sau','xhsmcp','biliup','ytuploader','xapi','matrixmedia','spreado'}
def seed(s):
    from .db import Channel
    for engine,platforms in COVERAGE.items():
        for platform in platforms:
            key=f'{engine}-{platform}'
            if not s.get(Channel,key):
                s.add(Channel(id=key,engine=engine,platform=platform,priority=80 if engine in {'xhsmcp','ytuploader','xapi'} else 50,
                  capabilities={'media':['text'] if engine=='xapi' else ['video','images'] if engine=='xhsmcp' else ['video'],
                  'fault_domain':'x-official-api' if engine in {'xapi','postiz','mixpost'} and platform=='x' else 'biliup-upload' if platform=='bilibili' and engine in {'sau','biliup'} else f'{platform}-browser' if engine in {'sau','spreado','matrixmedia','postbot','xbrowser','xhsmcp'} else f'{platform}-official-api',
                  'implemented':engine in IMPLEMENTED,'egress_modes':['direct'],
                  'note':'候选；需安装、授权、实机核验后启用。Mixpost Lite 能力待核实；biliup 用途限制待澄清。'}))
