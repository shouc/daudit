import interface
import logs
import utils
import os
import hashlib
import sys
try:
    import pymysql
    import pymysql.err
except ModuleNotFoundError:
    logs.ERROR("PyMySQL is not installed! Run python3 -m pip install pymysql before checking MySQL / MariaDB")
    sys.exit(0)


class Mysql(interface.Interface):
    def __init__(self,
                 host="127.0.0.1",
                 port=3306,
                 username="root",
                 password=""):
        super().__init__()
        if username is not None:
            self.__username = username
        else:
            self.__username = "root"
        if password is not None:
            self.__password = password
        else:
            self.__password = ""
        if host is not None:
            self.__host = host
        else:
            self.__host = "127.0.0.1"
        if port is not None:
            self.__port = int(port)
        else:
            self.__port = 3306
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = pymysql.connect(host=self.__host,
                                        user=self.__username,
                                        passwd=self.__password,
                                        port=self.__port)
            self.cursor = self.conn.cursor()
        except pymysql.err.OperationalError:
            logs.ERROR('Cannot connect to MySQL')
            sys.exit(0)
        except pymysql.err.InternalError as e:
            logs.ERROR(f'Cannot connect to MySQL: {e}')
            sys.exit(0)

    def check_authentication(self):
        if self.conn is None:
            self.connect()
        self.cursor.execute("SELECT host, user FROM mysql.user")
        weak_passwords = utils.get_weak_passwords()
        for u in self.cursor.fetchall():
            if "%" in u[0]:
                logs.WARN(f"User {u[1]} is exposed to the internet (0.0.0.0)")
            else:
                if utils.is_internal(u[0]):
                    continue
                else:
                    logs.WARN(f"User {u[1]} is exposed to external IP {u[0]}")

            if utils.ask("Would you like to perform weak-password check? This may create high traffic load "
                         "for MySQL server. (i.e. Do not perform this when there is already high traffic.)"):
                flag = True
                for password in weak_passwords:
                    try:
                        conn = pymysql.connect(host=self.__host,
                                               user=u[1],
                                               passwd=password,
                                               port=self.__port)
                        logs.WARN(f"Weak password {password} set by user {u[1]} with host {u[0]}")
                        conn.close()
                        flag = False
                        break
                    except pymysql.err.OperationalError:
                        pass
                    except pymysql.err.InternalError as e:
                        pass
                if flag:
                    logs.DEBUG(f"No weak password is used by user {u[1]} with host {u[0]}")

    def has_obsolete_account(self):
        if self.conn is None:
            self.connect()
        for u in ["test", ""]:
            res = self.cursor.execute(f"SELECT * FROM mysql.user WHERE user='{u}'")
            if res > 0:
                logs.WARN(f"Found one possible obsolete account '{u}'")
            else:
                logs.DEBUG(f"Obsolete account '{u}' is deleted")

    def test_load_file(self):
        if self.conn is None:
            self.connect()
        try:
            self.cursor.execute("SELECT HEX(LOAD_FILE('/etc/passwd')) INTO DUMPFILE '/tmp/test'")
            logs.WARN("--secure-file-priv is not enabled")
        except pymysql.err.InternalError:
            logs.DEBUG("--secure-file-priv is enabled")

    @staticmethod
    def is_trivial_username(username):
        return username == "root" or (len(username) >= 6 and username[:6] == "mysql.") or username == "debian-sys-maint"

    def test_grants(self):
        if self.cursor is None:
            self.connect()
        available_privs = [
            "grant_priv",
            "references_priv",
            "alter_routine_priv",
            "create_routine_priv",
            "file_priv",
            "create_tmp_table_priv",
            "lock_tables_priv",
            "execute_priv",
            "create_user_priv",
            "process_priv",
            "reload_priv",
            "repl_slave_priv",
            "repl_client_priv",
            "show_db_priv",
            "shutdown_priv",
            "super_priv"
        ]
        self.cursor.execute("SELECT user, host, "
                            "grant_priv, "
                            "references_priv, "
                            "alter_routine_priv, "
                            "create_routine_priv, "
                            "file_priv,"
                            "create_tmp_table_priv, "
                            "lock_tables_priv, "
                            "execute_priv, "
                            "create_user_priv, "
                            "process_priv,"
                            "reload_priv, "
                            "repl_slave_priv, "
                            "repl_client_priv, "
                            "show_db_priv, "
                            "shutdown_priv, "
                            "super_priv "
                            "FROM mysql.user ")
        result = self.cursor.fetchall()
        for row in result:
            if self.is_trivial_username(row[0]) and (row[1] == "localhost" or row[1] == "127.0.0.1"):
                logs.DEBUG("Skipping privilege checking for root/internal account")
                continue
            for k,v in enumerate(row):
                if k == 0 or k == 1:
                    continue
                if v == 'Y':
                    logs.WARN(f'Setting {available_privs[k-2]} = N is for user {row[0]} with host {row[1]}')

    def test_db_grants(self):
        if self.cursor is None:
            self.connect()
        available_privs = [
            "drop_priv",
            "grant_priv",
            "references_priv",
            "create_tmp_table_priv",
            "lock_tables_priv",
            "create_routine_priv",
            "alter_routine_priv",
            "execute_priv",
            "event_priv",
            "trigger_priv"

        ]
        self.cursor.execute("SELECT user, host, "
                            "drop_priv, "
                            "grant_priv, "
                            "references_priv,"
                            "create_tmp_table_priv,"
                            "lock_tables_priv,"
                            "create_routine_priv,"
                            "alter_routine_priv,"
                            "execute_priv,"
                            "event_priv,"
                            "trigger_priv "
                            "FROM mysql.db ")
        result = self.cursor.fetchall()
        for row in result:
            if self.is_trivial_username(row[0]) and (row[1] == "localhost" or row[1] == "127.0.0.1"):
                logs.DEBUG("Skipping database privilege checking for root/internal account")
                continue
            for k, v in enumerate(row):
                if k == 0 or k == 1:
                    continue
                if v == 'Y':
                    logs.WARN(f'Setting {available_privs[k-2]} = N is for user {row[0]} with host {row[1]}')

    def has_useless_db(self):
        if self.cursor is None:
            self.connect()
        self.cursor.execute("SHOW DATABASES")
        for data in self.cursor.fetchall():
            if data[0] in ["test"]:
                logs.WARN(f"Have useless DB {data[0]}")

    def check_conf(self):
        logs.INFO("Checking authentication...")
        self.check_authentication()
        logs.INFO("Checking obsolete accounts...")
        self.has_obsolete_account()
        logs.INFO("Checking useless database...")
        self.has_useless_db()
        logs.INFO("Checking load file func...")
        self.test_load_file()
        logs.INFO("Checking global grants...")
        self.test_grants()
        logs.INFO("Checking database grants...")
        self.test_db_grants()

