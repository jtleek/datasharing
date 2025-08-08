from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment
if "OPENAI_API_KEY" not in os.environ or not os.environ["OPENAI_API_KEY"].startswith("sk-"):
    print("WARNING: OPENAI_API_KEY not found or invalid. Please set it in backend/.env")

class PromptRequest(BaseModel):
    input: str
    prompt_name: str

class PromptResponse(BaseModel):
    response: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A dictionary of prompts
prompts = {
    "summarize": PromptTemplate(
        input_variables=["text"],
        template="Summarize the following text: {text}",
    ),
    "translate_to_french": PromptTemplate(
        input_variables=["text"],
        template="Translate the following text to French: {text}",
    ),
    "explain_code": PromptTemplate(
        input_variables=["code"],
        template="Explain the following code snippet: {code}",
    ),
}

llm = ChatOpenAI(temperature=0)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/invoke", response_model=PromptResponse)
async def invoke_prompt(request: PromptRequest):
    if request.prompt_name not in prompts:
        raise HTTPException(status_code=400, detail="Prompt not found")

    prompt = prompts[request.prompt_name]

    # The input variable name in the prompt template must match the key in the input dictionary.
    # We will use the first input variable in the list.
    input_key = prompt.input_variables[0]

    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        response = await chain.arun({input_key: request.input})
        return PromptResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
