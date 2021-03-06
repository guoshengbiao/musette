from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from musette._environ import Environment, environ, resolve, resolve_files
from musette._environ import text_type

basename = os.path.basename
dirname = os.path.dirname
pathjoin = os.path.join
abspath = os.path.abspath

def filepath(relpath):
    return pathjoin(dirname(abspath(__file__)), "data", relpath.lstrip('/'))

class BaseTests(unittest.TestCase):

    URL = 'http://www.google.com/'
    POSTGRES = 'postgres://uf07k1i6d8ia0v:wegauwhgeuioweg@ec2-107-21-253-135.compute-1.amazonaws.com:5431/d8r82722r2kuvn'
    MYSQL = 'mysql://bea6eb025ca0d8:69772142@us-cdbr-east.cleardb.com/heroku_97681db3eff7580?reconnect=true'
    MYSQLGIS = 'mysqlgis://user:password@127.0.0.1/some_database'
    SQLITE = 'sqlite:////full/path/to/your/database/file.sqlite'
    MEMCACHE = 'memcache://127.0.0.1:11211'
    REDIS = 'rediscache://127.0.0.1:6379:1?client_class=redis_cache.client.DefaultClient&password=secret'
    EMAIL = 'smtps://user@domain.com:password@smtp.example.com:587'
    JSON = dict(one='bar', two=2, three=33.44)
    DICT = dict(foo='bar', test='on')
    PATH = '/home/dev'

    @classmethod
    def generateData(cls):
        return dict(STR_VAR='bar',
                    INT_VAR='42',
                    FLOAT_VAR='33.3',
                    FLOAT_COMMA_VAR='33,3',
                    FLOAT_STRANGE_VAR1='123,420,333.3',
                    FLOAT_STRANGE_VAR2='123.420.333,3',
                    BOOL_TRUE_VAR='1',
                    BOOL_TRUE_VAR2='True',
                    BOOL_FALSE_VAR='0',
                    BOOL_FALSE_VAR2='False',
                    PROXIED_VAR='$STR_VAR',
                    INT_LIST='42,33',
                    STR_LIST_WITH_SPACES=' foo,  bar',
                    EMPTY_LIST='',
                    DICT_VAR='foo=bar,test=on',
                    DATABASE_URL=cls.POSTGRES,
                    DATABASE_MYSQL_URL=cls.MYSQL,
                    DATABASE_MYSQL_GIS_URL=cls.MYSQLGIS,
                    DATABASE_SQLITE_URL=cls.SQLITE,
                    CACHE_URL=cls.MEMCACHE,
                    CACHE_REDIS=cls.REDIS,
                    EMAIL_URL=cls.EMAIL,
                    URL_VAR=cls.URL,
                    JSON_VAR=json.dumps(cls.JSON),
                    PATH_VAR=cls.PATH,
                    A_SECRET_VAR='my secret key',
                    A_PASSWORD_VAR='qwerty123',
                   )

    def setUp(self):
        self.env = Environment(self.generateData())

    def assertTypeAndValue(self, type_, expected, actual):
        self.assertEqual(type_, type(actual))
        self.assertEqual(expected, actual)


