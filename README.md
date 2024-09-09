
```markdown
# Image Recognition and Search API with OpenAI and Exa

This FastAPI application allows users to perform image recognition using OpenAI's API and search for related content on a provided website using Exa's API. Users can upload an image or provide a text query (or both) to search for relevant products or content on a specified website. The API also suggests follow-up questions based on the user's query and search results.

## Features

- **Image Recognition**: Upload an image, and the application will identify the product in the image using OpenAI's model.
- **Text Query Search**: Provide a search string to query content on a specified website using Exa's API.
- **Combined Search**: Use both image and text queries to refine the search.
- **Suggested Follow-up Questions**: The API suggests follow-up questions based on the user's query and the search results.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.9 or later installed on your machine (I found issues in exa python library in 3.8.. )
- `pip` package installer.
- OpenAI API key and Exa API key set in your environment.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/alinaqi/website-search.git
   cd image-recognition-api
   ```

2. **Create and Activate a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**:

   Set the OpenAI and Exa API keys in your environment:

   ```bash
   export OPENAI_API_KEY='your_openai_api_key_here'
   export EXA_API_KEY='your_exa_api_key_here'
   ```

   On Windows, use `set` instead of `export`:

   ```cmd
   set OPENAI_API_KEY=your_openai_api_key_here
   set EXA_API_KEY=your_exa_api_key_here
   ```

5. **Run the Application**:

   Start the FastAPI server using Uvicorn:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

   Replace `main` with the name of your Python file if it's different.

6. **Access the API**:

   Open your browser and go to `http://localhost:8000/docs` to access the interactive API documentation (Swagger UI).

## API Endpoints

### 1. `POST /search_website/`

This endpoint allows users to perform a search using either an image, a text query, or both.

- **Parameters**:
  - `file` (optional): An image file (PNG or JPEG).
  - `search_string` (optional): A text query to search for content.
  - `website` (required): The website to perform the search on.
  -`api_choice` : api to use exa.ai or perplexity.. default is exa

- **Example Request**:

  Using `curl`:

  ```bash
  curl -X POST "http://localhost:8000/search_website/" \
       -F "file=@path/to/your/image.jpg" \
       -F "search_string=what does zenloop do?" \
       -F "website=www.zenloop.com"
  ```

  Using Swagger UI, upload an image or enter a search string.

- **Response**:

  ```json
  {
    "results": [
      {
        "url": "https://example.com/product",
        "title": "Product Title",
        "text": "Description of the product",
        "highlights": "Highlighted content from the search",
        "summary": "Summary of the content"
      },
      ...
    ],
    "suggested_questions": {
      "suggested_questions": [
        "How do I sign up?",
        "What is the pricing?"
      ]
    }
  }
  ```

### 2. `GET /`

Health check endpoint to confirm the server is running.

- **Response**:

  ```json
  {
    "message": "Welcome to website search"
  }
  ```

## How It Works

1. **Image Processing**: If an image is uploaded, it is processed using OpenAI's GPT-4 model to identify the product in the image. The identified product information is then used to search on the provided website using Exa's API.

2. **Text Query Search**: If a text query (`search_string`) is provided, it is processed to determine the user's intent and to create an expanded search query. This query is then used to search for content on the provided website.

3. **Combined Search**: If both an image and text query are provided, both are processed, and a combined search query is created to refine the search results.

4. **Follow-up Question Suggestions**: Based on the user's query and search results, the application suggests follow-up questions to help the user find more relevant information.

## Contributing

To contribute to this project:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit and push your changes (`git commit -m 'Add new feature'`).
5. Create a pull request.

## License

No license, feel free to do whatever your heart desires :)

## Contact

If you have any questions, feel free to contact me. 

```
