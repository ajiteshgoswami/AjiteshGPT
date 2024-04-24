# HariGPT - Harikrishna's Resume Bot

## Overview

This Streamlit application serves as a chatbot, providing information about Harikrishna (Harry) Dev's professional background and qualifications. The chatbot is powered by large language models and can answer questions based on the provided context, which includes Harikrishna's resume and additional data.

## Features

- Provides information about Harikrishna's educational background, professional experience, and skills
- Allows users to ask questions and receive relevant responses
- Stores conversation history in a Cloud Firebase database for further analysis
- Supports both CSV and PDF (resume) data sources

## Link

Resume Bot Wesbite : [harikrishnad1997-resume-bot.hf.space](https://harikrishnad1997-resume-bot.hf.space/)

## Demo

![1713819389962](assets/demo.gif)

## Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Cloud Firebase project

## Installation

1. Clone the repository:

```
git clone https://github.com/harikrishnad1997/HariGPT.git && cd HariGPT
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Set up the environment variables:

   - Create a `.toml file with the OPENAI key inputted `
   - Save your Firebase JSON key in the `.streamlit/` folder

## Usage

1. Run the Streamlit application:

```
streamlit run app.py
```

2. The application will open in your default web browser.
3. Ask questions about Harikrishna's background and qualifications, and the chatbot will provide relevant responses.

## Configuration

- The application uses a FAISS index to store the CSV and PDF data embeddings. If the index file (`faiss_index`) does not exist, it will be created automatically.
- The CSV data file path is set in the `data_source` variable, and the PDF resume file path is set in the `pdf_source` variable.
- The MongoDB connection details are set using the environment variables `mongodB_pass` and the `uri` variable.

## Acknowledgements

This project is highly influence by the Repository created by [Art Kreimer](https://github.com/kredar) and is dependent on the following libraries and tools:

- [Streamlit](https://streamlit.io/) for building the web application
- [LangChain](https://langchain.com/) for integrating the language model and retrieval chain
- [OpenAI API](https://openai.com/) for the language model
- [FAISS](https://github.com/facebookresearch/faiss) for the vector database
- [Firebase](https://firebase.google.com/) for storing the conversation history

## License

This project is licensed under the [MIT License](LICENSE).
