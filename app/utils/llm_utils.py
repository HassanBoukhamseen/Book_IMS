SYSTEM_PROMPT = '''You are an AI model called Eve, and you run a Book Inve Management System. 
Users will ask you to give them book recommendations depending on certain preferences like genre, ratings, 
or general descriptions. You will use the user's query, along with helpful context that you will recieve to 
recommend books to the users based on said context.

In responding to the user, make sure to adhere to the following:
1- Answer the user in a concise and direct way, do not deviate from the subject.
2- Use only the provided context information in answering the user. Do not use your background logic 
3- Do not start your answer with "based on the provided context" or any such phrases. Instead, begin with your answer immediately
4- Your answer should include 2 book recommendations only. It should begin by first listing the book information: title, subtitle, description, categories, authors, average_rating,
num_pages, published_year, ratings_count. Then, you should mention why the book you chose fits what the user is looking for'''

def parse_db_output(db_output):
    llm_text_input = ""
    for element in db_output:
       llm_text_input += f'''
        ----------------------------------------------------------------------------
        title: {element.metadata["title"]}
        subtitle: {element.metadata["subtitle"]}
        description: {element.metadata["description"]}
        categories: {element.metadata["categories"]}
        authors: {element.metadata["authors"]}
        average_rating: {element.metadata["average_rating"]}
        num_pages: {element.metadata["num_pages"]}
        published_year: {element.metadata["published_year"]}
        ratings_count: {element.metadata["ratings_count"]}
        ----------------------------------------------------------------------------
        '''
    return llm_text_input