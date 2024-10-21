import time
import threading
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate

template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer:
"""

# Initialize the model and prompt template
model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

class WaitingThread(threading.Thread):
    """Thread to display a waiting message with moving dots."""
    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        dots = 0
        while self._running:
            message = "Wait" + "." * dots
            print("\r" + message, end="")
            time.sleep(0.5)
            dots = (dots + 1) % 4  # Cycle through 0 to 3 dots

    def stop(self):
        self._running = False

def handle_conversation():
    context = ""  # Stores conversation history
    print("Welcome to the AI ChatBot! Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        try:
            # Start the waiting message in a separate thread
            waiting_thread = WaitingThread()
            waiting_thread.start()

            # Invoke the chain with context and user question
            result = chain.invoke({"context": context, "question": user_input})

            # Stop the waiting message
            waiting_thread.stop()
            waiting_thread.join()  # Ensure the thread has finished

            # Print the bot's response
            print("\rBOT:", result)  # Clear the waiting message line and show the result

            # Update the context with the new interaction
            context += f"\nUser: {user_input}\nAI: {result}"

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    handle_conversation()
