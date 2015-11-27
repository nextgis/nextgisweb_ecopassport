# coding=utf-8
from nextgisweb import Component

__author__ = 'yellow'
__license__ = ''
__date__ = '2014'


@Component.registry.register
class LipetskManageComponent(Component):
    identity = 'lipetsk_manage'

    def initialize(self):
        super(LipetskManageComponent, self).initialize()

    def setup_pyramid(self, config):
        super(LipetskManageComponent, self).setup_pyramid(config)


    settings_info = (
        dict(key='ftp_address', desc=u"Адрес сервера FTP, на котором хранятся выгрузки с 1C"),
        dict(key='ftp_login', desc=u"Имя пользователя для FTP"),
        dict(key='ftp_pass', desc=u"Пароль для FTP"),
        dict(key='ftp_file_name', desc=u"Файл CSV c результатми мониторинга на FTP"),
    )
