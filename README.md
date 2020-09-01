# Mahdi Todo API
This is my implementation of a Todo API for the capstone project of the Udacity Fullstack Web Developer Nanodegree.

A live version of the API is deployed on Heroku and can be reached at this link:

[https://mahdi-todo.herokuapp.com]()

## Running the App
Running this app requires having a PostgreSQL database server running as well.

#### Running and Initializing the Database
To start a PostgreSQL database server locally using Docker with a database created for the app, run the following 
command with Docker installed:
```shell script
docker run -d --name mahdi-todo-db -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=mahdi_todo postgres:12
```

#### Starting the Backend Server 
##### Locally
To start the backend server you will need to have Python 3.8 installed. You will also need to 
have a PostgreSQL server running locally on port `5432` with a user named `postgres` and password `password`. 

Open a terminal and navigate to the root directory of this repository and do the following steps:

* Intall the dependencies:
```shell script
pip install -r requirements.txt
```

* Set required environment variables
```shell script
export AUTH0_DOMAIN='your-auth0-domain'
export AUTH0_API_AUDIENCE='you-auth0-api-id'
export AUTH0_SIGNING_ALGORITHM='RS256'
```

* Start the app server:
```shell script
FLASK_APP=app.py flask run
```
* If all went well then the server will be running at `http://localhost:5000`

##### With Docker
To start the backend server using Docker follow the steps:

* Build the Docker image:
```shell script
docker build . -t mahdi-todo:SNAPSHOT
```
* Run the Docker image:
```shell script
docker run -it --rm --name mahdi-todo \
    --link mahdi-todo-db:localhost \
    -p 5000:8000 \
    -e AUTH0_DOMAIN='your-auth0-domain' \
    -e AUTH0_API_AUDIENCE='you-auth0-api-id' \
    -e AUTH0_SIGNING_ALGORITHM='RS256' \
    mahdi-todo:SNAPSHOT
    
```
* If all went well then the server will be running at `http://localhost:5000`

This assumes that you have already started a PostgreSQL server using Docker with name `mahdi-todo-db` as in the steps 
above.


## Authorization Roles and Actions
These are the permissions defined in the system:
* `write:own-user`: Create and modify the user profile belonging to himself.
* `read:own-user`: Read his user profile.
* `write:own-todos`: Create and modify todos belonging to his user account.
* `read:own-todos`: Read the todos belonging to his user account.
* `read:all-users`: Read the user profiles of all user accounts in the system.

This app makes use of two roles for taking actions against the API:
* `User` Role
* `Manager` Role

A user with the `User` role can perform the following actions:
* `write:own-user`
* `read:own-user`
* `write:own-todos`
* `read:own-todos`

A user with the `Manager` role can perform the same actions that a `User` can in addition to the following:
* `read:all-users`

## Demo Credentials
Two user accounts are created for testing and demo purposes and can be used against the live deployment at the link
above:

#### Account with `User` Role
Email: user@example.com
Password: Hello123

#### Account with `Manager` Role
Email: manager@example.com
Password: Hello123

### Obtaining a JWT token
To use the demo accounts provided above and get a JWT you can visit the following link in your browser:

[https://mahdi-todo.us.auth0.com/authorize?audience=backend&response_type=token&client_id=OrlQaGgAAqRVlmiwMDQfxX4KTIutPNU0&redirect_uri=http://localhost:3000]()

Then enter the username and password and you will be redirected to an error page and the token will be available
in the address bar of the browser in the `access-token` query parameter.

## API Reference
The API documentation for this app is hosted using Postman at the link:

[https://documenter.getpostman.com/view/12466232/TVCb4VbS]()