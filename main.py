from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Union
from PIL import Image
import io
import base64
import openai
import os
import requests
import json
from exa_py import Exa
from typing import List, Dict 

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
exa = Exa(api_key=os.getenv("EXA_API_KEY"))

app = FastAPI(title="Image recognition APIs", description="APIs for image recognition using OpenAI and agents", version="0.1")

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to encode the image
def encode_image(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')

prompt_for_products = """
"Identify in the image the product and return it in the JSON format: {'product': 'product_name', 'product_type': 'type_of_product', 'product_color': 'color of product', 'price_category':'price category of product'}. If no product is present, please return {'product': 'no product found'}"}"
"""

@app.post("/search_website/")
async def search_website(
    file: Optional[Union[UploadFile, str]] = File(None),
    search_string: Optional[str] = Form(None),
    website: str = Form(...)
):
    print("Website:", website)
    if not file and not search_string:
        raise HTTPException(status_code=400, detail="You must provide either an image or a search string.")

    # Initialize the combined search input
    combined_search_input = ""

    # If image is provided, process the image
    if file and file.filename:

        try:
            if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
                raise HTTPException(status_code=400, detail="Invalid file type. Only PNG and JPEG images are supported.")


            print("Loading image:", file.filename)
            image = Image.open(io.BytesIO(await file.read()))

            # Encode the image to base64
            base64_image = encode_image(image)

            # Prepare the payload for OpenAI API
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_for_products},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ]
            }

            # Make the request to OpenAI API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai.api_key}",
            }
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            # Handle the response
            if response.status_code == 200:
                result = response.json().get("choices")[0].get("message").get("content")
                print("OpenAI API Response:", result)
                
                # Parse the result to remove any surrounding ```json and ```
                result_dict = eval(result.strip("```json").strip("```").strip())

                # Add the generated search input from the image
                combined_search_input += f"Find similar products as given in the following json: {result_dict}"

            else:
                print("Error from OpenAI API:", response.status_code, response.text)
                return JSONResponse(content={"error": response.text}, status_code=response.status_code)

        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=400)

    # If search string is provided, add it to the combined search input
    if search_string:
        get_intent_response = await get_intent(search_string, website)
        if combined_search_input:
            # Combine the search strings if both image and text are provided
            combined_search_input += f" AND {get_intent_response}"
        else:
            # Use only the search string if no image was processed
            combined_search_input = get_intent_response

    # Make the request to Exa API to find similar products
    try:
        exa_result = exa.search_and_contents(
            combined_search_input,
            type="auto",
            num_results=3,
            text=True,
            include_domains=[website]
        )

        print("Result from Exa API:", exa_result)

        # Access the "results" attribute directly and convert to JSON-serializable format
        results_only = [
            {
                "url": res.url,
                "title": res.title,
                "text": res.text,
                "highlights": res.highlights,
                "summary": res.summary
            }
            for res in exa_result.results  # Assuming exa_result.results is a list of Result objects
        ]

        suggested_questions_response = await suggest_questions(search_string, results_only)

        # Return only the "results" as a JSON response
        return JSONResponse(content={"results": results_only, "suggested_questions": suggested_questions_response}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

intent_prompt = """
Given the user query, and the provided website as context, convert to json with user's intent in a structured way as specified. 
Do not add any additional information as the user query json will be used to run the search query.


Return it as following json:

{
  "intent": <intent e.g. search_for_contact, potential_customer, potential_employee, etc.>,
  "query": <actual user query>,
  "expanded_query": <expand and clarify user query if needed ie if user query is ambiguous>
}

"""
async def get_intent(query: str, website: str):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        response_format= { "type": "json_object"},
        messages=[
            {
                "role": "system", "content": intent_prompt,
                "role": "user", "content": f"User query: {query}. Provided website as context: {website} \n Return as JSON object."
            }
        ]
    )
    print("Intent response:", response.choices[0].message.content)
    intent = response.choices[0].message.content

    return intent

suggest_questions_prompt = """
Given user's query and the search results, suggest next questions a user can ask to get more information. 
The next questions will be used to suggest to users what are follow up questions they can ask:
e.g 
What is zenloop?
Suggested questions would be:
How do i sign up?
What is pricing?
etc.

Return it as json as follows:

{
  "suggested_questions": [
    <related question to original query 1>,
    <related question to original query 2>,
    <related question to original query 3>"
  ]
}
"""
async def suggest_questions(query: List[Dict], search_results: List[Dict]):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        response_format= { "type": "json_object"},
        messages=[
            {
                "role": "system", "content": suggest_questions_prompt,
                "role": "user", "content": f"Original user query: {query}. \n Search results: {search_results} \n Suggest follow up questions as JSON object."
            }
        ]
    )
    print("Suggested questions:", response.choices[0].message.content)
    intent = response.choices[0].message.content

    return intent



@app.get("/")
async def read_main():
    return {"message": "Welcome to website search"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)