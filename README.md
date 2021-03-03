# Marvel Impossible Challenge

NOTE: Please enter your public and private API keys in the Dockerfile.

The code is written in `python3`.

The Marvel API is used to gather this information. The `marvel.py` file in the `src/` folder has code to answer the questions in order. The `docker-compose.yml` file will spin up two containers. One for a `mySQL` database, and another to run the python script. There is a `wait-for-it.sh` script that will make the python app wait until the mySQL database is able to be pinged. Otherwise the python app errors out because it runs before the database exists. The script will print to stdout the answers to the challenge, and populate a table called `marvel.characters` in the mySQL database. The schema for the table can be seen in `db/init.sql` file.

Steps:
1. Have Docker on your machine.
2. In the directory of the `docker-compose.yml` file, run `docker-compose build` to build the image.
3. Run `docker-compose up` to spin up the containers. This will create the mySQL container, as well as run the python script.
4. To view the table contents, go into the mySQL docker container (explained in the next steps).
5. Run `docker ps` to list out all of your containers. Find the one that is named `marvel_db*`. Locate the container ID.
6. To shell into the container, run `docker exec -it <CONTAINER_ID> bash`.
7. Run `mysql -u root -p root` to log into mySQL
8. Set the database by running `use marvel`.
9. Query the table by running `select * from characters`.
10. Run other queries.

Few details:  
1. Because this runs in a Docker container, "showing" the image of a character is omitted, since it doesn't actually show anything. There is code that is commented that would actually show this interactively.
2. The `marvel.ipynb` can be loaded locally to run the code interactively through a Jupyter notebook on your machine (for a closer look). Just `pip install notebook`, and `pip install -r requirements.txt` before you do that.
3. Obviously this is a starting point and would need more resiliency if put into production.