class EnvTests(BaseTests):

    def test_not_present_with_default(self):
        self.assertEqual(3, self.env('not_present', default=3))

    def test_not_present_without_default(self):
        self.assertRaises(KeyError, self.env, 'not_present')

    def test_str(self):
        self.assertTypeAndValue(text_type, 'bar', self.env('STR_VAR'))
        self.assertTypeAndValue(text_type, 'bar', self.env.str('STR_VAR'))

    def test_int(self):
        self.assertTypeAndValue(int, 42, self.env('INT_VAR', cast=int))
        self.assertTypeAndValue(int, 42, self.env.int('INT_VAR'))

    def test_int_with_none_default(self):
        self.assertTrue(self.env('NOT_PRESENT_VAR', cast=int, default=None) is None)

    def test_float(self):
        self.assertTypeAndValue(float, 33.3, self.env('FLOAT_VAR', cast=float))
        self.assertTypeAndValue(float, 33.3, self.env.float('FLOAT_VAR'))

        self.assertTypeAndValue(float, 33.3, self.env('FLOAT_COMMA_VAR', cast=float))
        self.assertTypeAndValue(float, 123420333.3, self.env('FLOAT_STRANGE_VAR1', cast=float))
        self.assertTypeAndValue(float, 123420333.3, self.env('FLOAT_STRANGE_VAR2', cast=float))

    def test_bool_true(self):
        self.assertTypeAndValue(bool, True, self.env('BOOL_TRUE_VAR', cast=bool))
        self.assertTypeAndValue(bool, True, self.env('BOOL_TRUE_VAR2', cast=bool))
        self.assertTypeAndValue(bool, True, self.env.bool('BOOL_TRUE_VAR'))

    def test_bool_false(self):
        self.assertTypeAndValue(bool, False, self.env('BOOL_FALSE_VAR', cast=bool))
        self.assertTypeAndValue(bool, False, self.env('BOOL_FALSE_VAR2', cast=bool))
        self.assertTypeAndValue(bool, False, self.env.bool('BOOL_FALSE_VAR'))

    def test_proxied_value(self):
        self.assertTypeAndValue(text_type, 'bar', self.env('PROXIED_VAR'))

    def test_int_list(self):
        self.assertTypeAndValue(list, [42, 33], self.env('INT_LIST', cast=[int]))
        self.assertTypeAndValue(list, [42, 33], self.env.list('INT_LIST', int))

    def test_str_list_with_spaces(self):
        self.assertTypeAndValue(list, [' foo', '  bar'],
                                self.env('STR_LIST_WITH_SPACES', cast=[text_type]))
        self.assertTypeAndValue(list, [' foo', '  bar'],
                                self.env.list('STR_LIST_WITH_SPACES'))

    def test_empty_list(self):
        self.assertTypeAndValue(list, [], self.env('EMPTY_LIST', cast=[int]))

    def test_dict_value(self):
        self.assertTypeAndValue(dict, self.DICT, self.env.dict('DICT_VAR'))

    def test_dict_parsing(self):

        self.assertEqual({'a': '1'}, self.env.parse_value('a=1', dict))
        self.assertEqual({'a': 1}, self.env.parse_value('a=1', dict(value=int)))
        self.assertEqual({'a': ['1', '2', '3']}, self.env.parse_value('a=1,2,3', dict(value=[text_type])))
        self.assertEqual({'a': [1, 2, 3]}, self.env.parse_value('a=1,2,3', dict(value=[int])))
        self.assertEqual({'a': 1, 'b': [1.1, 2.2], 'c': 3},
                         self.env.parse_value('a=1;b=1.1,2.2;c=3', dict(value=int, cast=dict(b=[float]))))

    def test_url_value(self):
        url = self.env.url('URL_VAR')
        self.assertEqual(url.__class__, self.env.URL_CLASS)
        self.assertEqual(url.geturl(), self.URL)

    def test_db_url_value(self):
        pg_config = self.env.db()
        self.assertEqual(pg_config['ENGINE'], 'django.db.backends.postgresql_psycopg2')
        self.assertEqual(pg_config['NAME'], 'd8r82722r2kuvn')
        self.assertEqual(pg_config['HOST'], 'ec2-107-21-253-135.compute-1.amazonaws.com')
        self.assertEqual(pg_config['USER'], 'uf07k1i6d8ia0v')
        self.assertEqual(pg_config['PASSWORD'], 'wegauwhgeuioweg')
        self.assertEqual(pg_config['PORT'], 5431)

        mysql_config = self.env.db('DATABASE_MYSQL_URL')
        self.assertEqual(mysql_config['ENGINE'], 'django.db.backends.mysql')
        self.assertEqual(mysql_config['NAME'], 'heroku_97681db3eff7580')
        self.assertEqual(mysql_config['HOST'], 'us-cdbr-east.cleardb.com')
        self.assertEqual(mysql_config['USER'], 'bea6eb025ca0d8')
        self.assertEqual(mysql_config['PASSWORD'], '69772142')
        self.assertEqual(mysql_config['PORT'], None)
        
        mysql_gis_config = self.env.db('DATABASE_MYSQL_GIS_URL')
        self.assertEqual(mysql_gis_config['ENGINE'], 'django.contrib.gis.db.backends.mysql')
        self.assertEqual(mysql_gis_config['NAME'], 'some_database')
        self.assertEqual(mysql_gis_config['HOST'], '127.0.0.1')
        self.assertEqual(mysql_gis_config['USER'], 'user')
        self.assertEqual(mysql_gis_config['PASSWORD'], 'password')
        self.assertEqual(mysql_gis_config['PORT'], None)

        sqlite_config = self.env.db('DATABASE_SQLITE_URL')
        self.assertEqual(sqlite_config['ENGINE'], 'django.db.backends.sqlite3')
        self.assertEqual(sqlite_config['NAME'], '/full/path/to/your/database/file.sqlite')

    def test_cache_url_value(self):

        cache_config = self.env.cache_url()
        self.assertEqual(cache_config['BACKEND'], 'django.core.cache.backends.memcached.MemcachedCache')
        self.assertEqual(cache_config['LOCATION'], '127.0.0.1:11211')

        redis_config = self.env.cache_url('CACHE_REDIS')
        self.assertEqual(redis_config['BACKEND'], 'redis_cache.cache.RedisCache')
        self.assertEqual(redis_config['LOCATION'], '127.0.0.1:6379:1')
        self.assertEqual(redis_config['OPTIONS'], {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
            'PASSWORD': 'secret',
        })

    def test_email_url_value(self):

        email_config = self.env.email_url()
        self.assertEqual(email_config['EMAIL_BACKEND'],
                'django.core.mail.backends.smtp.EmailBackend')
        self.assertEqual(email_config['EMAIL_HOST'], 'smtp.example.com')
        self.assertEqual(email_config['EMAIL_HOST_PASSWORD'], 'password')
        self.assertEqual(email_config['EMAIL_HOST_USER'], 'user@domain.com')
        self.assertEqual(email_config['EMAIL_PORT'], 587)
        self.assertEqual(email_config['EMAIL_USE_TLS'], True)


    def test_json_value(self):
        self.assertEqual(self.JSON, self.env.json('JSON_VAR'))

