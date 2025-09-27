from typing import Annoteated, Sequence, TypeDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from prompt_library.prompts import PROMPT_REGISTRY, PromptType
from retriver.retrival import Retriver
from utils.model_loader import ModelLoader
from langgraph.checkpoint.memory import MemorySaver


class AgenticRAG:
    class AgentState(Typedict):
        messages:Annotated[Sequence[BaseMessage], add_messages]

    def __init__(self):
        self.retriver_obj = Retriver()
        self.model_loader = ModelLoader()
        self.llm = self.model_Loader.load_llm()
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

        #-------Helpers--------
        def _format_docs(self, docs) -> str:
            if not docs:
                return "No relevant documents found."
            formatted_chunks = []
            for d in docs:
                meta =d.metadata or {}
                formatted = (
                    f"Title: {meta.get('product_title', 'N/A')}\n"
                    f"Price: {meta.get('price', 'N/A')}\n"
                    f"Rating: {meta.get('rating', 'N/A')}\n"
                    f"Reviews: \n{d.page_content.strip()}"
                )
                formatted_chunks.append(formatted)
            return "\n\n---\n\n".join(formatted_chunks)
        #-------Nodes--------
        def _ai_assistant(self, state:AgentState):
            print("--- CALL ASSISTANT ---")
            messages = state["messages"]
            last_message = messages[-1].content

            if any(word in last_message.lower() for word in ["price", "review", "product"]):
                return {"messages": [HumanMessage(content: "TOOL: Retriver")]}
            else:
                prompt = ChatPromptTemplate.from_template(
                    "You are a helpful assistant. Answer the user directly. \n\nQuestion: {question}\nAnswer:"
                )
                chain = prompt | self.llm | SterOutputParser()
                response = chain.invoke({"question": last_message})
                return {"messages": [HumanMessage(content: response)]}
            
        def _vector_retriver(self, state:AgentState):
            print("--- Retriver ---")
            query = state["messagee"][-1].content
            retriver = self.retriver_obj.Load_retriver()
            docs = retriver.invoke(query)
            context = self._format_docs(docs)
            return {"messages": [HumanMessage(contet: context)]}
        
        def _grade_documents(self, state: AgentState) -> Literal["genterator", "rewriter"]:
            print("--- GRADE DOCUMENTS ---")
            question = state["messages"][0].content
            docs = state["messages"][-1].content

            promt = PromptTemplate(
                template="""Your are a grager. Question : {question}\nDocs: {docs}\n
                Are docs relevant to the question? Answer yes or no.""",
                input_variables=["question", "docs"],
            )
            chain = prompt | self.llm | StrOutputParser()
            score = chain.invoke({"question": question, "docs": docs})
            return "generator" if "yes" in score.lower() else "rewriter"
        
        def _genrate(self, state: AgentState):
            print("--- GENERATOR ---")
            question = state["messages"][0].content
            docs = state["messages"][-1].content
            prompt = ChatPromptTemplate.from_template(
                PROMPT_REGISTRY[PromptTYpe.PRODUCT_BOT].template
            )
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke({"question": question, "context": docs})

        def _rewrite(self, state: AgentState):
            print("--- REWRITE ---")
            question = state["messages"][0].content
            new_q = self.llm.invoke(
                [HumanMessage(content=f"Rewrite the query to be clearer: {question}")]
            )
            

            
        