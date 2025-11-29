Do this to setup everything to run as configured:

Open PgAdmin > Select server 'PostGreSQL 17' > In Databases, create new DB called: PostOffice_DB
cd PostOffice\PostOffice_Proj > run the commands:
    py manage.py makemigrations
    py manage.py migrate
Run DML script(PostOffice\populate_data.sql) inside PgAdmin query tool to load data directly to the app
Then try it
    py manage.py runserver