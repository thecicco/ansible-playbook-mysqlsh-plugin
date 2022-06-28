from mysqlsh.plugin_manager import plugin, plugin_function

@plugin_function("security.showPasswordExpire")
def show_password_expire(show_expired=True, session=None):
    """
    Lists all accounts and their expiration date.

    Args:
        show_expired (bool): List expired passwords too (default: false).
        session (object): The optional session object used to query the
            database. If omitted the MySQL Shell's current session will be used.
    
    """
    import mysqlsh
    shell = mysqlsh.globals.shell

    if session is None:
        session = shell.get_session()
        if session is None:
            print("No session specified. Either pass a session object to this "
                  "function or connect the shell to a database")
            return
    stmt = "select @@default_password_lifetime, @@disconnect_on_expired_password"
    result = session.run_sql(stmt)   
    rows = result.fetch_all()
    if rows[0][0] == 0:
        print("Default password doesn't expire")
    else:
        print("Default password expires in %d days" % rows[0][0])
    if rows[0][1] == 1:
        print("On expired password disconnect")
    if show_expired:
        stmt = """select concat(sys.quote_identifier(user),'@',sys.quote_identifier(host))
              AS user, 
              password_last_changed, IF((cast(
              IFNULL(password_lifetime, @@default_password_lifetime) as signed)
              + cast(datediff(password_last_changed, now()) as signed) > 0),
              concat(
               cast(
              IFNULL(password_lifetime, @@default_password_lifetime) as signed)
              + cast(datediff(password_last_changed, now()) as signed), ' days'), 
              IF(@@default_password_lifetime > 0, 'expired', 'do not expire')) expires_in
              from mysql.user
              where 
              user not like 'mysql.%' order by user"""
    else:
        stmt = """select concat(sys.quote_identifier(user),'@',sys.quote_identifier(host))
              AS user, 
              password_last_changed,
              concat(
               cast(
              IFNULL(password_lifetime, @@default_password_lifetime) as signed)
              + cast(datediff(password_last_changed, now()) as signed), ' days') expires_in
              from mysql.user
              where 
              cast(
               IFNULL(password_lifetime, @@default_password_lifetime) as signed)
              + cast(datediff(password_last_changed, now()) as signed) > 0 
              and user not like 'mysql.%' order by user;"""

    result = session.run_sql(stmt)
    shell.dump_rows(result)


@plugin_function("security.showPasswordExpireSoon")
def show_password_expire_soon(expire_in_days=30, session=None):
    """
    Lists all accounts that will expire in specific days.

    Args:
        expire_in_days (integer): List accounts that will expire in that range upper limit, 
                                  if none provided, the default is 30.
        session (object): The optional session object used to query the
            database. If omitted the MySQL Shell's current session will be used.
    
    """

    import mysqlsh
    shell = mysqlsh.globals.shell

    if session is None:
        session = shell.get_session()
        if session is None:
            print("No session specified. Either pass a session object to this "
                  "function or connect the shell to a database")
            return
    stmt = """select concat(sys.quote_identifier(user),'@',sys.quote_identifier(host))
              AS user, 
              password_last_changed,
              concat(
               cast(
              IFNULL(password_lifetime, @@default_password_lifetime) as signed)
              + cast(datediff(password_last_changed, now()) as signed), ' days') expires_in
              from mysql.user
              where 
              cast(
               IFNULL(password_lifetime, @@default_password_lifetime) as signed)
              + cast(datediff(password_last_changed, now()) as signed) BETWEEN 1 and {limit}
              and user not like 'mysql.%' order by user;""".format(limit=expire_in_days)

    result = session.run_sql(stmt)
    shell.dump_rows(result)
