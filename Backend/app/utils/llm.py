import time
from langchain_core.messages import trim_messages
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from operator import itemgetter
from app.utils.llm_utils import SYSTEM_PROMPT, parse_db_output
from langchain_ollama import OllamaLLM
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager

from app.utils.vector_store import base_retriever
from langchain_core.messages import HumanMessage


class StreamingGeneratorCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str, *, chunk= None, run_id, parent_run_id = None, **kwargs):
        self.tokens.append(token)

callback_handler = StreamingGeneratorCallbackHandler()
callback_manager = CallbackManager([callback_handler])

model = OllamaLLM(model="llama3.1:8b", num_thread=16, callback_manager=callback_manager)

store = {}

def get_session_history(session_id:str) -> BaseChatMessageHistory:
    if session_id not in store.keys():
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chat_with_history = RunnableWithMessageHistory(model, get_session_history)

# parser = StrOutputParser()

config = {"configurable": {"session_id": "abc11"}}

prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), MessagesPlaceholder(variable_name="human_messages")]
)

trimmer = trim_messages(
    max_tokens=300,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=True,
    start_on="human"
)

chain = (RunnablePassthrough.assign(messages=itemgetter("human_messages") | trimmer) | prompt| model)

with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="human_messages",
)

def get_llm_response(query):
    message_with_context = query + f" Here is some context: {parse_db_output(base_retriever.invoke(query))}"
    model_input = {"human_messages": [HumanMessage(content=message_with_context)]}
    output = with_message_history.invoke(model_input, config=config)
    return stream_response(callback_handler.tokens)

def stream_response(response_tokens):
    for response in response_tokens:
        time.sleep(0.1)
        yield response


if __name__ == "__main__":
    print(with_message_history.invoke({"human_messages": "Hi"}, config=config))