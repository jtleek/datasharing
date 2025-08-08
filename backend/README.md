# Backend for AI Prompt Invocation

This is a FastAPI-based backend that allows you to invoke AI prompts asynchronously.

## Setup

1.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set your OpenAI API key:**
    -   Open `backend/.env` and replace `"your-openai-api-key"` with your actual OpenAI API key.

## Running the server

To run the server, navigate to the `backend` directory and run the following command:
```bash
uvicorn main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

## API

### POST /invoke

This endpoint allows you to invoke a prompt with a given input.

**Request Body:**
```json
{
  "input": "Your input text here",
  "prompt_name": "name_of_the_prompt"
}
```

**Available `prompt_name` values:**
- `summarize`
- `translate_to_french`
- `explain_code`

**Response Body:**
```json
{
  "response": "The AI-generated response"
}
```

**Example using `curl`:**
```bash
curl -X POST "http://127.0.0.1:8000/invoke" \
-H "Content-Type: application/json" \
-d '{
  "input": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.",
  "prompt_name": "summarize"
}'
```
