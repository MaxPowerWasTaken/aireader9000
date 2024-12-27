import re

from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam
from pydantic import BaseModel, Field, field_validator

from schemas import RetrievedDocChunk

#class QuotedSection(BaseModel):
#    quote_and_pgnum: str = Field(..., description="A relevant quote from the source text")

class Reader9000Response(BaseModel):
    content: str = Field(
        ..., 
        description="""A cohesive narrative response that naturally incorporates quoted material 
                   using phrases like 'According to...', 'As stated in...', etc. 
                   Quotes should be wrapped in "" quotation marks and followed by the quoted 
                   DocumentChunk's pg_num_0idx attribute in square brackets, like this: 
                   "According to personA, the reason X happened was Y" [page: pg_num_0idx]."""
    )

    @field_validator('content')
    def validate_quote_format(cls, v):
        pattern = r'(\".*?\")\s*\[page:\s*(\d+)\]'
        if not re.search(pattern, v):
            raise ValueError("Response must contain >=1 properly formatted quote with page number")
        return v
    
    # BUG: NEED ANOTEHR VALIDATOR THAT THE QUOTE IS ACTUALLY A SUBSTRING OF THE SOURCE


def generate_response(
    query: str, 
    context_passages: list[RetrievedDocChunk],
    llm_name: str = "gpt-4o-mini",
    temperature: float = 0.0,
) -> str:
    """
    Generate a response using the provided LLM based on the query and retrieved context.
    
    Parameters
    ----------
    query : str
        The user's original question
    context_passages : List[Dict[str, Any]]
        Retrieved and reranked passages from the vector database
    model : GenerativeModel
        The Gemini model instance to use for generation
        
    Returns
    -------
    str
        The generated response
    """
    # Prepare the context from retrieved passages
    print(context_passages)
    context = "\n\n".join([f"""page-number: {c.pg_num_0idx+1}
                            relevance_score: {c.relevance_score}
                            text: {c.text}
                            """
                          for c in context_passages])
    
    prompt = f"""You are a thoughtful research assistant, providing answers to questions based on 
    insightful reviews of source material, and you cite specific passages that back up your claims.

    Below, I will present you with a question, followed by a list of source materials as
    context. The code/schema that defines the source materials is as follows:

    context =   page-number: c.pg_num_0idx+1
                relevance_score: c.relevance_score
                text: c.text  
        ... for c in most_relevant_document_chunks

    The 'relevance_score' in particular is very reliable (higher scores are more relevant); 
    if a particular source material passage has a significantly higher/lower relevance score 
    than others, please increase/decrease your focus on it in your answer accordingly

    It is very important to formulate your answer to utilize direct quote(s) from one or (ideally) 
    more of the source materials. After a direct quote, include a citation like 
    "[page: _page-number_]" to the source material. For brevity, direct quotes can
    omit unnecessary words with ellipsis ('...'), between two (or more) key substrings
    from a source material passage.

    Below is the QUESTION and SOURCE MATERIALS, as described above:
    ---------------------------------------------
    QUESTION: {query}

    SOURCE MATERIALS:
    {context}
    """
    messages = [ChatCompletionUserMessageParam(content=prompt, role='user')]
    client = OpenAI()
    response = client.beta.chat.completions.parse(
        model=llm_name,
        messages=messages,
        temperature=temperature,
        response_format=Reader9000Response
    )
    
    final_response = response.choices[0].message.parsed.content  # type: ignore

    return final_response