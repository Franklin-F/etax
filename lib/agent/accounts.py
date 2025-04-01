from lib.attrdict import AttrDict, AttrList

accounts = [
    {'name': '天津市中宜汽车装具有限公司', 'credit_id': '91120116MA07D9W536', 'user_id': '362330198207187517', 'password': 'Aa123456'}, #
    {'name': '天津恒晟嘉航供应链管理有限公司', 'credit_id': '91120116MABXW7M86D', 'user_id': '130924199004031526', 'password': 'Tj123456'}, # mac test
    {'name': '天津欲旌商贸有限公司', 'credit_id': '91120112MA0764AU6U', 'user_id': '510521197404147588', 'password': 'Aa111111'}, # work test, 202305无抵扣
    {'name': '天津市峰顺国际货物运输代理有限公司', 'credit_id': '91120118MA07CRGB44', 'user_id': '412728197411115211', 'password': 'Hh123456'}, # work test, 202305无抵扣
    {'name': '天津海博轮商贸有限公司', 'credit_id': '91120116MA07EWP14R', 'user_id': '372321198606220877', 'password': 'Aa111111'},
    {'name': '天津市金禾物流有限公司', 'credit_id': '91120116MA0768GW16', 'user_id': '371481198310176636', 'password': 'Dd123456'},
    {'name': '天津卓远联运物流有限公司', 'credit_id': '91120116MA7N2P00XL', 'user_id': '120221198211010046', 'password': 'Aa111111'},  # 202312有189条抵扣
    {'name': '天津市嘉昌旺新能源科技有限公司', 'credit_id': '91120116MACK8R67X2', 'user_id': '120111196002271525', 'password': 'a123456789'},
    {'name': '拓顺物资（天津）有限公司', 'credit_id': '91120116MAD436NF6D', 'user_id': '132929196903264411', 'password': 'Aa123456'},
    {'name': '天津市麦伽伦海洋科技有限公司', 'credit_id': '91120118341058702R', 'user_id': '130622198706168048', 'password': '123456AAaa'},
    {'name': '速达建筑工程（天津）有限公司', 'credit_id': '91120116MA7N68PD0D', 'user_id': '371481199906103619', 'password': 'Hh159753'}, # 小规模 不能勾选
    {'name': '天津市鑫博源商贸有限公司', 'credit_id': '91120116MA7E5EMU3Q', 'user_id': '120225198401255437', 'password': 'Aa123456#'}, # 一般人 无勾选
    {'name': '天津路捷顺物流有限公司', 'credit_id': '91120118MA079QBL5M', 'user_id': '131182198306025048', 'password': 'Hh123456'},
    {'name': '天津岳联企业管理有限公司', 'credit_id': '911201165626692916', 'user_id': '22032319760625005X', 'password': 'Yuelian123'},
    {'name': '天津鑫盛博科技有限公司', 'credit_id': '91120116MABRMD5254', 'user_id': '230207195907260638', 'password': 'Aa123456'},
    {'name': '天津市捷瑞通物流服务有限公司', 'credit_id': '91120116MABWQ59H8Q', 'user_id': '130434198512145221', 'password': 'Aa111111'},
    {'name': '天津通网达科技有限公司', 'credit_id': '91120116MABP9DMK8P', 'user_id': '411323198705151736', 'password': 'Hh159753'},
    {'name': '天津稳胜物流有限公司', 'credit_id': '91120116MACU4Q578R', 'user_id': '372323198810101237', 'password': 'Yue543068499@'},
    {'name': '天津浩瀚石化有限公司', 'credit_id': '91120116MA07D4RY51', 'user_id': '130529198511042620', 'password': 'Aa111111'}, # ok, new version
    {'name': '天津金安国际货运代理有限公司', 'credit_id': '91120116MA07F1454N', 'user_id': '130529198612240335', 'password': 'Aa123456'}, # 密码错, 需改密码
    {'name': '天津鸿悦国际货运代理有限公司', 'credit_id': '91120116MAC5YAAF27', 'user_id': '110227198111080035', 'password': 'djl512301'}, # 密码错, 需改密码
    {'name': '天津一联通物流服务有限公司', 'credit_id': '91120116MAC213UY3F', 'user_id': '120112198701250016', 'password': 'Aa123456'}, # bad
    {'name': '天津维义人力资源服务有限公司', 'credit_id': '91120116MA7L9HCG18', 'user_id': '210726199004200918', 'password': 'Hh159753'}, # bad
    {'name': '天津远致科技发展有限公司', 'credit_id': '91120116MA06CX4971', 'user_id': '110106198912143617', 'password': 'tiyz1130'}, # bad code
    {'name': '天津千晓晟工贸有限公司', 'credit_id': '91120116MA7L3NJ841', 'user_id': '371526200112261611', 'password': 'Ss123456'},
    {'name': '天津祺顺人力资源服务有限公司', 'credit_id': '91120113MA7ET4WQ8U', 'user_id': '120113198803081619', 'password': 'a12345678'},
    {'name': '天津亿之源贸易有限公司', 'credit_id': '91120116MACQK01R9P', 'user_id': '210381197512195610', 'password': 'my001219MY'},
    {'name': '天津坤胜建筑工程有限公司', 'credit_id': '91120116MA7JU8YH8A', 'user_id': '131025198312192712', 'password': 'Hh123456'},
    {'name': '天津重科阀门有限公司', 'credit_id': '91120112MA06TNA58M', 'user_id': '152104198512264125', 'password': 'Dd123456'}, #
    {'name': '天津新胜亿传媒有限公司', 'credit_id': '91120116MACHULD91Y', 'user_id': '372324198606300331', 'password': 'Aa123456'}, #
    {'name': '天津兆麟人力资源管理有限公司（10月份）', 'credit_id': '91120111MACUKG957D', 'user_id': '232101199612123448', 'password': 'Aa111111'}, #
    {'name': '天津市滨海新区林森装卸服务部', 'credit_id': '92120116MA827RC79N', 'user_id': '130283198710082926', 'password': 'Aa111111'}, #
    {'name': '天津鑫路达吊装有限公司', 'credit_id': '91120116MA075QDD0E', 'user_id': '372432197605225430', 'password': 'Ee123456789'}, #
    {'name': '天津冬阳建筑装饰工程有限公司', 'credit_id': '91120223MA07E37E7A', 'user_id': '411423198007286524', 'password': 'Aa111111'}, #
    {'name': '鼎达船舶工程（天津）有限责任公司', 'credit_id': '91120116MABP0M0H9M', 'user_id': '412327198204143726', 'password': 'Aa111111'}, #
    {'name': '熠程（天津）物流科技有限公司', 'credit_id': '91120110MA06XXXD9R', 'user_id': '130705199305120012', 'password': 'Ab111111'}, #
    {'name': '天津汇通博瑞国际货运代理有限公司', 'credit_id': '91120116MA073HTY9K', 'user_id': '120110197508130920', 'password': 'Yy123456'},
    {'name': '桐瑞海国际物流（天津）有限公司', 'credit_id': '91120116MA7EJCTU9X', 'user_id': '12010319570331292X', 'password': 'Dd123456'},
    {'name': '天津望岳建筑工程有限公司', 'credit_id': '91120116MA06XLFN3N', 'user_id': '370902199803282723', 'password': 'LM666666'},
    {'name': '天津滨海新区酷跑咔叮体育竞技俱乐部馆', 'credit_id': '92120191MA07HQMFX5', 'user_id': '120102198301310320', 'password': 'mM888888',},
    {'name': '天津众志人力资源服务有限公司', 'credit_id': '91120116MADH1QRN2D', 'user_id': '22240319640512381X', 'password': 'Aa111111',},
    {'name': '涞水汇森劳务派遣有限公司天津分公司', 'credit_id': '9112011655035337X7', 'user_id': '130181199211053924', 'password': 'lz19921105',},
    {'name': '天津塘沽沃德斯特阀门有限公司', 'credit_id': '91120116MACP478L5R', 'user_id': '350627198105011531', 'password': 'Qh111111',},
    {'name': '鑫盛畅达（天津）供应链管理有限公司', 'credit_id': '91120116MACWC2UF2X', 'user_id': '230204198202041720', 'password': 'zhaoxin25$',},
    {'name': '天津市宏盛格雅装饰工程有限公司', 'credit_id': '91120116MACWUQ993P', 'user_id': '340821198207093436', 'password': 'gaoXU201556',},
    {'name': '旺速达信息科技（天津）有限公司', 'credit_id': '91120116MACURC313L', 'user_id': '130124199402242421', 'password': 'qwer982698',},
    {'name': '天津塘沽尼科诺克阀门有限公司', 'credit_id': '91120116MACN88CP6A', 'user_id': '35058319890603603X', 'password': 'nknkfm1234',},
]

accounts = AttrList(accounts, AttrDict)


def get_account(name=None):
    for account in accounts:
        if account.name == name:
            return account


def search_account(name=None):
    for account in accounts:
        if name in account.name:
            return account


default_account = accounts[-1]