class FileEnvTests(EnvTests):

    def setUp(self):
        self.env = Environment(self.generateData())
        file_path = filepath('test_env.txt')
        self.env.read_env(file_path, PATH_VAR="/another/path")

    def test_path(self):
        self.assertNotEqual(self.PATH, self.env('PATH_VAR'))

class OsEnvironTests(unittest.TestCase):

    def test_singleton_environ(self):
        env = Environment()
        self.assertTrue(env._environ is os.environ)

    def test_environ_mutation(self):
        os.environ['MUSETTE_TEST_KEY'] = 'musette'
        env = Environment()
        self.assertEqual(env['MUSETTE_TEST_KEY'], 'musette')
        env['MUSETTE_TEST_KEY'] = 'mutated'
        self.assertEqual(env['MUSETTE_TEST_KEY'], 'mutated')
        self.assertEqual(os.environ['MUSETTE_TEST_KEY'], 'mutated')
        del env['MUSETTE_TEST_KEY']
        with self.assertRaises(KeyError):
            env['MUSETTE_TEST_KEY']
        with self.assertRaises(KeyError):
            os.environ['MUSETTE_TEST_KEY']

class AltEnvironTests(unittest.TestCase):

    def setUp(self):
        self._environ = {}
        self.env = Environment(self._environ)

    def test_singleton_environ(self):
        try:
            os_environ = os.environ.data
        except AttributeError:
            os_environ = os.environ._data
        self.assertFalse(self.env._environ is os_environ)

