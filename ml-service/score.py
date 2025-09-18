# Inside score.py or new function in train_embed_index.py

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
llm = genai.GenerativeModel('gemini-1.5-flash')

def generate_answer(question, context_chunks):
    context = "\n".join(context_chunks)
    prompt = f"""
    Answer based ONLY on context below. Say 'I don't know' if unsure.

    Context:
    {context}

    Question: {question}
    """
    response = llm.generate_content(prompt)
    return response.text