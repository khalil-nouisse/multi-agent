from dotenv import load_dotenv
load_dotenv()

import threading
import time
from langchain_core.messages import HumanMessage
from graph.graph_builder import build_graph
from langsmith1.tracing import get_callback_manager
from langsmith import traceable

# Import the listener and email service
from communication.email.email_listener import listen_for_emails, parse_email
from communication.email.email_service import email_service


# Assuming the graph is a long-lived object
graph = build_graph()

def display_conversation(messages):
    shown = set()
    for msg in messages:
        sender = getattr(msg, "name", "user")
        key = (sender, msg.content)
        if key in shown:
            continue
        shown.add(key)
        print(f"{sender}: {msg.content}")

def handle_final_response(final_state):
    """
    Handles the final output from the graph and delivers it to the user.
    """
    final_message_obj = final_state["messages"][-1]
    final_message_text = final_message_obj.content

    communication_type = final_state.get("communication_type")
    
    if communication_type == "email":
        sender_email = final_state.get("original_sender_email")
        reply_subject = f"Re: {final_state.get('original_subject', 'Your Request')}"
        
        # Use the email service to send the response
        success, message = email_service.send_email(sender_email, reply_subject, final_message_text)
        if success:
            print(f"Successfully sent email response to {sender_email}")
        else:
            print(f"Failed to send email response: {message}")
    else: # For direct user input from console or API
        display_conversation(final_state["messages"])
        
@traceable(name="ActevaCRM")
def run_direct_input(user_input: str, communication_type: str = "console"):
    callback_manager = get_callback_manager()
    
    input_data = {
        "messages": [HumanMessage(content=user_input)],
        "next": "supervisor",
        "communication_type": communication_type,
    }
    
    result = graph.invoke(input_data, config={"callbacks": callback_manager})
    handle_final_response(result)

def process_incoming_email(email_data):
    """
    This is the callback function for the email listener.
    It takes parsed email data and runs the graph.
    """
    print(f"Processing email from {email_data['sender']} with subject: {email_data['subject']}")

    callback_manager = get_callback_manager()
    
    input_data = {
        "messages": [HumanMessage(content=email_data['body'])],
        "next": "supervisor",
        "communication_type": "email",
        "original_sender_email": email_data['sender'],
        "original_subject": email_data['subject']
    }
    
    try:
        result = graph.invoke(input_data, config={"callbacks": callback_manager})
        handle_final_response(result)
    except Exception as e:
        print(f"Error during graph execution for email from {email_data['sender']}: {e}")
        error_message = "I'm sorry, an error occurred while processing your request. Please try again later."
        email_service.send_email(email_data['sender'], f"Re: {email_data['subject']}", error_message)

if __name__ == "__main__":
    # Start the email listener in a separate thread , for processing incoming emails 
    listener_thread = threading.Thread(target=listen_for_emails, args=(process_incoming_email,), daemon=True)
    listener_thread.start()
    
    print("Email listener started in a background thread.")
    print("Enter console input to test the system or wait for emails.")
    
    try:
        while True:
            user_input = input("\nHello there i need help from technical support to know the status of my ticket , ticket123! ")
            if user_input.lower() == 'exit':
                break
            run_direct_input(user_input, communication_type="console")
    except KeyboardInterrupt:
        print("Main script terminated.")