class DictionaryInterfaceTests(BaseTests):

    def setUp(self):
        self.env = Environment(
            self.generateData(),
            INT_VAR=int,
            NOT_PRESENT_VAR=(float, 33.3),
            STR_VAR=text_type,
            INT_LIST=[int],
            DEFAULT_LIST=([int], [2])
        )

    def test_get(self):
        self.assertTypeAndValue(int, 42, self.env['INT_VAR'])
        self.assertTypeAndValue(int, 42, self.env.get('INT_VAR'))

    def test_set_and_get(self):
        self.env['INT_VAR'] = 24
        self.assertTypeAndValue(int, 24, self.env['INT_VAR'])
        self.assertTypeAndValue(int, 24, self.env.get('INT_VAR'))
        self.env['INT_VAR'] = '99'
        self.assertTypeAndValue(int, 99, self.env['INT_VAR'])
        self.assertTypeAndValue(int, 99, self.env.get('INT_VAR'))

    def test_get_returns_none_not_keyerror(self):
        self.assertTrue(self.env.get('nonexistent') is None)

    def test_length(self):
        self.assertEqual(len(self.env), 27)

    def test_keys_method(self):
        self.assertEqual(set(self.env.keys()), set(self.generateData().keys()))

    def test_copy(self):
        copied = self.env.copy()
        self.assertTrue(type(self.env) is type(copied))
        self.assertEqual(len(self.env), len(copied))

    def test_get_attribute(self):
        int_var_value = self.env['INT_VAR']
        self.assertEqual(int_var_value, self.env('INT_VAR'))
        self.assertEqual(int_var_value, self.env.INT_VAR)

    def test_set_attribute(self):
        self.env.MY_DEFAULT_SETTING = '1000'
        self.assertEqual(self.env.MY_DEFAULT_SETTING, '1000')
        self.assertEqual(self.env['MY_DEFAULT_SETTING'], '1000')
        self.assertEqual(self.env('MY_DEFAULT_SETTING'), '1000')
        self.assertEqual(self.env.int('MY_DEFAULT_SETTING'), 1000)

    def test_setdefault(self):
        self.assertTrue('INT_VAR' in self.env)
        self.assertTrue('XYZ' not in self.env)
        int_var_value = self.env['INT_VAR']
        ret = self.env.setdefault('INT_VAR', int_var_value)
        self.assertEqual(ret, int_var_value)
        default = 'AAAAAA'
        ret = self.env.setdefault('XYZ', default)
        self.assertEqual(ret, default)
        self.assertTrue('INT_VAR' in self.env)
        self.assertTrue('XYZ' in self.env)

class SchemaEnvTests(BaseTests):

    def setUp(self):
        self.env = Environment(
            self.generateData(),
            INT_VAR=int,
            NOT_PRESENT_VAR=(float, 33.3),
            STR_VAR=text_type,
            INT_LIST=[int],
            DEFAULT_LIST=([int], [2])
        )

    def test_schema(self):
        self.assertTypeAndValue(int, 42, self.env('INT_VAR'))
        self.assertTypeAndValue(float, 33.3, self.env('NOT_PRESENT_VAR'))

        self.assertTypeAndValue(text_type, 'bar', self.env('STR_VAR'))
        self.assertTypeAndValue(text_type, 'foo', self.env('NOT_PRESENT2', default='foo'))

        self.assertTypeAndValue(list, [42, 33], self.env('INT_LIST'))
        self.assertTypeAndValue(list, [2], self.env('DEFAULT_LIST'))

        # Override schema in this one case
        self.assertTypeAndValue(text_type, '42', self.env('INT_VAR', cast=text_type))


