import os
from llama_index.core.settings import Settings
from llama_index.core.agent import AgentRunner
from llama_index.core.tools.query_engine import QueryEngineTool
from app.engine.index import get_index
from llama_index.core.tools import ToolMetadata
from llama_index.tools.wikipedia import WikipediaToolSpec

def get_chat_engine(filters=None):
    system_prompt = os.getenv("SYSTEM_PROMPT")
    top_k = os.getenv("TOP_K", "3")
    tools = []

    # Add query tool if index exists
    index = get_index()
    if index is not None:
        query_engine = index.as_query_engine(
            similarity_top_k=int(top_k), filters=filters
        )
        query_engine_tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name="JapanTravelTips",
                    description="Search for posts as they appear in JapanTravelTips",
                ))
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
