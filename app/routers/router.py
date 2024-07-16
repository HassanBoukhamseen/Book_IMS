from fastapi import FastAPI

app = FastAPI()

##DEFAULT 
#ADDED FUNCTION
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/books")
def get_books():
    return {"ALl": "Books"}

@app.get("/books/{book_id}")
def get_book():
    return {"Specific": "Book by ID"}

#@ADMIN ONLY
@app.post("/books")
def add_book():
    return {"add": "new book"}

#@ADMIN ONLY
@app.put("/books/{book_id}")
def update_book():
    return {"update": "existing book"}

#@ADMIN ONLY
@app.delete("/books/{book_id}")
def delete_book():
    return {"delete": "book"}

@app.get("/authors")
def get_authors():
    return {"retreive": "all authors"}

@app.get("/authors/{author_id}")
def get_author():
    return {"retreive": "author by id"}

#@ADMIN ONLY
@app.post("/authors")
def add_author():
    return {"add ": "new auhtor"}

#@ADMIN ONLY
@app.put("/authors/{author_id}")
def update_author():
    return {"add ": "new auhtor"}

#@ADMIN ONLY
@app.delete("/authors/{author_id}")
def delete_author():
    return {"delete": "author"}


@app.post("/users/register")
def add_user():
    return {"add": "user"}

#What's JWT? ADDED FUNCTION
@app.post("/users/login")
def auth_user():
    return {"auth": "user"}

@app.get("/users/me")
def get_user():
    return {"retreive": "authed user"}

@app.put("/users/me")
def update_user():
    return {"update": "authed user"}

@app.get("/recommendations")
def get_recommendations():
    return {"retreive": "recommendations for authed user prefs"}

@app.get("/healthcheck")
def health_check():
    return True