class DatabaseTestSuite(unittest.TestCase):

    def test_postgres_parsing(self):
        url = 'postgres://uf07k1i6d8ia0v:wegauwhgeuioweg@ec2-107-21-253-135.compute-1.amazonaws.com:5431/d8r82722r2kuvn'
        url = environ.db_url_config(url)

        self.assertEqual(url['ENGINE'], 'django.db.backends.postgresql_psycopg2')
        self.assertEqual(url['NAME'], 'd8r82722r2kuvn')
        self.assertEqual(url['HOST'], 'ec2-107-21-253-135.compute-1.amazonaws.com')
        self.assertEqual(url['USER'], 'uf07k1i6d8ia0v')
        self.assertEqual(url['PASSWORD'], 'wegauwhgeuioweg')
        self.assertEqual(url['PORT'], 5431)

    def test_postgis_parsing(self):
        url = 'postgis://uf07k1i6d8ia0v:wegauwhgeuioweg@ec2-107-21-253-135.compute-1.amazonaws.com:5431/d8r82722r2kuvn'
        url = environ.db_url_config(url)

        self.assertEqual(url['ENGINE'], 'django.contrib.gis.db.backends.postgis')
        self.assertEqual(url['NAME'], 'd8r82722r2kuvn')
        self.assertEqual(url['HOST'], 'ec2-107-21-253-135.compute-1.amazonaws.com')
        self.assertEqual(url['USER'], 'uf07k1i6d8ia0v')
        self.assertEqual(url['PASSWORD'], 'wegauwhgeuioweg')
        self.assertEqual(url['PORT'], 5431)

    def test_mysql_gis_parsing(self):
        url = 'mysqlgis://uf07k1i6d8ia0v:wegauwhgeuioweg@ec2-107-21-253-135.compute-1.amazonaws.com:5431/d8r82722r2kuvn'
        url = environ.db_url_config(url)

        self.assertEqual(url['ENGINE'], 'django.contrib.gis.db.backends.mysql')
        self.assertEqual(url['NAME'], 'd8r82722r2kuvn')
        self.assertEqual(url['HOST'], 'ec2-107-21-253-135.compute-1.amazonaws.com')
        self.assertEqual(url['USER'], 'uf07k1i6d8ia0v')
        self.assertEqual(url['PASSWORD'], 'wegauwhgeuioweg')
        self.assertEqual(url['PORT'], 5431)

    def test_cleardb_parsing(self):
        url = 'mysql://bea6eb025ca0d8:69772142@us-cdbr-east.cleardb.com/heroku_97681db3eff7580?reconnect=true'
        url = environ.db_url_config(url)

        self.assertEqual(url['ENGINE'], 'django.db.backends.mysql')
        self.assertEqual(url['NAME'], 'heroku_97681db3eff7580')
        self.assertEqual(url['HOST'], 'us-cdbr-east.cleardb.com')
        self.assertEqual(url['USER'], 'bea6eb025ca0d8')
        self.assertEqual(url['PASSWORD'], '69772142')
        self.assertEqual(url['PORT'], None)

    def test_empty_sqlite_url(self):
        url = 'sqlite://'
        url = environ.db_url_config(url)

        self.assertEqual(url['ENGINE'], 'django.db.backends.sqlite3')
        self.assertEqual(url['NAME'], ':memory:')

    def test_memory_sqlite_url(self):
        url = 'sqlite://:memory:'
        url = environ.db_url_config(url)

        self.assertEqual(url['ENGINE'], 'django.db.backends.sqlite3')
        self.assertEqual(url['NAME'], ':memory:')

    def test_database_options_parsing(self):
        url = 'postgres://user:pass@host:1234/dbname?conn_max_age=600'
        url = environ.db_url_config(url)
        self.assertEqual(url['CONN_MAX_AGE'], 600)

        url = 'mysql://user:pass@host:1234/dbname?init_command=SET storage_engine=INNODB'
        url = environ.db_url_config(url)
        self.assertEqual(url['OPTIONS'], {
            'init_command': 'SET storage_engine=INNODB',
        })

    def test_database_ldap_url(self):
        url = 'ldap://cn=admin,dc=nodomain,dc=org:some_secret_password@ldap.nodomain.org/'
        url = environ.db_url_config(url)

        self.assertEqual(url['ENGINE'], 'ldapdb.backends.ldap')
        self.assertEqual(url['HOST'], 'ldap.nodomain.org')
        self.assertEqual(url['PORT'], None)
        self.assertEqual(url['NAME'], 'ldap://ldap.nodomain.org')
        self.assertEqual(url['USER'], 'cn=admin,dc=nodomain,dc=org')
        self.assertEqual(url['PASSWORD'], 'some_secret_password')

