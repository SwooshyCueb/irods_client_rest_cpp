from __future__ import print_function

import sys
if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest
import os
import shutil
from .. import lib
from . import session

import json
import irods_rest

class TestClientRest(session.make_sessions_mixin([], []), unittest.TestCase):

    def setUp(self):
        super(TestClientRest, self).setUp()

    def tearDown(self):
        super(TestClientRest, self).tearDown()

    def test_invalid_authentication(self):
        token = irods_rest.authenticate('invalid', 'user', 'native')
        assert(token.find('827000') != -1)

    def test_authentication(self):
        token = irods_rest.authenticate('rods', 'rods', 'native')
        assert(token.find('827000') == -1)

    def test_access(self):
        with session.make_session_for_existing_admin() as admin:
            try:
                file_name = 'test_access_object'
                lib.make_file(file_name, 1024)

                admin.assert_icommand(['iput', file_name])
                admin.assert_icommand(['ils', '-l'], 'STDOUT_SINGLELINE', file_name)

                pwd, _ = lib.execute_command(['ipwd'])
                pwd = pwd.rstrip()
                logical_path = os.path.join(pwd, file_name)

                token  = irods_rest.authenticate('rods', 'rods', 'native')
                result = irods_rest.access(token, logical_path)
                assert(result.find('error') == -1)

                # Verify that the use count option works as expected.
                use_count = 50
                result = json.loads(irods_rest.access(token, logical_path, use_count))
                ticket_id = result['headers']['irods-ticket'][0]
                admin.assert_icommand(['iticket', 'ls', ticket_id], 'STDOUT', ['uses limit: ' + str(use_count)])
            finally:
                os.remove(file_name)
                admin.assert_icommand(['irm', '-f', file_name])

    def test_get_configuration(self):
        token  = irods_rest.authenticate('rods', 'rods', 'native')
        result = irods_rest.get_configuration(token)
        assert(result.find('advanced_settings') != -1)

    def test_put_configuration(self):
        file1 = "/etc/irods/test_rest_cfg_put_1.json"
        file2 = "/etc/irods/test_rest_cfg_put_2.json"

        # clean up
        if os.path.exists(file1):
              os.remove(file1)
        if os.path.exists(file2):
              os.remove(file2)

        cfg    = "%5B%7B%22file_name%22%3A%22test_rest_cfg_put_1.json%22%2C%20%22contents%22%3A%7B%22key0%22%3A%22value0%22%2C%22key1%22%20%3A%20%22value1%22%7D%7D%2C%7B%22file_name%22%3A%22test_rest_cfg_put_2.json%22%2C%22contents%22%3A%7B%22key2%22%20%3A%20%22value2%22%2C%22key3%22%20%3A%20%22value3%22%7D%7D%5D"
        token  = irods_rest.authenticate('rods', 'rods', 'native')

        # put config files
        irods_rest.put_configuration(token, cfg)

        # config files should exist
        assert(os.path.exists(file1))
        assert(os.path.exists(file2))

        # confirm contents for file1
        with open(file1) as f:
            data = json.load(f)
            assert(data['key0'] == 'value0')
            assert(data['key1'] == 'value1')

        # confirm contents for file2
        with open(file2) as f:
            data = json.load(f)
            assert(data['key2'] == 'value2')
            assert(data['key3'] == 'value3')

        # clean up /etc/irods
        os.remove(file1)
        os.remove(file2)

    def test_list(self):
        with session.make_session_for_existing_admin() as admin:
            try:
                file_count = 10

                dir_name = 'test_list_collection_directory'
                lib.make_large_local_tmp_dir(dir_name, file_count, 1024)

                admin.assert_icommand(['iput', '-r', dir_name], 'STDOUT_SINGLELINE', 'Running')
                admin.assert_icommand(['ils', '-l', '-r'], 'STDOUT_SINGLELINE', dir_name)

                pwd, _ = lib.execute_command(['ipwd'])
                pwd = pwd.rstrip()
                logical_path = os.path.join(pwd, dir_name)

                token  = irods_rest.authenticate('rods', 'rods', 'native')
                result = irods_rest.list(token, logical_path, 'false', 'false', 'false', 0, 100)

                cnt = 0
                lst = json.loads(result)
                for entry in lst['_embedded']:
                    lp = entry['logical_path']
                    print(lp)
                    assert(lp.find('junk') != -1)
                    cnt = cnt + 1

                assert(file_count == cnt)
            finally:
                shutil.rmtree(dir_name)
                admin.assert_icommand(['irm', '-f', '-r', dir_name])

    def test_list_with_limit_and_offset(self):
        with session.make_session_for_existing_admin() as admin:
            try:
                file_count = 10

                dir_name = 'test_list_collection_directory'
                lib.make_large_local_tmp_dir(dir_name, file_count, 1024)

                admin.assert_icommand(['iput', '-r', dir_name], 'STDOUT_SINGLELINE', 'Running')
                admin.assert_icommand(['ils', '-l', '-r'], 'STDOUT_SINGLELINE', dir_name)

                pwd, _ = lib.execute_command(['ipwd'])
                pwd = pwd.rstrip()
                logical_path = os.path.join(pwd, dir_name)

                token  = irods_rest.authenticate('rods', 'rods', 'native')

                offset = 0
                for i in range(1,10):
                    result = irods_rest.list(token, logical_path, 'false', 'false', 'false', offset, 1)
                    lst = json.loads(result)

                    assert(len(lst['_embedded']) == 1)

                    fn = 'junk000' + str(offset)
                    lp = lst['_embedded'][0]['logical_path']
                    print(fn+' vs '+lp)

                    assert(lp.find(fn) != -1)

                    offset = offset + 1
            finally:
                shutil.rmtree(dir_name)
                admin.assert_icommand(['irm', '-f', '-r', dir_name])

    def test_list_with_accoutrements(self):
        with session.make_session_for_existing_admin() as admin:
            try:
                file_name = 'test_access_object'
                lib.make_file(file_name, 1024)

                admin.assert_icommand(['iput', file_name])
                admin.assert_icommand(['ils', '-l'], 'STDOUT_SINGLELINE', file_name)

                pwd, _ = lib.execute_command(['ipwd'])
                pwd = pwd.rstrip()
                logical_path = os.path.join(pwd, file_name)

                admin.assert_icommand(['imeta', 'set', '-d', logical_path, 'attr', 'val', 'unit'])

                token  = irods_rest.authenticate('rods', 'rods', 'native')
                result = irods_rest.list(token, logical_path, 'true', 'true', 'true', 0, 0)

                lst = json.loads(result)['_embedded'][0]

                assert(lst['type'] == 'data_object')

                md = lst['metadata'][0]
                assert(md['attribute'] == 'attr')
                assert(md['value'] == 'val')
                assert(md['units'] == 'unit')

                stat = lst['status_information']
                assert(stat['last_write_time'] != '')
                assert(stat['size'] == 1024)

                perm = lst['permission_information']
                assert(perm['rods']== 'own')

            finally:
                os.remove(file_name)
                admin.assert_icommand(['irm', '-f', file_name])

    def test_query_with_limit_and_offset(self):
        with session.make_session_for_existing_admin() as admin:
            try:
                file_count = 10

                dir_name = 'test_query_collection_directory'
                lib.make_large_local_tmp_dir(dir_name, file_count, 1024)

                admin.assert_icommand(['iput', '-r', dir_name], 'STDOUT_SINGLELINE', 'Running')
                admin.assert_icommand(['ils', '-l', '-r'], 'STDOUT_SINGLELINE', dir_name)

                pwd, _ = lib.execute_command(['ipwd'])
                pwd = pwd.rstrip()
                logical_path = os.path.join(pwd, dir_name)

                token  = irods_rest.authenticate('rods', 'rods', 'native')

                query = "SELECT COLL_NAME, DATA_NAME WHERE COLL_NAME = '"+logical_path+"'"

                offset = 0
                for i in range(1,10):
                    fn = 'junk000' + str(offset)

                    result = irods_rest.query(token, query, 1, offset, 'general')

                    print('*****************\n')
                    print(result)
                    print('*****************\n')

                    res = json.loads(result)
                    assert(len(res['_embedded']) == 1)

                    arr = res['_embedded'][0]

                    assert(arr[0] == logical_path)
                    assert(arr[1] == fn)

                    offset = offset + 1
            finally:
                shutil.rmtree(dir_name)
                admin.assert_icommand(['irm', '-f', '-r', dir_name])

    def test_stream_put_and_get(self):
        with session.make_session_for_existing_admin() as admin:
            try:
                file_name  = 'stream_put_and_get_file'
                file_name2 = file_name+'2'
                with open(file_name, 'w') as f:
                    f.write('This is some test data.  This is only a test.')

                pwd, _ = lib.execute_command(['ipwd'])
                pwd = pwd.rstrip()
                logical_path = os.path.join(pwd, file_name)

                token = irods_rest.authenticate('rods', 'rods', 'native')

                irods_rest.put(token, file_name, logical_path)
                admin.assert_icommand(['ils', '-l'], 'STDOUT_SINGLELINE', file_name)

                irods_rest.get(token, file_name2, logical_path)

                sz  = os.path.getsize(file_name)
                sz2 = os.path.getsize(file_name2)

                print(str(sz) + ' vs ' + str(sz2))

                assert(sz == sz2)
            finally:
                os.remove(file_name)
                os.remove(file_name2)
                admin.assert_icommand(['irm', '-f', file_name])

    def test_zone_report(self):
        with session.make_session_for_existing_admin() as admin:
            zr0, _ = lib.execute_command(['izonereport'])
            js0 = json.loads(zr0)

            token = irods_rest.authenticate('rods', 'rods', 'native')
            zr1 = irods_rest.zone_report(token)
            js1 = json.loads(zr1)

            assert(js0 == js1)
