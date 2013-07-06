from mock import MagicMock
from pytest import fixture
from ezjail import Ezjail, list_jails

ezjail_admin_list_output = '''STA JID  IP              Hostname                       Root Directory
--- ---- --------------- ------------------------------ ------------------------
ZR  2    192.168.91.131  webserver                      /usr/jails/webserver
ZR  1    127.0.0.2       unbound                        /usr/jails/unbound
ZS  N/A  127.0.0.3       cleanser                       /usr/jails/cleanser
ZR  3    127.0.0.2       appserver                      /usr/jails/appserver
    '''


class AnsibleModule(object):

    def get_bin_path(self, arg, required=False, opt_dirs=[]):
        return '/usr/bin/%s' % arg


@fixture
def module():
    return AnsibleModule()


@fixture
def jail(module):
    return Ezjail(module=module, name='foo')


def test_jail_exists(module):
    module.run_command = MagicMock(return_value=(0, ezjail_admin_list_output, ''))
    jail = Ezjail(module=module, name='unbound')
    assert jail.exists()


def test_jail_does_not_exist(module):
    module.run_command = MagicMock(return_value=(0, ezjail_admin_list_output, ''))
    jail = Ezjail(module=module, name='foo')
    assert not jail.exists()


def test_parse_ezjail_admin_list():
    jails = list_jails(ezjail_admin_list_output)
    assert 'appserver' in jails
    assert jails.keys() == ['webserver', 'unbound', 'cleanser', 'appserver']
