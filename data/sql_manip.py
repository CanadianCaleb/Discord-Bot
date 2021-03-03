import sqlite3

class roles():
    def __init__(self):
        pass
    
    async def create_roles_table(self):
        conn = sqlite3.connect('rolestorage.db')
        c = conn.cursor()
        c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='roles';")
        if c.fetchone()[0] == 0:
            c.execute("CREATE TABLE roles (id text,role_ids text)")
        conn.commit()
        conn.close()

    async def gen_roles(self, message):
        conn = sqlite3.connect('rolestorage.db')
        c = conn.cursor()
        for user in message.guild.members:
            if not user.bot:
                c.execute("INSERT INTO roles (id, role_ids) VALUES ('{}', '{}')".format(user.id, [i.id for i in user.roles if i.name!='@everyone']))
        conn.commit()
        conn.close()
    
    async def update_roles(self, member):
        try:
            conn = sqlite3.connect('rolestorage.db')
            c = conn.cursor()
            c.execute("SELECT * FROM roles WHERE id IS '{}'".fomat(member.id))
            x = str(c.fetchone())
            if len(x) > 0:
                c.execute("DELETE FROM roles WHERE id IS '{}'".format(member.id))
                c.execute("INSERT INTO roles (id, role_ids) VALUES ('{}', '{}')".format(member.id, [i.id for i in member.roles if i.name!='@everyone']))
            else:
                c.execute("INSERT INTO roles (id, role_ids) VALUES ('{}', '{}')".format(member.id, [i.id for i in member.roles if i.name!='@everyone']))
        except sqlite3.OperationalError as x:
            print(f"SQL error : {x}")