class CacheTestSuite(unittest.TestCase):

    def test_memcache_parsing(self):
        url = 'memcache://127.0.0.1:11211'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.memcached.MemcachedCache')
        self.assertEqual(url['LOCATION'], '127.0.0.1:11211')

    def test_memcache_pylib_parsing(self):
        url = 'pymemcache://127.0.0.1:11211'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.memcached.PyLibMCCache')
        self.assertEqual(url['LOCATION'], '127.0.0.1:11211')

    def test_memcache_multiple_parsing(self):
        url = 'memcache://172.19.26.240:11211,172.19.26.242:11212'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.memcached.MemcachedCache')
        self.assertEqual(url['LOCATION'], ['172.19.26.240:11211', '172.19.26.242:11212'])

    def test_memcache_socket_parsing(self):
        url = 'memcache:///tmp/memcached.sock'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.memcached.MemcachedCache')
        self.assertEqual(url['LOCATION'], 'unix:/tmp/memcached.sock')

    def test_dbcache_parsing(self):
        url = 'dbcache://my_cache_table'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.db.DatabaseCache')
        self.assertEqual(url['LOCATION'], 'my_cache_table')

    def test_filecache_parsing(self):
        url = 'filecache:///var/tmp/django_cache'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.filebased.FileBasedCache')
        self.assertEqual(url['LOCATION'], '/var/tmp/django_cache')

    def test_filecache_windows_parsing(self):
        url = 'filecache://C:/foo/bar'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.filebased.FileBasedCache')
        self.assertEqual(url['LOCATION'], 'C:/foo/bar')

    def test_locmem_parsing(self):
        url = 'locmemcache://'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.locmem.LocMemCache')
        self.assertEqual(url['LOCATION'], '')

    def test_locmem_named_parsing(self):
        url = 'locmemcache://unique-snowflake'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.locmem.LocMemCache')
        self.assertEqual(url['LOCATION'], 'unique-snowflake')

    def test_dummycache_parsing(self):
        url = 'dummycache://'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.dummy.DummyCache')
        self.assertEqual(url['LOCATION'], '')

    def test_redis_parsing(self):
        url = 'rediscache://127.0.0.1:6379:1?client_class=redis_cache.client.DefaultClient&password=secret'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'redis_cache.cache.RedisCache')
        self.assertEqual(url['LOCATION'], '127.0.0.1:6379:1')
        self.assertEqual(url['OPTIONS'], {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
            'PASSWORD': 'secret',
        })

    def test_redis_socket_parsing(self):
        url = 'rediscache:///path/to/socket:1'
        url = environ.cache_url_config(url)
        self.assertEqual(url['BACKEND'], 'redis_cache.cache.RedisCache')
        self.assertEqual(url['LOCATION'], 'unix:/path/to/socket:1')

    def test_options_parsing(self):
        url = 'filecache:///var/tmp/django_cache?timeout=60&max_entries=1000&cull_frequency=0'
        url = environ.cache_url_config(url)

        self.assertEqual(url['BACKEND'], 'django.core.cache.backends.filebased.FileBasedCache')
        self.assertEqual(url['LOCATION'], '/var/tmp/django_cache')
        self.assertEqual(url['TIMEOUT'], 60)
        self.assertEqual(url['OPTIONS'], {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 0,
        })

    def test_custom_backend(self):
        url = 'memcache://127.0.0.1:5400?foo=option&bars=9001'
        backend = 'redis_cache.cache.RedisCache'
        url = environ.cache_url_config(url, backend)

        self.assertEqual(url['BACKEND'], backend)
        self.assertEqual(url['LOCATION'], '127.0.0.1:5400')
        self.assertEqual(url['OPTIONS'], {
            'FOO': 'option',
            'BARS': 9001,
        })


class EmailTests(unittest.TestCase):

    def test_smtp_parsing(self):
        url = 'smtps://user@domain.com:password@smtp.example.com:587'
        url = environ.email_url_config(url)

        self.assertEqual(url['EMAIL_BACKEND'],
                'django.core.mail.backends.smtp.EmailBackend')
        self.assertEqual(url['EMAIL_HOST'], 'smtp.example.com')
        self.assertEqual(url['EMAIL_HOST_PASSWORD'], 'password')
        self.assertEqual(url['EMAIL_HOST_USER'], 'user@domain.com')
        self.assertEqual(url['EMAIL_PORT'], 587)
        self.assertEqual(url['EMAIL_USE_TLS'], True)


