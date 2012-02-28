# Copyright 2011 OpenStack LLC.
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

from proboscis import after_class
from proboscis import before_class
from proboscis import test
from proboscis.asserts import assert_false
from proboscis.asserts import assert_true
from proboscis.asserts import assert_raises
from tests.util import test_config
from tests.util.users import Requirements
from tests.util import create_dbaas_client
from tests.util import create_test_client
from novaclient import exceptions

AUTH_GROUP = 'dbaas.auth'


@test(groups=[AUTH_GROUP],
      depends_on_groups=["services.initialize"])
class VerifyAuth(object):
    @before_class
    def setUp(self):
        """Sets up the client."""
        # sets up a chuck client that has a valid auth token
        self.chunk = test_config.users.find_user_by_name("chunk")
        self.good_client = create_test_client(self.chunk)

        # shuts the keystone auth service down
        #TODO(cp16net) THIS NEVER WORKED FOR THE KEYSTONE SERVICE
        assert_true(test_config.keystone_service.is_running)
        if test_config.keystone_service.is_running:
            test_config.keystone_service.stop()
        assert_false(test_config.keystone_service.is_running)

        # gets another user to attempt to auth later that should fail
        # because the auth service is down
        self.daffy = test_config.users.find_user_by_name("daffy")

    @after_class(always_run=True)
    def tearDown(self):
        """Be nice to other tests and restart the keystone service normally."""
        test_config.keystone_service.start()

    @test
    def auth_service_failure(self):
        print "user : %r" % self.daffy
#        dbaas_client = create_dbaas_client(self.user)
#        assert dbaas_client.client.auth_token is not None
        # We make a call with a different user that has not authenticated
        assert_raises(exceptions.BadRequest, create_test_client, self.daffy)

    @test
    def auth_service_cache(self):
        print "user client : %r" % self.chunk
        # When we make a call with the good client it should not return an
        # exception because the user has already authenticated to the
        # service and the auth token should be in the cache.
        instances = self.good_client.instances.index()

