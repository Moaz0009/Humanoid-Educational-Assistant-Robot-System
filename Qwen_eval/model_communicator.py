import ollama

class QwenConversation:
    def __init__(self, model_name="prakasharyan/qwen-arabic"):
        self.model_name = model_name
        self.messages = []

    def send_message(self, prompt):
        try:
            self.messages.append({"role": "user", "content": prompt})
            response = ollama.chat(model=self.model_name, messages=self.messages)
            message_content = response['message']['content']
            self.messages.append({"role": "assistant", "content": message_content})

            return message_content
        except Exception as e:
            print(f"Error communicating with Ollama API: {e}")
            return "Error communicating with Ollama API"
    def reset_conversation(self):
        """Clear the conversation history."""
        self.messages = []