class InterpolationTests(unittest.TestCase):

    def test_empty_input(self):
        lines = '''
        '''.splitlines()
        d = resolve([lines])
        self.assertTrue(type(d) is dict)
        self.assertTrue(len(d) == 0)

    def test_default_separators(self):
        lines = '''
        foo := bar
        fee:= fum
        fab :=day
        null :=
        '''.splitlines()
        d = resolve([lines])
        self.assertEqual(d['foo'], 'bar')
        self.assertEqual(d['fee'], 'fum')
        self.assertEqual(d['fab'], 'day')
        self.assertEqual(d['null'], '')
        lines = '''
        foo = bar
        fee= fum
        fab =day
        null =
        '''.splitlines()
        d = resolve([lines])
        self.assertEqual(d['foo'], 'bar')
        self.assertEqual(d['fee'], 'fum')
        self.assertEqual(d['fab'], 'day')
        self.assertEqual(d['null'], '')

    def test_multiple_input(self):
        common = '''
        foo := bar
        fee:= fum
        fab :=day
        null :=
        '''.splitlines()
        env_overrides = '''
        password := mysecret
        fab := night
        null := nolongernull
        '''.splitlines()
        d = resolve([common, env_overrides])
        self.assertEqual(d['foo'], 'bar')
        self.assertEqual(d['fee'], 'fum')
        self.assertEqual(d['fab'], 'night')
        self.assertEqual(d['null'], 'nolongernull')
        self.assertEqual(d['password'], 'mysecret')

    def test_interpolation(self):
        lines = '''
        foo := bar
        fat := cat
        fee := DB_${foo}
        fab := ${fee} TABLE_${foo}
        baf := TABLE_${foo} $fee
        fit := $fat ${fab}
        tif := $fab $fat
        '''.splitlines()
        d = resolve([lines])
        self.assertEqual(d['foo'], 'bar')
        self.assertEqual(d['fee'], 'DB_bar')
        self.assertEqual(d['fab'], 'DB_bar TABLE_bar')
        self.assertEqual(d['baf'], 'TABLE_bar DB_bar')
        self.assertEqual(d['fit'], 'cat DB_bar TABLE_bar')
        self.assertEqual(d['tif'], 'DB_bar TABLE_bar cat')

    def test_bad_input(self):
        lines = '''
        foo := bar
        fee := DB_$typo
        '''.splitlines()
        self.assertRaises(KeyError, resolve, [lines])

        lines = '''
        2foo := bar
        fee := DB_$2foo
        '''.splitlines()
        self.assertRaises(ValueError, resolve, [lines])

    def test_defaults(self):
        lines = '''
        foo := bar
        fee := DB_$typo
        '''.splitlines()
        d = resolve([lines], {'typo': 'TEST'})
        self.assertEqual(d['foo'], 'bar')
        self.assertEqual(d['fee'], 'DB_TEST')

    def test_overrides(self):
        lines = '''
        foo := bar
        fee := DB_$typo
        '''.splitlines()
        d = resolve([lines], {'typo': 'TEST'}, {'fee': 'OVERRIDE'})
        self.assertEqual(d['foo'], 'bar')
        self.assertEqual(d['fee'], 'OVERRIDE')

    def test_file_input(self):
        infiles = [filepath("common.properties"), filepath("env.properties")]
        d = resolve_files(infiles)
        self.assertEqual(d['foo'], 'TEST')
        self.assertEqual(d['fee'], 'DB_TEST')
        self.assertEqual(d['fab'], 'DB_TEST TABLE_TEST')
        self.assertEqual(d['baf'], 'TABLE_TEST DB_TEST')
        self.assertEqual(d['fit'], 'cat DB_TEST TABLE_TEST')
        self.assertEqual(d['tif'], 'DB_TEST TABLE_TEST cat')

    def test_read_method(self):
        ENVIRON = {}
        env = Environment(ENVIRON)
        infiles = [filepath("common.properties"), filepath("env.properties")]
        env.read(infiles)
        self.assertEqual(ENVIRON['foo'], 'TEST')
        self.assertEqual(ENVIRON['fee'], 'DB_TEST')
        self.assertEqual(ENVIRON['fab'], 'DB_TEST TABLE_TEST')
        self.assertEqual(ENVIRON['baf'], 'TABLE_TEST DB_TEST')
        self.assertEqual(ENVIRON['fit'], 'cat DB_TEST TABLE_TEST')
        self.assertEqual(ENVIRON['tif'], 'DB_TEST TABLE_TEST cat')

