# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2011 OpenStack, LLC.
# All Rights Reserved.
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

"""
:mod:`tests` -- Utility methods for tests.
===================================

.. automodule:: utils
   :platform: Unix
   :synopsis: Tests for Nova.
.. moduleauthor:: Nirmal Ranganathan <nirmal.ranganathan@rackspace.com>
.. moduleauthor:: Tim Simpson <tim.simpson@rackspace.com>
"""


import re
import subprocess

from sqlalchemy import create_engine
from sqlalchemy.sql.expression import text

from nova import flags
from nova import utils
from reddwarfclient import Dbaas

FLAGS = flags.FLAGS

from tests.util.client import TestClient as TestClient

_dns_entry_factory = None
def get_dns_entry_factory():
    """Returns a DNS entry factory."""
    global _dns_entry_factory
    if not _dns_entry_factory:
        class_name = FLAGS.dns_instance_entry_factory
        _dns_entry_factory = utils.import_object(class_name)
    return _dns_entry_factory

entry_factory = utils.import_object(FLAGS.dns_instance_entry_factory)


def check_database(container_id, dbname):
    """Checks if the name appears in a container's list of databases."""
    default_db = re.compile("[\w\n]*%s[\w\n]*" % dbname)
    dblist, err = process("sudo vzctl exec %s \"mysql -e 'show databases';\""
                            % container_id)
    if err:
        raise RuntimeError(err)
    if default_db.match(dblist):
        return True
    else:
        return False


def create_dbaas_client(user):
    """Creates a rich client for the RedDwarf API using the test config."""
    test_config.nova.ensure_started()
    dbaas = Dbaas(user.auth_user, user.auth_key, test_config.dbaas.url)
    dbaas.authenticate()
    return dbaas

def create_dns_entry(user_name, container_id):
    """Given the container_Id and it's owner returns the DNS entry."""
    instance = {'user_id':user_name,
                    'id':str(container_id)}
    entry_factory = get_dns_entry_factory()
    return entry_factory.create_entry(instance)

def create_openstack_client(user):
    """Creates a rich client for the OpenStack API using the test config."""
    test_config.nova.ensure_started()
    openstack = OpenStack(user.auth_user, user.auth_key, test_config.dbaas.url)
    openstack.authenticate()
    return openstack

def init_engine(user, password, host):
    return create_engine("mysql://%s:%s@%s:3306" %
                               (user, password, host),
                               pool_recycle=1800, echo=True)

def process(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    result = process.communicate()
    return result


def string_in_list(str, substr_list):
    """Returns True if the string appears in the list."""
    return any([str.find(x) >=0 for x in substr_list])
