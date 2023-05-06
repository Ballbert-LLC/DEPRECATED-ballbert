import weaviate
import json
import sqlite3

# Open a connection to the database file
conn = sqlite3.connect('skills.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Execute a SELECT query on the actions table
cursor.execute('SELECT * FROM actions')

# Fetch all the rows returned by the query
actions_data = cursor.fetchall()

# Execute a SELECT query on the installedSkills table
cursor.execute('SELECT * FROM installedSkills')

# Fetch all the rows returned by the query
installed_skills_data = cursor.fetchall()

# Execute a SELECT query on the installedSkills table
cursor.execute('SELECT * FROM requirements')

# Fetch all the rows returned by the query
required_data = cursor.fetchall()

# Close the cursor and the database connection
cursor.close()
conn.close()

# Create a Weaviate client object
client = weaviate.Client("http://localhost:8080")

# Retrieve all the data stored in the Weaviate database
data = client.data_object.get()

# Print the data from the actions and installedSkills tables
print("Data from actions table:")
for row in actions_data:
    print(row)

print("Data from installedSkills table:")
for row in installed_skills_data:
    print(row)

print("Data from requirements table:")
for row in required_data:
    print(row)

# Print out the data
print("Data from vector database:")
clean = []
for item in data["objects"]:
    clean.append(item["properties"])
print(json.dumps(clean, indent=2))
