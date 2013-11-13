* Install the heroku toolchain
* Install `postgres.app`

**psql:**

    CREATE DATABASE todo

**shell:**

    export DATABASE_URL=postgres://postgres@localhost/todo
    python ./manage.py syncdb --noinput
    foreman start
