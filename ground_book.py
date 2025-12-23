# from typing import TypedDict, List
# import csv
# import os
# from datetime import datetime


# class BookingSchema(TypedDict):
#     user_id: str
#     start_time: str
#     end_time: str
#     date: str
#     status:str

# CSV_FILE = "bookings.csv"


# def get_booking(user_id: str) -> List[BookingSchema]:
#     """
#     Get all bookings for a specific user_id.
    
#     Args:
#         user_id: The user ID to filter bookings by
        
#     Returns:
#         List of booking dictionaries matching the user_id
#     """
#     bookings = read_bookings_from_csv()
#     return [booking for booking in bookings if booking["user_id"] == user_id]


# def is_time_slot_available(booking: BookingSchema) -> bool:
#     """
#     Check if a time slot is available (not conflicting with existing bookings).
    
#     Args:
#         booking: A booking dictionary with user_id, start_time, end_time, and date
        
#     Returns:
#         True if the time slot is available, False if it conflicts with existing bookings
#     """
#     existing_bookings = read_bookings_from_csv()
    
#     # Parse the new booking times
#     new_start = datetime.strptime(booking["start_time"], "%H:%M").time()
#     new_end = datetime.strptime(booking["end_time"], "%H:%M").time()
#     new_date = booking["date"]
    
#     for existing_booking in existing_bookings:
#         # Check if it's the same date
#         if existing_booking["date"] == new_date:
#             # Parse existing booking times
#             existing_start = datetime.strptime(existing_booking["start_time"], "%H:%M").time()
#             existing_end = datetime.strptime(existing_booking["end_time"], "%H:%M").time()
            
#             # Check for time overlap
#             # Two time slots overlap if:
#             # - new_start < existing_end AND new_end > existing_start
#             if new_start < existing_end and new_end > existing_start:
#                 return False
    
#     return True


# def save_booking_to_csv(booking: BookingSchema) -> str:
#     """
#     Save a booking to the CSV file.
#     If the file doesn't exist, it will be created with headers.
#     Checks for time slot conflicts before saving.
    
#     Args:
#         booking: A booking dictionary with user_id, start_time, end_time, and date
        
#     Returns:
#         Success message if booking is saved, or error message if time slot is occupied
#     """
#     # Check if time slot is available
#     if not is_time_slot_available(booking):
#         return "Unable to book on this time. Please update your start time or end time."
    
#     file_exists = os.path.isfile(CSV_FILE)
    
#     with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
#         fieldnames = ['user_id', 'start_time', 'end_time', 'date']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
#         # Write header if file is new
#         if not file_exists:
#             writer.writeheader()
        
#         # Write the booking data
#         writer.writerow(booking)
    
#     return booking


# def read_bookings_from_csv() -> List[BookingSchema]:
#     """
#     Read all bookings from the CSV file.
    
#     Returns:
#         List of all booking dictionaries from the CSV file
#     """
#     bookings = []
    
#     if not os.path.isfile(CSV_FILE):
#         return bookings
    
#     with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             booking: BookingSchema = {
#                 "user_id": row["user_id"],
#                 "start_time": row["start_time"],
#                 "end_time": row["end_time"],
#                 "date": row["date"]
#             }
#             bookings.append(booking)
    
#     return bookings


# # user_bookings = get_booking("user123")
# # booking: BookingSchema = {
# #     "user_id": "user123",
# #     "start_time": "09:00",    # 9:00 AM in 24-hour format
# #     "end_time": "17:30",       # 5:30 PM in 24-hour format
# #     "date": "2024-01-15"
# # }

# # result = save_booking_to_csv(booking)
# # print(result)
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from typing import TypedDict, List
import csv
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import true
load_dotenv()  # loads .env from current directory
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")


class BookingSchema(TypedDict):
    user_id: str
    start_time: str
    end_time: str
    date: str
    status:str

CSV_FILE = "bookings.csv"


def get_booking(user_id: str) -> List[BookingSchema]:
    """
    Get all bookings for a specific user_id.
    
    Args:
        user_id: The user ID to filter bookings by
        
    Returns:
        List of booking dictionaries matching the user_id
    """
    bookings = read_bookings_from_csv()
    return [booking for booking in bookings if booking["user_id"] == user_id]


