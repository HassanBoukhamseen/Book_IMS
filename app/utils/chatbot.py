from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from app.utils.recommendations import get_recommended_books, format_recommended_books


template = """
Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# Custom callback handler for streaming responses
class MyCustomHandler(BaseCallbackHandler):
    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.tokens.append(token)

# Function to get or create session history
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# In-memory store for session histories
store = {}

# Initialize the OllamaLLM with the Mistral model
callback_manager = CallbackManager([MyCustomHandler()])

model = OllamaLLM(model="llama3.1:8b", callbacks=callback_manager, temperature=0.2)

# Create a chain that processes the prompt through the model
chain = prompt | model

# Create a RunnableWithMessageHistory instance
with_message_history = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history
)

def get_combined_query(user_input):
    # Get book recommendations
    recommended_books = get_recommended_books(user_input)
    books_str = format_recommended_books(recommended_books)
    # Combine user input with recommended books
    combined_query = f"""
        You are a highly knowledgeable and specialized book recommendation assistant. Your primary function is to recommend books based on the provided list. You should only answer questions that are directly related to books and book recommendations. If a user asks a general question or a question not related to books, politely redirect them to ask about books. When recommending books, ensure each book is structured in a readable and detailed format. Avoid making up information that is not provided in the list.

        Here are your instructions:
        1. **Focus on Books**: Only answer questions about books. If the user's question is not about books, kindly remind them that you can only provide book recommendations.
        2. **Structured Responses**: When providing book recommendations, follow this structure for each book:
        - **Title**: [Book Title]
        - **Author**: [Author Name]
        - **Description**: [A brief description of the book]
        - **Categories**: [Categories or genres the book falls into]
        - **Year**: [Year of publication]
        - **Score**: [Relevance score or rating]
        3. **Use Provided Information Only**: Do not generate content that is not based on the provided list of books. If the necessary information is not available, simply state that the information is not available.
        4. **Friendly Tone**: Maintain a friendly and helpful tone throughout the conversation.

        If the user's question does not relate to books, respond with:
        "I am here to help with book recommendations. Please ask me about books you are interested in, and I will provide you with suitable suggestions."

        User's Question: {user_input}

        Recommended Books (CONTEXT):

        {books_str}

        Answer:
        """
    return combined_query

# Function to process user input and get response
def get_response(user_input, session_id="1"):
    config = {"configurable": {"session_id": session_id}}
    handler = MyCustomHandler()
    callback_manager = CallbackManager([handler])
    model.callbacks = callback_manager
    with_message_history.invoke(
        [HumanMessage(content=user_input)],
        config=config,
    )
    return handler.tokens


