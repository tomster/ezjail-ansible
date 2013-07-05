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


class Ezjail(object):

    platform = 'FreeBSD'

    def __init__(self, module, name):
        self.module = module
        self.name = name
        self.changed = False

    def exists(self):
        cmd = [self.module.get_bin_path('ezjail-admin', True)]
        cmd.append('list')
        (rc, out, err) = self.module.run_command(' '.join(cmd))
        if rc == 0:
            return True
        else:
            return False

    def create(self):
        if self.module.check_mode:
            self.changed = True
            return

    def destroy(self):
        raise NotImplemented


def main():

    # FIXME: should use dict() constructor like other modules, required=False is default
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
    result = {}
    result['name'] = name
    result['state'] = state

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
main()
