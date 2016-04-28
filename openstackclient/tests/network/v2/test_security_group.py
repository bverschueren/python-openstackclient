#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import copy
import mock

from openstackclient.network.v2 import security_group
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


class TestSecurityGroupNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestSecurityGroupNetwork, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestSecurityGroupCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestSecurityGroupCompute, self).setUp()

        # Get a shortcut to the compute client
        self.compute = self.app.client_manager.compute


class TestCreateSecurityGroupNetwork(TestSecurityGroupNetwork):

    # The security group to be created.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
    )

    data = (
        _security_group.description,
        _security_group.id,
        _security_group.name,
        _security_group.project_id,
        '',
    )

    def setUp(self):
        super(TestCreateSecurityGroupNetwork, self).setUp()

        self.network.create_security_group = mock.Mock(
            return_value=self._security_group)

        # Set identity client v3. And get a shortcut to Identity client.
        identity_client = identity_fakes.FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.identity = identity_client
        self.identity = self.app.client_manager.identity

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity.projects
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity.domains
        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = security_group.CreateSecurityGroup(self.app, self.namespace)

    def test_create_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_create_min_options(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('name', self._security_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group.assert_called_once_with(**{
            'description': self._security_group.name,
            'name': self._security_group.name,
        })
        self.assertEqual(tuple(self.columns), columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--description', self._security_group.description,
            '--project', identity_fakes.project_name,
            '--project-domain', identity_fakes.domain_name,
            self._security_group.name,
        ]
        verifylist = [
            ('description', self._security_group.description),
            ('name', self._security_group.name),
            ('project', identity_fakes.project_name),
            ('project_domain', identity_fakes.domain_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group.assert_called_once_with(**{
            'description': self._security_group.description,
            'name': self._security_group.name,
            'tenant_id': identity_fakes.project_id,
        })
        self.assertEqual(tuple(self.columns), columns)
        self.assertEqual(self.data, data)


class TestCreateSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group to be shown.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group()

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
    )

    data = (
        _security_group.description,
        _security_group.id,
        _security_group.name,
        _security_group.tenant_id,
        '',
    )

    def setUp(self):
        super(TestCreateSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.security_groups.create.return_value = self._security_group

        # Get the command object to test
        self.cmd = security_group.CreateSecurityGroup(self.app, None)

    def test_create_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_create_network_options(self):
        arglist = [
            '--project', identity_fakes.project_name,
            '--project-domain', identity_fakes.domain_name,
            self._security_group.name,
        ]
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_create_min_options(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('name', self._security_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.security_groups.create.assert_called_once_with(
            self._security_group.name,
            self._security_group.name)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--description', self._security_group.description,
            self._security_group.name,
        ]
        verifylist = [
            ('description', self._security_group.description),
            ('name', self._security_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.security_groups.create.assert_called_once_with(
            self._security_group.name,
            self._security_group.description)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteSecurityGroupNetwork(TestSecurityGroupNetwork):

    # The security group to be deleted.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    def setUp(self):
        super(TestDeleteSecurityGroupNetwork, self).setUp()

        self.network.delete_security_group = mock.Mock(return_value=None)

        self.network.find_security_group = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.DeleteSecurityGroup(self.app, self.namespace)

    def test_security_group_delete(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('group', self._security_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.delete_security_group.assert_called_once_with(
            self._security_group)
        self.assertIsNone(result)


class TestDeleteSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group to be deleted.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group()

    def setUp(self):
        super(TestDeleteSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.security_groups.delete = mock.Mock(return_value=None)

        self.compute.security_groups.get = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.DeleteSecurityGroup(self.app, None)

    def test_security_group_delete(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('group', self._security_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute.security_groups.delete.assert_called_once_with(
            self._security_group.id)
        self.assertIsNone(result)


class TestListSecurityGroupNetwork(TestSecurityGroupNetwork):

    # The security group to be listed.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    expected_columns = (
        'ID',
        'Name',
        'Description',
        'Project',
    )

    expected_data = ((
        _security_group.id,
        _security_group.name,
        _security_group.description,
        _security_group.tenant_id,
    ),)

    def setUp(self):
        super(TestListSecurityGroupNetwork, self).setUp()

        self.network.security_groups = mock.Mock(
            return_value=[self._security_group])

        # Get the command object to test
        self.cmd = security_group.ListSecurityGroup(self.app, self.namespace)

    def test_security_group_list_no_options(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_groups.assert_called_once_with()
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, tuple(data))

    def test_security_group_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_groups.assert_called_once_with()
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, tuple(data))


class TestListSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group to be listed.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group()

    expected_columns = (
        'ID',
        'Name',
        'Description',
    )
    expected_columns_all_projects = (
        'ID',
        'Name',
        'Description',
        'Project',
    )

    expected_data = ((
        _security_group.id,
        _security_group.name,
        _security_group.description,
    ),)
    expected_data_all_projects = ((
        _security_group.id,
        _security_group.name,
        _security_group.description,
        _security_group.tenant_id,
    ),)

    def setUp(self):
        super(TestListSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False
        self.compute.security_groups.list.return_value = [self._security_group]

        # Get the command object to test
        self.cmd = security_group.ListSecurityGroup(self.app, None)

    def test_security_group_list_no_options(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'search_opts': {'all_tenants': False}}
        self.compute.security_groups.list.assert_called_once_with(**kwargs)
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, tuple(data))

    def test_security_group_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'search_opts': {'all_tenants': True}}
        self.compute.security_groups.list.assert_called_once_with(**kwargs)
        self.assertEqual(self.expected_columns_all_projects, columns)
        self.assertEqual(self.expected_data_all_projects, tuple(data))


class TestSetSecurityGroupNetwork(TestSecurityGroupNetwork):

    # The security group to be set.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    def setUp(self):
        super(TestSetSecurityGroupNetwork, self).setUp()

        self.network.update_security_group = mock.Mock(return_value=None)

        self.network.find_security_group = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.SetSecurityGroup(self.app, self.namespace)

    def test_set_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_set_no_updates(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('group', self._security_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.update_security_group.assert_called_once_with(
            self._security_group,
            **{}
        )
        self.assertIsNone(result)

    def test_set_all_options(self):
        new_name = 'new-' + self._security_group.name
        new_description = 'new-' + self._security_group.description
        arglist = [
            '--name', new_name,
            '--description', new_description,
            self._security_group.name,
        ]
        verifylist = [
            ('description', new_description),
            ('group', self._security_group.name),
            ('name', new_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'description': new_description,
            'name': new_name,
        }
        self.network.update_security_group.assert_called_once_with(
            self._security_group,
            **attrs
        )
        self.assertIsNone(result)


class TestSetSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group to be set.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group()

    def setUp(self):
        super(TestSetSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.security_groups.update = mock.Mock(return_value=None)

        self.compute.security_groups.get = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.SetSecurityGroup(self.app, None)

    def test_set_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_set_no_updates(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('group', self._security_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute.security_groups.update.assert_called_once_with(
            self._security_group,
            self._security_group.name,
            self._security_group.description
        )
        self.assertIsNone(result)

    def test_set_all_options(self):
        new_name = 'new-' + self._security_group.name
        new_description = 'new-' + self._security_group.description
        arglist = [
            '--name', new_name,
            '--description', new_description,
            self._security_group.name,
        ]
        verifylist = [
            ('description', new_description),
            ('group', self._security_group.name),
            ('name', new_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute.security_groups.update.assert_called_once_with(
            self._security_group,
            new_name,
            new_description
        )
        self.assertIsNone(result)


class TestShowSecurityGroupNetwork(TestSecurityGroupNetwork):

    # The security group rule to be shown with the group.
    _security_group_rule = \
        network_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    # The security group to be shown.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group(
            attrs={'security_group_rules': [_security_group_rule._info]}
        )

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
    )

    data = (
        _security_group.description,
        _security_group.id,
        _security_group.name,
        _security_group.project_id,
        security_group._format_network_security_group_rules(
            [_security_group_rule._info]),
    )

    def setUp(self):
        super(TestShowSecurityGroupNetwork, self).setUp()

        self.network.find_security_group = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.ShowSecurityGroup(self.app, self.namespace)

    def test_show_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_show_all_options(self):
        arglist = [
            self._security_group.id,
        ]
        verifylist = [
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_security_group.assert_called_once_with(
            self._security_group.id, ignore_missing=False)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestShowSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group rule to be shown with the group.
    _security_group_rule = \
        compute_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    # The security group to be shown.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group(
            attrs={'rules': [_security_group_rule._info]}
        )

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
    )

    data = (
        _security_group.description,
        _security_group.id,
        _security_group.name,
        _security_group.tenant_id,
        security_group._format_compute_security_group_rules(
            [_security_group_rule._info]),
    )

    def setUp(self):
        super(TestShowSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.security_groups.get.return_value = self._security_group

        # Get the command object to test
        self.cmd = security_group.ShowSecurityGroup(self.app, None)

    def test_show_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_show_all_options(self):
        arglist = [
            self._security_group.id,
        ]
        verifylist = [
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.security_groups.get.assert_called_once_with(
            self._security_group.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)