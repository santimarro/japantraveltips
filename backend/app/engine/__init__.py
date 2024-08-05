import os
from llama_index.core.settings import Settings
from llama_index.core.agent import AgentRunner
from llama_index.core.tools.query_engine import QueryEngineTool
from app.engine.index import get_index
from llama_index.core.tools import ToolMetadata
from llama_index.tools.wikipedia import WikipediaToolSpec
from llama_index.postprocessor.cohere_rerank import CohereRerank


cohere_rerank = None


def get_chat_engine(filters=None):
    # Reranker
    global cohere_rerank
    if not cohere_rerank:
        api_key = os.getenv("COHERE_API_KEY")
        top_k_ranked = os.getenv("TOP_K_RANKED", "3")
        cohere_rerank = CohereRerank(api_key=api_key, top_n=top_k_ranked)

    system_prompt = os.getenv("SYSTEM_PROMPT")
    top_k = os.getenv("TOP_K", "10")
    tools = []

    # Add query tool if index exists
    index = get_index()
    if index is not None:
        query_engine = index.as_query_engine(
            similarity_top_k=int(top_k),
            filters=filters,
            node_postprocessors=[cohere_rerank],
        )
        query_engine_tool = QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name="JapanTravelTips",
                description="Always use to find relevant advice, suggestions and any other non-historical information about Japan.",
            ),
        )
        tools.append(query_engine_tool)

    wikipedia_tool_spec = WikipediaToolSpec()
    tool_list = wikipedia_tool_spec.to_tool_list()
    # Add additional tools
    tools.extend(tool_list)

    return AgentRunner.from_llm(
        llm=Settings.llm,
        tools=tools,
        system_prompt=system_prompt,
        verbose=True,
    )