def is_time_slot_available(booking: BookingSchema) -> bool:
    """
    Check if a time slot is available (not conflicting with existing bookings).
    
    Args:
        booking: A booking dictionary with user_id, start_time, end_time, and date
        
    Returns:
        True if the time slot is available, False if it conflicts with existing bookings
    """
    existing_bookings = read_bookings_from_csv()
    
    # Parse the new booking times
    new_start = datetime.strptime(booking["start_time"], "%H:%M").time()
    new_end = datetime.strptime(booking["end_time"], "%H:%M").time()
    new_date = booking["date"]
    
    for existing_booking in existing_bookings:
        # Check if it's the same date
        if existing_booking["date"] == new_date:
            # Parse existing booking times
            existing_start = datetime.strptime(existing_booking["start_time"], "%H:%M").time()
            existing_end = datetime.strptime(existing_booking["end_time"], "%H:%M").time()
            
            # Check for time overlap
            # Two time slots overlap if:
            # - new_start < existing_end AND new_end > existing_start
            if new_start < existing_end and new_end > existing_start:
                return False
    
    return True


def save_booking_to_csv(booking: BookingSchema):
    required_fields = ["user_id", "start_time", "end_time", "date"]

    if not all(booking.get(f) for f in required_fields):
        booking["status"] = ""
        return booking

    if not is_time_slot_available(booking):
        booking["status"] = "Unable to book on this time. Please update your start time or end time."
        return booking

    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['user_id', 'start_time', 'end_time', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # ✅ write header if file is new OR empty
        if not file_exists or os.stat(CSV_FILE).st_size == 0:
            writer.writeheader()

        writer.writerow({
            "user_id": booking["user_id"],
            "start_time": booking["start_time"],
            "end_time": booking["end_time"],
            "date": booking["date"]
        })

    booking["status"] = "Booking confirmed"
    return booking



def read_bookings_from_csv() -> List[BookingSchema]:
    """
    Read all bookings from the CSV file.
    
    Returns:
        List of all booking dictionaries from the CSV file
    """
    bookings = []
    
    if not os.path.isfile(CSV_FILE):
        return bookings
    
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            
            booking: BookingSchema = {
                "user_id": row["user_id"],
                "start_time": row["start_time"],
                "end_time": row["end_time"],
                "date": row["date"]
            }
            bookings.append(booking)
    
    return bookings

ground_booking_bilder=StateGraph(BookingSchema)
ground_booking_bilder.add_node("save_booking_to_csv",save_booking_to_csv)
ground_booking_bilder.add_edge(START,"save_booking_to_csv")
ground_booking_bilder.add_edge("save_booking_to_csv",END)
checkpointer = MemorySaver()
ground_book_graph=ground_booking_bilder.compile()
config = {"configurable": {"thread_id": '12345'}}


# save_booking_to_csv(booking={'user_id': 123, 'start_time': '00:00', 'end_time': '14:00', 'date': '2026-03-02'})

from typing import TypedDict
import json
import openai


# -----------------------------
# OpenAI API key setup
# -----------------------------
openai.api_key = OPENAI_API_KEY

# -----------------------------
# Prompt template
# -----------------------------
PROMPT_TEMPLATE = PROMPT_TEMPLATE = """
                    You are a booking assistant.

                    Extract booking information from the user query.

                    Return ONLY a valid JSON object matching:
                    BookingSchema(TypedDict, total=False)
                    Allowed fields: user_id, start_time, end_time, date, status

                    STRICT RULES:
                    1. Output MUST be valid JSON only. No explanation.
                    2. Time format MUST be 24-hour HH:MM.
                    3. Convert AM/PM to 24-hour time.
                    4. Date format MUST be YYYY-MM-DD.
                    5. Include ONLY fields explicitly mentioned or clearly inferred.
                    6. If a field exists in the previous state and is NOT updated by the user,
                    KEEP the previous value.
                    7. 🚫 If end_time is NOT mentioned, DO NOT include end_time.
                    8. 🚫 Never copy start_time into end_time.
                    9. Do NOT guess missing fields.
                    10. Do NOT include empty, null, or invalid values.

                    Previous state:
                    {previous_state}

                    User query:
                    "{user_query}"
"""



# -----------------------------
# Function to update single booking state
# -----------------------------
def update_booking_state(user_query: str, previous_state: BookingSchema) -> BookingSchema:
    prev_state_str = json.dumps(previous_state)
    prompt = PROMPT_TEMPLATE.format(user_query=user_query, previous_state=prev_state_str)

    # New syntax for v1.0+ OpenAI Python SDK
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful booking assistant."},
            {"role": "user", "content": prompt}
        ],
       
    )

    ai_text = response.choices[0].message.content.strip()

    try:
        updated_state = json.loads(ai_text)
        
        return updated_state
    except json.JSONDecodeError:
        return previous_state