class MoreInterpolationTests(unittest.TestCase):

    def test_set_and_get_variable_values(self):
        ENVIRON = {}
        env = Environment(ENVIRON)
        env['PATH'] = '$CURRENT/path/to/file'
        self.assertEqual(env['PATH'], '$CURRENT/path/to/file')
        env['CURRENT'] = '/home/user'
        self.assertEqual(env['PATH'], '/home/user/path/to/file')

    def test_set_and_get_nested_variable_values(self):
        ENVIRON = {}
        env = Environment(ENVIRON)
        env['PATH'] = '$CURRENT/path/to/file/$NAME'
        self.assertEqual(env['PATH'], '$CURRENT/path/to/file/$NAME')
        env['CURRENT'] = '${ROOT}/instance'
        # unresolved
        self.assertEqual(env['CURRENT'], '${ROOT}/instance')
        self.assertEqual(env['PATH'], '$CURRENT/path/to/file/$NAME')
        env['ROOT'] = '/opt'
        # still unresolved
        self.assertEqual(env['CURRENT'], '${ROOT}/instance')
        self.assertEqual(env['PATH'], '$CURRENT/path/to/file/$NAME')
        env['NAME'] = 'setup.py'
        # resolved
        self.assertEqual(env['CURRENT'], '/opt/instance')
        self.assertEqual(env['PATH'], '/opt/instance/path/to/file/setup.py')

    def test_set_and_get_nested_variable_values_again(self):
        ENVIRON = {}
        env = Environment(ENVIRON)
        env['PATH'] = '$CURRENT/path/to/file/$NAME'
        self.assertEqual(env['PATH'], '$CURRENT/path/to/file/$NAME')
        env['CURRENT'] = '${ROOT}/instance'
        # unresolved
        self.assertEqual(env['CURRENT'], '${ROOT}/instance')
        self.assertEqual(env['PATH'], '$CURRENT/path/to/file/$NAME')
        env['NAME'] = 'setup.py'
        # still unresolved
        self.assertEqual(env['CURRENT'], '${ROOT}/instance')
        self.assertEqual(env['PATH'], '$CURRENT/path/to/file/$NAME')
        env['ROOT'] = '/opt'
        # resolved
        self.assertEqual(env['CURRENT'], '/opt/instance')
        self.assertEqual(env['PATH'], '/opt/instance/path/to/file/setup.py')

    def test_variables_in_initial_dict(self):
        env = Environment({'INSTALL_ROOT': '$PWD', 'PATH': '$INSTALL_ROOT/path'})
        self.assertEqual(env['INSTALL_ROOT'], '$PWD')
        self.assertEqual(env['PATH'], '$INSTALL_ROOT/path')
        env['PWD'] = '/home/user'
        self.assertEqual(env['INSTALL_ROOT'], '/home/user')
        self.assertEqual(env['PATH'], '/home/user/path')

class PrettyPrintTests(BaseTests):

    def test_pprint(self):
        from musette.compat import BytesIO
        stream = BytesIO()
        self.env.pprint(stream=stream, maxlines=1)
        expected = b'''
A_PASSWORD_VAR = ********

'''
        self.assertEqual(stream.getvalue(), expected)

        stream.seek(0)
        self.env.pprint(stream=stream, maxlines=2)
        expected = b'''
A_PASSWORD_VAR = ********
A_SECRET_VAR = ********

'''
        self.assertEqual(stream.getvalue(), expected)

        stream.seek(0)
        self.env.pprint(stream=stream, maxlines=13)
        expected = b'''
A_PASSWORD_VAR = ********
A_SECRET_VAR = ********

BOOL_FALSE_VAR = 0
BOOL_FALSE_VAR2 = False
BOOL_TRUE_VAR = 1
BOOL_TRUE_VAR2 = True

CACHE_REDIS = rediscache://127.0.0.1:6379:1?client_class=redis_cache.client.DefaultClient&password=secret
CACHE_URL = memcache://127.0.0.1:11211

DATABASE_MYSQL_GIS_URL = mysqlgis://user:password@127.0.0.1/some_database
DATABASE_MYSQL_URL = mysql://bea6eb025ca0d8:69772142@us-cdbr-east.cleardb.com/heroku_97681db3eff7580?reconnect=true
DATABASE_SQLITE_URL = sqlite:////full/path/to/your/database/file.sqlite
DATABASE_URL = postgres://uf07k1i6d8ia0v:wegauwhgeuioweg@ec2-107-21-253-135.compute-1.amazonaws.com:5431/d8r82722r2kuvn

DICT_VAR = foo=bar,test=on

'''
        self.assertEqual(stream.getvalue(), expected)

def load_suite():

    test_suite = unittest.TestSuite()
    cases = [
        EnvTests, FileEnvTests, OsEnvironTests, SchemaEnvTests,
        DatabaseTestSuite, CacheTestSuite, EmailTests, InterpolationTests,
        PrettyPrintTests, DictionaryInterfaceTests, MoreInterpolationTests
    ]
    for case in cases:
        test_suite.addTest(unittest.makeSuite(case))
    return test_suite

if __name__ == "__main__":

    try:
        if sys.argv[1] == '-o':
            for key, value in BaseTests.generateData().items():
                print("{0}={1}".format(key, value))
            sys.exit()
    except IndexError:
        pass

    unittest.TextTestRunner().run(load_suite())

