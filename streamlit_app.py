import streamlit as st
import psutil
import time
from graph import app, config, process_response
from langgraph.types import Command

# Page config
st.set_page_config(
    page_title="AI Assistant - Math, Knowledge & Booking",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "waiting_for_input" not in st.session_state:
    st.session_state.waiting_for_input = False
if "interrupt_question" not in st.session_state:
    st.session_state.interrupt_question = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"streamlit-{int(time.time())}"
if "booking_state" not in st.session_state:
    st.session_state.booking_state = {
        "user_id": "",
        "start_time": "",
        "end_time": "",
        "date": ""
    }

# Update config with session thread_id
config["configurable"]["thread_id"] = st.session_state.thread_id


def get_machine_resources():
    """Get current machine resource usage."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_used_gb": memory.used / (1024**3),
        "memory_total_gb": memory.total / (1024**3),
        "disk_percent": disk.percent,
        "disk_used_gb": disk.used / (1024**3),
        "disk_total_gb": disk.total / (1024**3)
    }


def process_graph_response(result):
    """Process graph response and handle interrupts."""
    if "__interrupt__" in result:
        intr = result["__interrupt__"][0]
        question = intr.value.get("question", "No question provided.")
        st.session_state.interrupt_question = question
        st.session_state.waiting_for_input = True
        return None
    else:
        st.session_state.waiting_for_input = False
        st.session_state.interrupt_question = None
        return result.get("responce", "No response")


# Sidebar for machine resources
with st.sidebar:
    st.header("🖥️ Machine Resources")
    
    resources = get_machine_resources()
    
    st.metric("CPU Usage", f"{resources['cpu_percent']:.1f}%")
    
    st.progress(resources['cpu_percent'] / 100)
    
    st.metric("Memory Usage", f"{resources['memory_percent']:.1f}%")
    st.caption(f"{resources['memory_used_gb']:.2f} GB / {resources['memory_total_gb']:.2f} GB")
    st.progress(resources['memory_percent'] / 100)
    
    st.metric("Disk Usage", f"{resources['disk_percent']:.1f}%")
    st.caption(f"{resources['disk_used_gb']:.2f} GB / {resources['disk_total_gb']:.2f} GB")
    st.progress(resources['disk_percent'] / 100)
    
    st.divider()
    
    if st.button("🔄 Refresh Resources"):
        st.rerun()
    
    st.divider()
    
    if st.button("🗑️ Clear History"):
        st.session_state.conversation_history = []
        st.session_state.current_result = None
        st.session_state.waiting_for_input = False
        st.session_state.interrupt_question = None
        st.session_state.thread_id = f"streamlit-{int(time.time())}"
        config["configurable"]["thread_id"] = st.session_state.thread_id
        st.rerun()


# Main content area
st.title("🤖 AI Assistant")
st.markdown("**Ask me about Math, Knowledge, or Book a Ground!**")

# Display conversation history
if st.session_state.conversation_history:
    st.subheader("💬 Conversation History")
    for i, (role, message) in enumerate(st.session_state.conversation_history):
        if role == "user":
            with st.chat_message("user"):
                st.write(message)
        else:
            with st.chat_message("assistant"):
                st.write(message)
    
    st.divider()

# Handle interrupt question
if st.session_state.waiting_for_input and st.session_state.interrupt_question:
    st.warning("⚠️ **Bot needs your input:**")
    st.info(st.session_state.interrupt_question)
    
    user_response = st.text_input(
        "Your response:",
        key="interrupt_input",
        placeholder="Type your answer here..."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Submit Response", type="primary"):
            if user_response:
                # Resume the graph with user input
                try:
                    result = app.invoke(
                        Command(resume=user_response),
                        config=config
                    )
                    st.session_state.current_result = result
                    
                    # Add interrupt question and response to history
                    st.session_state.conversation_history.append(
                        ("assistant", f"❓ {st.session_state.interrupt_question}")
                    )
                    st.session_state.conversation_history.append(
                        ("user", user_response)
                    )
                    
                    # Process the result
                    response = process_graph_response(result)
                    if response:
                        st.session_state.conversation_history.append(
                            ("assistant", f"✅ {response}")
                        )
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.waiting_for_input = False
            st.session_state.interrupt_question = None
            st.rerun()

# Main input form
if not st.session_state.waiting_for_input:
    with st.form("user_query_form", clear_on_submit=True):
        user_query = st.text_input(
            "Enter your query:",
            placeholder="e.g., 'What is 5 + 3?', 'Tell me about MacBook', 'Book a ground for tomorrow 2pm'",
            key="query_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.form_submit_button("🚀 Send", type="primary")
        
        if submit_button and user_query:
            # Add user query to history
            st.session_state.conversation_history.append(("user", user_query))
            
            # Prepare initial state
            initial_state = {
                "query": user_query,
                "responce": "",
                "ans": "",
                "booking": st.session_state.booking_state.copy()
            }
            
            # Invoke the graph
            with st.spinner("🤔 Processing your query..."):
                try:
                    result = app.invoke(initial_state, config=config)
                    st.session_state.current_result = result
                    
                    # Process the result
                    response = process_graph_response(result)
                    
                    if response:
                        st.session_state.conversation_history.append(
                            ("assistant", f"✅ {response}")
                        )
                        # Update booking state if it exists
                        if "booking" in result:
                            st.session_state.booking_state.update(result["booking"])
                    else:
                        # Will be handled by interrupt section above
                        pass
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error processing query: {str(e)}")
                    st.session_state.conversation_history.append(
                        ("assistant", f"❌ Error: {str(e)}")
                    )

# Footer
st.divider()
st.caption("💡 **Tips:** Ask math questions, request knowledge/information, or book a ground. The system will ask for missing information if needed.")

