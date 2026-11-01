"""Explicit platform destinations. Listing a platform never asserts a live authorization."""
from urllib.parse import urlsplit,urlencode

def spec(label,home,compose,hosts,media=('text',),comments=True,group='writing'):
    return dict(label=label,home=home,compose=compose,hosts=hosts,media=list(media),actions=['publish','comment','reply'] if comments else ['publish'],group=group,mode='desktop_confirmation')
PLATFORM_SPECS={
 'tieba':spec('贴吧','https://tieba.baidu.com/','https://tieba.baidu.com/',('tieba.baidu.com','passport.baidu.com'),group='community'),
 'zhihu':spec('知乎','https://www.zhihu.com/','https://zhuanlan.zhihu.com/write',('zhihu.com',),('text','video'),group='community'),
 'douban':spec('豆瓣','https://www.douban.com/','https://www.douban.com/topic/create?subtype=note',('douban.com',),('text','images'),group='community'),
 'weibo':spec('微博','https://weibo.com/','https://weibo.com/',('weibo.com','weibo.cn','passport.weibo.com'),('text','images','video'),group='community'),
 'weixin':spec('微信公众号','https://mp.weixin.qq.com/','https://mp.weixin.qq.com/',('mp.weixin.qq.com',),('text',),False,'community'),
 'toutiao':spec('头条号','https://mp.toutiao.com/','https://mp.toutiao.com/profile_v4/graphic/publish',('toutiao.com','snssdk.com'),('text','video')),
 'jianshu':spec('简书','https://www.jianshu.com/','https://www.jianshu.com/writer',('jianshu.com',)),
 'juejin':spec('掘金','https://juejin.cn/','https://juejin.cn/editor/drafts/new?v=2',('juejin.cn',)),
 'csdn':spec('CSDN','https://www.csdn.net/','https://editor.csdn.net/md/',('csdn.net',)),
 'baijiahao':spec('百家号','https://baijiahao.baidu.com/','https://baijiahao.baidu.com/builder/rc/edit?type=news',('baijiahao.baidu.com','baidu.com'),('text','video')),
 'douyin':spec('抖音','https://creator.douyin.com/','https://creator.douyin.com/creator-micro/content/upload',('douyin.com',),('video','images'),group='shortvideo'),
 'kuaishou':spec('快手','https://cp.kuaishou.com/','https://cp.kuaishou.com/article/publish/video',('kuaishou.com','gifshow.com'),('video','images'),group='shortvideo'),
 'xigua':spec('西瓜视频','https://studio.ixigua.com/','https://studio.ixigua.com/upload',('ixigua.com','douyin.com'),('video',),group='shortvideo'),
 'haokan':spec('好看视频','https://haokan.baidu.com/','https://baijiahao.baidu.com/builder/rc/edit?type=video',('haokan.baidu.com','baijiahao.baidu.com','passport.baidu.com'),('video',),group='shortvideo'),
 'tencentvideo':spec('腾讯视频','https://v.qq.com/','https://v.qq.com/biu/creator/upload',('v.qq.com','qq.com'),('video',),group='longvideo'),
 'youku':spec('优酷','https://www.youku.com/','https://sc.youku.com/',('youku.com','passport.youku.com','login.taobao.com'),('video',),group='longvideo'),
 'iqiyi':spec('爱奇艺','https://www.iqiyi.com/','https://mp.iqiyi.com/',('iqiyi.com','qiyi.com'),('video',),group='longvideo'),
 'sohuvideo':spec('搜狐视频','https://tv.sohu.com/','https://my.tv.sohu.com/user/upload/video',('tv.sohu.com','passport.sohu.com'),('video',),group='longvideo'),
 'bilibili':spec('B站','https://www.bilibili.com/','https://member.bilibili.com/platform/upload/video/frame',('bilibili.com',),('text','video','images'),group='core'),
 'xiaohongshu':spec('小红书','https://www.xiaohongshu.com/','https://creator.xiaohongshu.com/publish/publish',('xiaohongshu.com',),('text','video','images'),group='core'),
 'tencent':spec('视频号','https://channels.weixin.qq.com/','https://channels.weixin.qq.com/platform/post/create',('channels.weixin.qq.com','weixin.qq.com'),('video',),group='core'),
 'youtube':spec('YouTube','https://www.youtube.com/','https://studio.youtube.com/',('youtube.com','accounts.google.com'),('video',),group='core'),
 'x':spec('X','https://x.com/','https://x.com/compose/post',('x.com','twitter.com'),('text','images','video'),group='core'),
}

def allowed_url(platform,url):
    try:
        u=urlsplit(url);host=(u.hostname or '').lower()
        return u.scheme=='https' and not u.username and not u.password and u.port in (None,443) and any(host==h or host.endswith('.'+h) for h in PLATFORM_SPECS[platform]['hosts'])
    except (ValueError,KeyError):return False

def validate_intent(platform,payload):
    action=payload.get('action','publish')
    if action not in {'publish','comment','reply'}:raise ValueError('发布动作无效')
    if action=='publish' and platform in PLATFORM_SPECS and payload.get('kind') not in PLATFORM_SPECS[platform]['media']:raise ValueError('此平台没有接入所选内容类型')
    if action!='publish':
        if platform not in PLATFORM_SPECS or action not in PLATFORM_SPECS[platform]['actions']:raise ValueError('此平台没有可用的评论操作')
        if payload.get('kind')!='text':raise ValueError('评论和回复使用纯文字，不接受视频素材')
        if not allowed_url(platform,payload.get('target_url','')):raise ValueError('请输入该平台的 HTTPS 原帖链接')
        if not payload.get('description','').strip():raise ValueError('评论或回复正文不能为空')
        if action=='reply' and not str(payload.get('target_comment_id','')).strip():raise ValueError('回复须指定目标评论 ID 或楼层')
    if payload.get('delivery','published') not in {'published','draft'}:raise ValueError('交付类型无效')
    if action!='publish' and payload.get('delivery')=='draft':raise ValueError('评论不能计作文章草稿')

def destination(platform,payload):
    validate_intent(platform,payload)
    if payload.get('action','publish')!='publish':return payload['target_url']
    if platform=='tieba' and payload.get('options',{}).get('board'):
        return 'https://tieba.baidu.com/f?'+urlencode({'kw':payload['options']['board']})
    return PLATFORM_SPECS[platform]['compose']


def cookie_domain_allowed(platform,domain):
    host=domain.lstrip('.').lower()
    if '.' not in host:return False
    return any(host==allowed or host.endswith('.'+allowed) or allowed.endswith('.'+host) for allowed in PLATFORM_SPECS[platform]['hosts'])
