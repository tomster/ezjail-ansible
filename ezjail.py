#!/usr/bin/python
DOCUMENTATION = '''
---
module: ezjail
author: Tom Lazar
short_description: Manage FreeBSD jails
requirements: [ zfs ]
description:
    - Manage FreeBSD jails
'''

from collections import OrderedDict


def list_jails(output):
    ''' parses the output from calling `ezjail-admin list` and returns a python data structure'''
    jails = OrderedDict()
    for line in output.split('\n')[2:-1]:
        entry = dict(zip(['status', 'jid', 'ip', 'name', 'path'], line.split()))
        jails[entry.pop('name')] = entry
    return jails


class Ezjail(object):

    platform = 'FreeBSD'

    def __init__(self, module, name):
        self.module = module
        self.name = name
        self.changed = False
        self.cmd = [self.module.get_bin_path('ezjail-admin', required=True)]

    def ezjail_admin(self, command, *params):
        return self.module.run_command(' '.join(self.cmd + [command] + list(params)))

    def exists(self):
        (rc, out, err) = self.ezjail_admin('list')
        return self.name in list_jails(out)

    def create(self):
        if self.module.check_mode:
            self.changed = True
            return
        self.changed = True

    def destroy(self):
        raise NotImplemented


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, type='str'),
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            ip_addr=dict(required=True, type='str'),
            ),
        supports_check_mode=True
        )

    state = module.params.pop('state')
    name = module.params.pop('name')
    result = dict(name=name, state=state)

    jail = Ezjail(module, name)

    if state == 'present':
        if not jail.exists():
            jail.create()

    elif state == 'absent':
        if jail.exists():
            jail.destroy()

    result['changed'] = jail.changed
    module.exit_json(**result)

# include magic from lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
if __name__ == "__main__":
    main()
