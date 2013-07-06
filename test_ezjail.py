from mock import MagicMock
from ezjail import Ezjail, list_jails, MODULE_SPECS
import testing
from testing import DummyAnsibleModule

ezjail_admin_list_output = '''STA JID  IP              Hostname                       Root Directory
--- ---- --------------- ------------------------------ ------------------------
ZR  2    192.168.91.131  webserver                      /usr/jails/webserver
ZR  1    127.0.0.2       unbound                        /usr/jails/unbound
ZS  N/A  127.0.0.3       cleanser                       /usr/jails/cleanser
ZR  3    127.0.0.2       appserver                      /usr/jails/appserver
    '''


def get_dummy_module(args):
    testing.MODULE_ARGS = args
    return DummyAnsibleModule(**MODULE_SPECS)


def test_jail_exists():
    module = get_dummy_module('state=present name=unbound ip_addr=127.0.0.4')
    module.run_command = MagicMock(return_value=(0, ezjail_admin_list_output, ''))
    jail = Ezjail(module)
    assert jail.exists()


def test_jail_does_not_exist():
    module = get_dummy_module('state=present name=foobar ip_addr=127.0.0.4')
    module.run_command = MagicMock(return_value=(0, ezjail_admin_list_output, ''))
    jail = Ezjail(module)
    assert not jail.exists()


def test_parse_ezjail_admin_list():
    jails = list_jails(ezjail_admin_list_output)
    assert 'appserver' in jails
    assert jails.keys() == ['webserver', 'unbound', 'cleanser', 'appserver']
