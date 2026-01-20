Do this to configured everything before running:

# PgAdmin > Select server 'PostGreSQL 17' > In DBs, create new DB called: PostOffice_DB

# In 'PostOffice\PostOffice\PostOffice_Proj\PostOffice_Proj\settings.py' : "PASSWORD": "postgres",
    Set your own server 'PostGreSQL 17' password

# PostOffice\PostOffice_Proj > run the commands:

    pip install django psycopg2-binary pymongo xhtml2pdf
    py manage.py makemigrations
    py manage.py migrate

# Inside PgAdmin query tool run DML script (PostOffice\populate_data.sql) to load data directly to the app

# Run
    py manage.py runserver

# Users to test from populate_data.sql:
Admin user: adminuser / password123
Client user: clientuser / password123
Driver user: driveruser / password123
Staff user: staffuser / password123
Manager user: manageruser / password123

