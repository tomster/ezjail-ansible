from mock import MagicMock
from pytest import fixture
from ezjail import Ezjail, list_jails


@fixture
def jail():
    return Ezjail(module=MagicMock(), name='foo')


def test_exists(jail):
    assert jail.exists()


def test_parse_ezjail_admin_list():
    output = '''STA JID  IP              Hostname                       Root Directory
--- ---- --------------- ------------------------------ ------------------------
ZR  2    192.168.91.131  webserver                      /usr/jails/webserver
ZR  1    127.0.0.2       unbound                        /usr/jails/unbound
ZS  N/A  127.0.0.3       cleanser                       /usr/jails/cleanser
ZR  3    127.0.0.2       appserver                      /usr/jails/appserver
    '''
    jails = list_jails(output)
    assert 'appserver' in jails
    assert jails.keys() == ['webserver', 'unbound', 'cleanser', 'appserver']
