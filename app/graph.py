"""Minimal LangGraph graph: a router picks the "knowledge" or "general" node.

Placeholder answers only, no LLM calls. The knowledge path will later call the
Java RAG API; this service never rebuilds RAG itself.
"""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

KNOWLEDGE_KEYWORDS = ("document", "documents", "pdf", "file", "upload", "knowledge")

Route = Literal["knowledge", "general"]


class GraphState(TypedDict, total=False):
    question: str
    route: Route
    answer: str


def router(state: GraphState) -> GraphState:
    words = state["question"].lower().split()
    is_knowledge = any(word.strip("?.,!") in KNOWLEDGE_KEYWORDS for word in words)
    return {"route": "knowledge" if is_knowledge else "general"}


def knowledge(state: GraphState) -> GraphState:
    return {
        "answer": "[knowledge] placeholder: this will be answered by the Java RAG API."
    }


def general(state: GraphState) -> GraphState:
    return {
        "answer": "[general] placeholder: this will be answered by the general assistant."
    }


def choose_route(state: GraphState) -> Route:
    return state["route"]


def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("router", router)
    graph.add_node("knowledge", knowledge)
    graph.add_node("general", general)
    graph.add_edge(START, "router")
    graph.add_conditional_edges(
        "router", choose_route, {"knowledge": "knowledge", "general": "general"}
    )
    graph.add_edge("knowledge", END)
    graph.add_edge("general", END)
    return graph.compile()


def run(question: str) -> GraphState:
    return build_graph().invoke({"question": question})
