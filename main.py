from dotenv import load_dotenv,dotenv_values
import os

# Provide the relative path to the .env file
load_dotenv()
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

# Ensure the API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY not found in environment variables")


