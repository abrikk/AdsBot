# Bot that helps create an advertisement for the purchase and sale of goods or services in a channel
The bot was created as an order for people from Mariupol.

### Used technologies
* Python 3.10;
* aiogram v2.21 (Telegram Bot framework);
* aiogram-dialog v1.8.0 (GUI framework for telegram bot);
* Docker and Docker Compose (containerization);
* PostgreSQL (database);
* SQLAlchemy v1.4.39 (working with database from Python);
* Alembic v1.8.0 (database migrations made easy);

### Project deployment in 3 steps:
1. Clone the repository:
    `git clone git@github.com:abrikk/AdsBot.git`
2. Copy `.env.dist` to `.env` and fill in the values
3. Up bot and environment by running:
    `docker compose up --build`

### How to restore data in case of data loss:
1. Unpack the backup file into folder where backup was made.
2. Enter the shell with the database `docker compose exec --tty --interactive db /bin/sh`
3. Set user `export PGUSER=DB_USER`
4. Drop database `psql template1 -c 'drop database DB_NAME;'`
5. Create database `psql template1 -c 'create database DB_NAME with owner DB_USER;'`
6. Fill data into database from unpacked dump `psql DB_NAME < backups/daily/unpacked_backup_file.sql`