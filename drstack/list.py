# Copyright 2012 Dean Troyer
# Copyright 2011 OpenStack LLC.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
LIST command
"""
from keystoneclient import exceptions as kc_exceptions

from drstack import base
from drstack import exceptions
from drstack import utils


class ListCommand(base.Command):

    def __init__(self, top=None):
        super(ListCommand, self).__init__(cmd='list', top=top)

    def on_catalog(self, args):
        service_name = args[1] if len(args) > 1 else None
        for service in self.top.kc.service_catalog.catalog.get(
                'serviceCatalog', []):
            if service_name and service_name != service['type']:
                continue
            endpoints = service['endpoints']
            for endpoint in endpoints:
                for k in endpoint.keys():
                    if not k in ['id']:
                        print "%s.%s=%s" % (service['type'], k,
                                endpoint.get(k, ''))

    def on_flavor(self, args):
        self.top._get_nova()
        utils.print_list(self.top.nc.flavors.list(), ['id', 'name'])

    def on_image(self, args):
        self.top.get_glance_client()
        utils.print_dict_list(self.top.gc.get_images(), ['id', 'name'])

    def on_imagen(self, args):
        self.top._get_nova()
        utils.print_list(self.top.nc.images.list(), ['id', 'name'])

    def on_instance(self, args):
        self.top._get_nova()
        utils.print_list(self.top.nc.servers.list(detailed=False),
                ['id', 'name'])

    def on_keypair(self, args):
        self.top._get_nova()
        utils.print_list(self.top.nc.keypairs.list(), ['id', 'name'])

    def on_role(self, args):
        if len(args) > 1:
            try:
                user_ref = self.top.kc.users.get_by_name_or_id(args[1])
                user_id = user_ref.id
            except kc_exceptions.NotFound:
                print "tenant %s not found" % args[1]
                return
        else:
            user_id = None
        try:
            if user_id:
                # FIXME(dtroyer): apparently UserController.get_user_roles()
                #                 is not implemented in keystone
                utils.print_list(self.top.kc.roles.roles_for_user(user_id),
                        ['id', 'name'])
            else:
                utils.print_list(self.top.kc.roles.list(), ['id', 'name'])
        except kc_exceptions.NotFound:
            # Most likely this is not authorized
            raise exceptions.NotAuthorized(None, 'list role')

    def on_security_group(self, args):
        self.top._get_nova()
        utils.print_list(self.top.nc.security_groups.list(), ['id', 'name'])

    def on_security_group_rules(self, args):
        self.top._get_nova()
        utils.print_list(self.top.nc.security_group_rules.list(),
                ['id', 'name'])

    def on_service(self, args):
        try:
            utils.print_list(self.top.kc.services.list(), ['id', 'name'])
        except kc_exceptions.NotFound:
            # Most likely this is not authorized
            raise exceptions.NotAuthorized(None, 'list service')

    def on_tenant(self, args):
        kwargs = {}
        try:
            utils.print_list(self.top.kc.tenants.list(**kwargs),
                    ['name', 'id', 'enabled', 'description'])
        except kc_exceptions.NotFound:
            # Most likely this is not authorized
            raise exceptions.NotAuthorized(None, 'list tenant')

    def on_user(self, args):
        if len(args) > 1:
            try:
                tenant_ref = self.top.kc.tenants.get_by_name_or_id(args[1])
                tenant_id = tenant_ref.id
            except kc_exceptions.NotFound:
                print "tenant %s not found" % args[1]
                return
        else:
            tenant_id = None
        try:
            utils.print_list(self.top.kc.users.list(tenant_id=tenant_id,
                                                    limit=999),
                    ['name', 'id', 'enabled', 'email'])
        except kc_exceptions.NotFound:
            # Most likely this is not authorized
            raise exceptions.NotAuthorized(None, 'list user')
