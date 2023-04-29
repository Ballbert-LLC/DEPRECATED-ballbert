import sqlite3

con = sqlite3.connect("skills.db")

cur = con.cursor()

cur.execute("CREATE TABLE actions(skill, action_uuid, action_id, action_name, action_paramiters)")

cur.execute("CREATE TABLE installedSkills(skill, version)")