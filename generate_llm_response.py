from typing import List, Tuple

from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam
from pydantic import BaseModel, Field

from schemas import RetrievedDocChunk


class QuotedSection(BaseModel):
    quote: str = Field(..., description="A relevant quote from the source text")
    section_title: str = Field(..., description="The section title where this quote was found")

class NarrativeResponse(BaseModel):
    content: str = Field(
        ..., 
        description="""A cohesive narrative response that naturally incorporates quoted material 
                   using phrases like 'According to...', 'As stated in...', etc. Quotes should be 
                   wrapped in quotation marks and followed by section references in parentheses."""
    )
    quotes: List[QuotedSection] = Field(
        ..., 
        description="List of all quotes used in the narrative, in order of appearance"
    )

def generate_response(
    query: str, 
    context_passages: list[RetrievedDocChunk],
    llm_name: str = "gpt-4o-mini",
    temperature: float = 0.0,
) -> Tuple[str, str]:
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
        response_format=NarrativeResponse
    )

    final_response = response.choices[0].message.parsed.content  # type: ignore

    return (final_response, prompt)