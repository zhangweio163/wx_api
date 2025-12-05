'''
人员信息类
填写须知：
1、不能在该Excel表中对成员信息类别进行增加、删除或修改；
2、Excel中红色字段为必填字段,黑色字段为选填字段（手机和邮箱需选其一填写），字段值里请不要填入“，”字符；手机和邮箱中，若仅填写邮箱或者填写国际手机号+邮箱，导入成功后将发送邀请邮件；
3、账号：成员的唯一标识，由1-64个字母、数字、点(.)、减号(-)或下划线(_)组成，账号相同会进行覆盖导入【账号初始设定后则不支持修改，企业微信系统自动生成的账号，支持修改一次。修改方法：在账号字段用英文冒号隔开新旧账号，示例：old_userid:new_userid】；
4、部门：上下级部门间用‘/’隔开，且从最上级部门开始，例如"腾讯公司/微信事业群/广州研发部"。若存在属于多个部门的情况，不同部门之间用“；”隔开。第一个填写的部门默认为成员的主部门。部门若为空，则自动将成员添加到选择的目录下。部门字段长度不能超过32个字符，部门英文名字段长度不能超过64个字符；
5、支持国内、国际手机号（国内手机号直接输入手机号即可；国际手机号必须包含加号以及国家地区码，格式示例：“+85259****24”） ；
6、网页类型字段：网页名称与网页地址之间用‘；’隔开，并且网页地址以http://或https://开头，格式示例：企业微信；http://work.weixin.qq.com；
7、企业邮箱：成员加入企业后直接可用。邮箱名由1-32个字母、数字、点(.)、减号(-)或下划线(_)组成，后缀必须填写当前企业的域名；
8、视频号：填写视频号名字，对应的视频号必须已绑定到企业微信；
姓名	账号	别名	职务	部门	性别	手机	座机	邮箱	地址	企业邮箱	视频号	激活状态	禁用状态	微信插件
'''
class Person:
    def __init__(self, name, userid, alias="", position="", department="", gender="", mobile=""
                 , telephone="", email="", address="", extid="", videonum="",
                 status="", disable="", wechat_plugin=""):
        self.name = name
        self.userid = userid
        self.alias = alias
        self.position = position
        self.department = department
        self.gender = gender
        self.mobile = mobile
        self.telephone = telephone
        self.email = email
        self.address = address
        self.extid = extid
        self.videonum = videonum
        self.status = status
        self.disable = disable
        self.wechat_plugin = wechat_plugin
    def __repr__(self):
        return (f"Person(name={self.name}, userid={self.userid},"
                f" alias={self.alias}, position={self.position}, department={self.department},"
                f" gender={self.gender}, mobile={self.mobile}, telephone={self.telephone}, email={self.email}, "
                f"address={self.address}, extid={self.extid}, videonum={self.videonum}, status={self.status},"
                f" disable={self.disable}, wechat_plugin={self.wechat_plugin})")