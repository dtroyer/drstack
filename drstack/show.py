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
SHOW command
"""

from glance.common import exception as gc_exceptions
from keystoneclient import exceptions as kc_exceptions

from drstack import base
from drstack import exceptions
from drstack import utils


class ShowCommand(base.Command):

    def __init__(self, top=None):
        super(ShowCommand, self).__init__(cmd='show', top=top)

    def on_catalog(self, args):
        service_name = args[1] if len(args) > 1 else None
        endpoint_type = args[2] if len(args) > 2 else None
        catalog = self.top.kc.service_catalog.catalog.get('serviceCatalog', [])
        for service in catalog:
            if service_name and service_name != service['type']:
                continue
            endpoints = service['endpoints']
            for endpoint in endpoints:
                for k in endpoint.keys():
                    if endpoint_type and endpoint_type == k:
                        print "%s.%s=%s" % (service['type'], k,
                                endpoint.get(k, ''))

    def on_ec2creds(self, args):
        if len(args) < 3:
            print "Required user and access key"
            return
        try:
            user_ref = self.top.kc.users.get_by_name_or_id(args[1])
            user_id = utils.getid(user_ref)
        except kc_exceptions.NotFound:
            print "user %s not found" % args[1]
            return
        # FIXME(dtroyer): look into more
        cred = self.top.kc.ec2.get(user_id, args[2])
        if cred:
            utils.print_dict(cred._info)

    def on_flavor(self, args):
        self.top._get_nova()
        if len(args) < 2:
            print "need more args for flavor"
            return
        utils.show_object(self.top.nc.flavors, args[1], [
                    'id', 'name', 'disk', 'ram', 'swap', 'vcpus'])

    def on_image(self, args):
        self.top.get_glance_client()
        if len(args) < 2:
            print "no image id"
            return
        image_id = args[1]
        try:
            i = self.top.gc.get_image_meta(image_id)
        except gc_exceptions.NotFound:
            print "No image with ID %s was found" % image_id
            return
        utils.print_dict_fields(i, [
                'id', 'name', 'owner', 'is_public', 'min_disk',
                'min_ram', 'status'])

    def on_imagen(self, args):
        self.top._get_nova()
        if len(args) < 2:
            print "no image id"
            return
        i = self.top.nc.images.get(args[1])
        i.bookmark = [x['href']
                for x in i.links if x['rel'] == 'bookmark'][0]
        utils.print_obj_fields(i, [
                'id', 'name', 'bookmark', 'metadata', 'minDisk',
                'minRam', 'status'])

    def on_instance(self, args):
        self.top._get_nova()
        if len(args) < 2:
            print "no server specified"
            return
        s = self.top.nc.servers.get(args[1])
        s.private_address = s.addresses['private'][0]['addr']
        s.flavor = self.top.nc.flavors.get(s.flavor['id']).name
        try:
            s.user = self.top.kc.users.get(s.user_id).name
        except:
            s.user = ""
        s.image = s.image['id']
        utils.print_obj_fields(s, [
                'id', 'name', 'flavor', 'image',
                'user', 'private_address',
                'status', 'OS-EXT-STS:power_state',
                'OS-EXT-STS:power_state',
                'OS-DCF:diskConfig'])

    def on_role(self, args):
        if len(args) < 2:
            print "no role specified"
            return
        try:
            utils.show_object(self.top.kc.roles, args[1],
                    ['id', 'name'])
        except kc_exceptions.NotFound:
            # Most likely this is not authorized
            raise exceptions.NotAuthorized(None, 'show role')

    def on_tenant(self, args):
        if len(args) < 2:
            print "no tenant specified"
            return
        try:
            utils.print_obj_fields(
                    self.top.kc.tenants.get_by_name_or_id(args[1]),
                    ['id', 'name', 'enabled', 'description'])
        except kc_exceptions.NotFound:
            print "tenant %s not found" % args[1]
        except Exception, e:
            print "other exception: %s" % e
            # Most likely this is not authorized
            raise exceptions.NotAuthorized(None, 'show tenant')

    def on_token(self, args):
        if self.top.auth_token:
            print self.top.auth_token

    def on_user(self, args):
        if len(args) < 2:
            print "no user specified"
            return
        try:
            utils.print_obj_fields(
                    self.top.kc.users.get_by_name_or_id(args[1]),
                    ['id', 'name', 'email', 'enabled'])
        except kc_exceptions.NotFound:
            print "user %s not found" % args[1]
        except Exception, e:
            print "other exception: %s" % e
            # Most likely this is not authorized
            raise exceptions.NotAuthorized(None, 'show user')
