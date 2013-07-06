from ansible import module_common
from ansible.utils import jsonify
import ansible.constants
import compiler
import imp
import mock


ezjail_admin_list_output = '''STA JID  IP              Hostname                       Root Directory
--- ---- --------------- ------------------------------ ------------------------
ZR  2    192.168.91.131  webserver                      /usr/jails/webserver
ZR  1    127.0.0.2       unbound                        /usr/jails/unbound
ZS  N/A  127.0.0.3       cleanser                       /usr/jails/cleanser
ZR  3    127.0.0.2       appserver                      /usr/jails/appserver
    '''


def get_ezjail_module(args):
    import ezjail
    encoded_args = repr(args.encode('utf-8'))
    encoded_lang = repr(ansible.constants.DEFAULT_MODULE_LANG)
    encoded_complex = repr(jsonify({}))
    fn = ezjail.__file__.replace('.pyc', '.py')
    with open(fn) as f:
        module_data = f.read()
    module_data = module_data.replace(module_common.REPLACER, module_common.MODULE_COMMON)
    module_data = module_data.replace(module_common.REPLACER_ARGS, encoded_args)
    module_data = module_data.replace(module_common.REPLACER_LANG, encoded_lang)
    module_data = module_data.replace(module_common.REPLACER_COMPLEX, encoded_complex)
    ofn = fn.replace('/ezjail.py', '/tmp_ezjail.py')
    with open(ofn, 'w') as f:
        f.write(module_data)
    code = compiler.compile(module_data, ofn, 'exec')
    ezjail = imp.new_module('ezjail')
    exec code in ezjail.__dict__
    ezjail.__file__ = ofn

    class AnsibleModule(ezjail.AnsibleModule):
        def get_bin_path(self, arg, required=False, opt_dirs=[]):
            return '/usr/bin/%s' % arg

    ezjail.AnsibleModule = AnsibleModule

    module = AnsibleModule(**ezjail.MODULE_SPECS)

    return ezjail, module


def test_jail_exists():
    ezjail, module = get_ezjail_module(
        'state=present name=unbound ip_addr=127.0.0.4')
    module.run_command = mock.Mock(return_value=(0, ezjail_admin_list_output, ''))
    jail = ezjail.Ezjail(module)
    assert jail.exists()
    assert module.run_command.call_count == 1


def test_jail_does_not_exist():
    ezjail, module = get_ezjail_module(
        'state=present name=foobar ip_addr=127.0.0.4')
    module.run_command = mock.Mock(return_value=(0, ezjail_admin_list_output, ''))
    jail = ezjail.Ezjail(module)
    assert not jail.exists()
    assert module.run_command.call_count == 1


def test_create_jail():
    ezjail, module = get_ezjail_module(
        'state=present name=foobar ip_addr=127.0.0.4')
    module.run_command = mock.Mock(return_value=(0, ezjail_admin_list_output, ''))
    jail = ezjail.Ezjail(module)
    result = jail()
    assert 'failed' not in result
    assert result['state'] == 'present'


def test_parse_ezjail_admin_list():
    import ezjail
    jails = ezjail.list_jails(ezjail_admin_list_output)
    assert 'appserver' in jails
    assert jails.keys() == ['webserver', 'unbound', 'cleanser', 'appserver']
