QUERY_ROUTER_PROMPT = """
You are a Query Router Agent.
Your task is to read the user's query and reply with only one agent name based on the intent.

Rules:
1. If the user query is about math operations (calculation, equation, arithmetic, numbers) → reply "math"
2. If the user query is about getting information, explanation, facts, or knowledge → reply "knowledge"
3. If the user wants to book a ground / playground / turf / ground reservation → reply "ground"
4. For any other request, reply exactly: "out of my known"

Strict instructions:
- Reply with only one word.
- Do not answer the user query.
- Do not add punctuation or extra text.
- Allowed outputs only: math, knowledge, ground, out of my known

your query :-{query}
"""
from sqlalchemy import true
from knolege_agent import llm,rag_chain
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from typing import TypedDict
from ground_book import update_booking_state,ground_book_graph,config,checkpointer
from langgraph.types import interrupt, Command

@tool
def math_tool(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

class InitailStateState(TypedDict):
    query: str
    responce:str
    ans:str
    
    
def inital_chat(state:InitailStateState):
  
    query=state["query"]
    QUERY_ROUTER_PROMPT =f"""
    You are a Query Router Agent.
    Your task is to read the user's query and reply with only one agent name based on the intent.

    Rules:
    1. If the user query is about math operations (calculation, equation, arithmetic, numbers) → reply "math"
    2. If the user query is about getting information, explanation, facts, or knowledge → reply "knowledge"
    3. If the user wants to book a ground / playground / turf / ground reservation → reply "ground"
    4. For any other request, reply exactly: "out_of_my_known"

    Strict instructions:
    - Reply with only one word.
    - Do not answer the user query.
    - Do not add punctuation or extra text.
    - Allowed outputs only: math, knowledge, ground, out_of_my_known

    your query :- {query}
    """
    route=llm.invoke(QUERY_ROUTER_PROMPT).content.strip()
    
    return route
llm_with_tools = llm.bind_tools([math_tool])


def math(state:InitailStateState):

    query = state["query"]

    llm_with_tools = llm.bind_tools([math_tool])
    ai_msg = llm_with_tools.invoke(query)

    # Tool calling case
    if ai_msg.tool_calls:
        tool_call = ai_msg.tool_calls[0]

        tool_result = math_tool.invoke(tool_call["args"])

        return {
            "responce": str(tool_result["result"])
        }

    # Fallback
    return {
        "responce": ai_msg.content
    }

def knowledge(state:InitailStateState):
    query=state["query"]
    # Make the LLM tool-aware
    responce=rag_chain.invoke(query)
    state["responce"]=responce
    return state

def out_of_my_known(state:InitailStateState):
    
    #state["responce"]="out of know"
    query=state["query"]
    # Make the LLM tool-aware
    responce=rag_chain.invoke(query)
    state["responce"]=responce
    return state



def ground(state: InitailStateState):
    booking = {"user_id":"123"}

    st = update_booking_state(state["query"], booking)
    kt = ground_book_graph.invoke(st)

    booking={
        "user_id":"123",
        "date": kt.get("date"),
        "start_time": kt.get("start_time"),
        "end_time": kt.get("end_time")
    }

    while True:
        human_answer = interrupt({
            "type": "ans",
            "question": f"Please provide data for {booking}"
        })

        st = update_booking_state(human_answer, booking)
        kt = ground_book_graph.invoke(st)

        booking={
            "user_id":"123",
            "date": kt.get("date"),
            "start_time": kt.get("start_time"),
            "end_time": kt.get("end_time")
        }

        if kt.get("status"):
            state["responce"] = kt["status"]
            break

    state["booking"] = booking
    return state



initail_graph=StateGraph(InitailStateState)
# initail_graph.add_node("inital_chat",inital_chat)
initail_graph.add_node("math",math)
initail_graph.add_node("knowledge",knowledge)
initail_graph.add_node("out_of_my_known",out_of_my_known)
initail_graph.add_node("ground",ground)

initail_graph.add_conditional_edges(START,inital_chat,{
        "math": "math",
        "knowledge": "knowledge",
        "out_of_my_known":"out_of_my_known",
        "ground":"ground"
    })
initail_graph.add_edge("math",END)
initail_graph.add_edge("knowledge",END)
initail_graph.add_edge("out_of_my_known",END)
initail_graph.add_edge("ground",END)
app=initail_graph.compile(checkpointer=checkpointer)

def process_response(response):
    """Extract interrupt question, show it, and collect human input."""
    if "__interrupt__" not in response:
        return None

    intr = response["__interrupt__"][0]
    question = intr.value.get("question", "No question provided.")

    print("\n🤖 BOT:", question)
    user_input = input("👤 USER: ")
    return user_input

if __name__ == "__main__":
    while True:
        user_input = input("enter user input :- ")
        if user_input == "quit":
            break
        # First invoke
        result = app.invoke({
            "query": user_input, 
            "responce": "", 
            "ans": ""
        }, config=config)
        
        # Human-in-the-loop loop
        while "__interrupt__" in result:
            user_input = process_response(result)
            if user_input=="quit":
                break
            result = app.invoke(Command(resume=user_input), config=config)
        print("\n✅ Finished conversation.")
        print("Final state:", result)

   

    