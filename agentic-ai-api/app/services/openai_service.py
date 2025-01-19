from uuid import uuid4
import uuid
import openai
from openai import OpenAI
import requests
from fastapi import HTTPException, Depends
from typing import Any, Optional, List, Dict
from app.api.endpoints.medicare import get_appointments, AppointmentResponse, AppointmentCreate, Appointment
from app.core.config import Settings
from functools import lru_cache
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from datetime import date
import json
import base64
from app.services.reservations import create_reservation, get_reservations  
from app.schemas.reservations import ReservationCreate, ReservationResponse 

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

client = OpenAI(
    api_key=settings.OPENAI_API_KEY  # Use the API key from settings
)

# BaseModel for the JSON output

# OpenAI Chat Completion
def complete_chat(message: str):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant."},
                {"role": "user", "content": message},
            ],
        )
        print(f"AI Response: {response}")
        return response
    except Exception as e:
        # Handle exceptions
        print("An error occurred:", e)
        return None

#############
# Agent 3
#############
# Agent function to process messages and call OpenAI API
async def process_agent3(custom_message: str):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g., San Francisco, CA",
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                        },
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_appointments",
                "description": "Retrieve medical appointments with optional filters such as status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Filter appointments by status, e.g., Pending",
                        },
                    },
                    "required": [],
                },
            },
        },
    ]

    # Function definitions for weather retrieval
    def get_current_weather(location: str, unit: str = "fahrenheit"):
        """Get the current weather in a given location."""
        if "tokyo" in location.lower():
            return json.dumps({"location": "Tokyo", "temperature": 10, "unit": unit})
        elif "san francisco" in location.lower():
            return json.dumps({"location": "San Francisco", "temperature": 72, "unit": unit})
        elif "paris" in location.lower():
            return json.dumps({"location": "Paris", "temperature": 22, "unit": unit})
        else:
            return json.dumps({"location": location, "temperature": "unknown"})

    def fetch_appointments(
        patient_id: str = None,
        status: str = None,
        type: str = None,
        scheduled_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[dict]:
        """Wrapper function to fetch appointments and ensure JSON serialization."""
        
        # Manually get a database session
        db: Session = next(get_db())
        try:
            # Call the get_appointments function (assuming it exists)
            appointments = get_appointments(
                patient_id=patient_id,
                status=status,
                type=type,
                scheduled_date=scheduled_date,
                skip=skip,
                limit=limit,
                db=db,  # Pass the database session
            )
            
            # Convert to JSON serializable format using Pydantic models
            return [AppointmentResponse.from_orm(appointment).dict() for appointment in appointments]
        finally:
            # Ensure the session is closed
            db.close()


    # Function to handle function calls
    def call_function(name, args):
        """Routes the function calls to their corresponding implementations."""
        if name == "get_current_weather":
            return get_current_weather(**args)
        elif name == "get_appointments":
            return fetch_appointments(**args)
        return json.dumps({"error": f"Function {name} not found."})

    # Agent Function to interact with OpenAI API and handle responses
    # Agent Function
    try:
        # Step 1: Call the OpenAI API with the initial user message and tools
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": custom_message},
        ]
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        # Debugging output (optional)
        # print("*DEBUG Start*:", completion.choices[0].message)
        
        # Step 2: Handle each tool call in the response
        tool_calls = completion.choices[0].message.tool_calls if completion.choices[0].message.tool_calls else []
        
        for tool_call in tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            result = call_function(name, args)
            
            # Debugging output (optional)
            # print("*DEBUG Start*:", result, "*DEBUG End*")
            
            messages.append(completion.choices[0].message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        # Step 3: Make a second API call with the updated messages
        completion_2 = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=tools,
        )

        # Return the final response from the second API call
        return completion_2.choices[0].message.content

    except Exception as e:
        # Handle exceptions
        print("An error occurred:", e)
        return None

#############
# Agent 4
#############
# Agent function to process messages and call OpenAI API
async def process_agent4(custom_message: str):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g., San Francisco, CA",
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                        },
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_reservations",
                "description": "Retrieve all the reservations details",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
        "type": "function",
        "function": {
            "name": "create_reservation",
            "description": "Create reservation order",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "The ID of the user making the reservation.",
                    },
                    "restaurant_name": {
                        "type": "string",
                        "description": "Name of the restaurant.",
                    },
                    "reservation_time": {
                        "type": "string",
                        "format": "date-time",  # Use ISO 8601 format
                        "description": "Date and time of the reservation in ISO 8601 format.",
                    },
                    "number_of_people": {
                        "type": "integer",
                        "description": "Number of people for the reservation.",
                    },
                    "budget": {
                        "type": "number",
                        "format": 'float',
                        'description': 'Budget for the reservation.',
                    },
                    # Optional status field
                    'status': {
                        'type': 'string',
                        'enum': ['pending', 'confirmed', 'canceled'],
                        'description': 'Status of the reservation.',
                    }
                },
                # Specify required fields
                'required': ['user_id', 'restaurant_name', 'reservation_time', 'number_of_people', 'budget'],
            },
        },
    },
    ]

    # Function definitions for weather retrieval
    def get_current_weather(location: str, unit: str = "fahrenheit"):
        """Get the current weather in a given location."""
        if "tokyo" in location.lower():
            return json.dumps({"location": "Tokyo", "temperature": 10, "unit": unit})
        elif "san francisco" in location.lower():
            return json.dumps({"location": "San Francisco", "temperature": 72, "unit": unit})
        elif "paris" in location.lower():
            return json.dumps({"location": "Paris", "temperature": 22, "unit": unit})
        else:
            return json.dumps({"location": location, "temperature": "unknown"})

    def fetch_reservations() -> list[ReservationResponse]:
        db: Session = next(get_db())  # Get a database session
        try:
            print("Accessing Database..")
            # Fetch all reservations
            reservations = get_reservations(db)
            
            # Convert SQLAlchemy objects to Pydantic models
            response = [ReservationResponse.from_orm(reservation) for reservation in reservations]
            
            # Log the response for debugging
            print(f"GET, Request Modeling: {response}")
            
            return response
        finally:
            db.close()  # Ensure the session is closed after use

    def make_reservation(reservation_data: ReservationCreate) -> ReservationResponse:
        db: Session = next(get_db())  # Get a database session
        try:
            print("Accessing Database..")
            # Create a new reservation
            new_reservation = create_reservation(db, reservation_data)  # Pass the reservation data
            
            # Convert SQLAlchemy object to Pydantic model
            response = ReservationResponse.from_orm(new_reservation)
            
            # Log the response for debugging
            print(f"POST, Request Modeling: {response}")
            
            return response  # Return the newly created reservation
        finally:
            db.close()  # Ensure the session is closed after use

    # Function to handle function calls
    def call_function(name, args):
        """Routes the function calls to their corresponding implementations."""
        if name == "get_current_weather":
            return get_current_weather(**args)
        elif name == "get_reservations":
            return fetch_reservations(**args)
        elif name == "create_reservation":
            # Predefine user_id statically for testing
            predefined_user_id = int(str(uuid.uuid4())[:8], 16) % 1000000  # Generate a new UUID
            
            # Create an instance of ReservationCreate with predefined user_id and other args
            reservation_data = ReservationCreate(
                user_id=predefined_user_id,
                restaurant_name=args.get('restaurant_name'),
                reservation_time=args.get('reservation_time'),
                number_of_people=args.get('number_of_people'),
                budget=args.get('budget'),
                status=args.get('status', 'pending')  # Default status if not provided
            )
            # # Create an instance of ReservationCreate from args
            # reservation_data = ReservationCreate(**args)
            return make_reservation(reservation_data)
        return json.dumps({"error": f"Function {name} not found."})

    # Agent Function to interact with OpenAI API and handle responses
    # Agent Function
    try:
        # Step 1: Call the OpenAI API with the initial user message and tools
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": custom_message},
        ]

        print("*Parsing Request..*")
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        # Debugging output (optional)
        # print("*DEBUG Start*:", completion.choices[0].message)
        print("Deciding Agent")
        print("Searching for available tools")
        # Step 2: Handle each tool call in the response
        tool_calls = completion.choices[0].message.tool_calls if completion.choices[0].message.tool_calls else []
        
        for tool_call in tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            result = call_function(name, args)
            
            # Debugging output (optional)
            #print("*DEBUG tool_calls Start*:", result, "*DEBUG End*")
            print("Tool Found")
            
            messages.append(completion.choices[0].message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": f'{result}'
            })
            #print("*DEBUG messages Start*:", messages, "*DEBUG End*")
            print("Making API Call..")
            #print("**Considering the restaurant accepted the reservation already, we can check the availability here..**")

        # Step 3: Make a second API call with the updated messages
        completion_2 = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=tools,
        )
        print("*Agent Status*: Successfull")
        # Return the final response from the second API call
        return completion_2.choices[0].message.content

    except Exception as e:
        # Handle exceptions
        print("An error occurred:", e)
        return None
    
#############
# Agent 5: Conversation Chain
#############

# Initialize a global state for conversation
conversation_state: Dict[str, Any] = {}
# Agent function to process messages and call OpenAI API
async def process_agent5(custom_message: str):
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g., San Francisco, CA",
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                        },
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_reservations",
                "description": "Retrieve all the reservations details",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
        "type": "function",
        "function": {
            "name": "create_reservation",
            "description": "Create reservation order",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "The ID of the user making the reservation.",
                    },
                    "restaurant_name": {
                        "type": "string",
                        "description": "Name of the restaurant.",
                    },
                    "reservation_time": {
                        "type": "string",
                        "format": "date-time",  # Use ISO 8601 format
                        "description": "Date and time of the reservation in ISO 8601 format.",
                    },
                    "number_of_people": {
                        "type": "integer",
                        "description": "Number of people for the reservation.",
                    },
                    "budget": {
                        "type": "number",
                        "format": 'float',
                        'description': 'Budget for the reservation.',
                    },
                    # Optional status field
                    'status': {
                        'type': 'string',
                        'enum': ['pending', 'confirmed', 'canceled'],
                        'description': 'Status of the reservation.',
                    }
                },
                # Specify required fields
                'required': ['restaurant_name', 'reservation_time', 'number_of_people', 'budget'],
            },
        },
    },
    ]
    # Initialize conversation state
    conversation_state = {}
    # Function definitions for weather retrieval
    def get_current_weather(location: str, unit: str = "fahrenheit"):
        """Get the current weather in a given location."""
        if "tokyo" in location.lower():
            return json.dumps({"location": "Tokyo", "temperature": 10, "unit": unit})
        elif "san francisco" in location.lower():
            return json.dumps({"location": "San Francisco", "temperature": 72, "unit": unit})
        elif "paris" in location.lower():
            return json.dumps({"location": "Paris", "temperature": 22, "unit": unit})
        else:
            return json.dumps({"location": location, "temperature": "unknown"})

    def fetch_reservations() -> list[ReservationResponse]:
        db: Session = next(get_db())  # Get a database session
        try:
            print("Accessing Database..")
            # Fetch all reservations
            reservations = get_reservations(db)
            
            # Convert SQLAlchemy objects to Pydantic models
            response = [ReservationResponse.from_orm(reservation) for reservation in reservations]
            
            # Log the response for debugging
            print(f"GET, Request Modeling: {response}")
            
            return response
        finally:
            db.close()  # Ensure the session is closed after use

    def make_reservation(reservation_data: ReservationCreate) -> ReservationResponse:
        db: Session = next(get_db())  # Get a database session
        try:
            print("Accessing Database..")
            # Create a new reservation
            new_reservation = create_reservation(db, reservation_data)  # Pass the reservation data
            
            # Convert SQLAlchemy object to Pydantic model
            response = ReservationResponse.from_orm(new_reservation)
            
            # Log the response for debugging
            print(f"POST, Request Modeling: {response}")
            
            return response  # Return the newly created reservation
        finally:
            db.close()  # Ensure the session is closed after use

    # Function to handle function calls
    def call_function(name, args):
        """Routes the function calls to their corresponding implementations."""
        if name == "get_current_weather":
            return get_current_weather(**args)
        elif name == "get_reservations":
            return fetch_reservations(**args)
        elif name == "create_reservation":
            # Predefine user_id statically for testing
            predefined_user_id = int(str(uuid.uuid4())[:8], 16) % 1000000  # Generate a new UUID
            
            # Create an instance of ReservationCreate with predefined user_id and other args
            reservation_data = ReservationCreate(
                user_id=predefined_user_id,
                restaurant_name=args.get('restaurant_name'),
                reservation_time=args.get('reservation_time'),
                number_of_people=args.get('number_of_people'),
                budget=args.get('budget'),
                status=args.get('status', 'pending')  # Default status if not provided
            )
            # # Create an instance of ReservationCreate from args
            # reservation_data = ReservationCreate(**args)
            return make_reservation(reservation_data)
        return json.dumps({"error": f"Function {name} not found."})

    # Agent Function to interact with OpenAI API and handle responses
    # Agent Function
    try:
        messages = [
            {"role": 'system', 'content': 'You are a helpful assistant.'},
            {"role": 'user', 'content': custom_message},
        ]

        while True:
            print("*Parsing Request..*")
            
            completion = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=messages,
                tools=tools,
                tool_choice='auto',
            )

            print("Deciding Agent")
            print("Searching for available tools")
            
            tool_calls = completion.choices[0].message.tool_calls if completion.choices[0].message.tool_calls else []

            # Iterate through each tool call
            for tool_call in tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                # Check for missing parameters dynamically
                required_params = tools[0]['function']['parameters']['required']
                missing_params = [param for param in required_params if param not in conversation_state or not conversation_state[param]]
                
                print("required_params: ", required_params)
                print("missing_params: ", missing_params)

                if missing_params:
                    # Respond with missing parameters
                    for param in missing_params:
                        description = tools[0]['function']['parameters']['properties'][param]['description']
                        
                        # Ask user for each missing parameter
                        response_message = f"I need more information: {description}."
                        messages.append({"role": 'assistant', 'content': response_message})
                        
                        # Here you would normally wait for user input. IMPLEMENT UserID, and ConversationId to store Conversation Chain.
                        # For simulation, we can just assume input is provided.
                        # user_response = await get_user_response(param)  # Replace with actual input handling
                        
                        # # Update conversation state with user's response
                        # conversation_state[param] = user_response
                        
                        # Append user's response to messages
                        # messages.append({"role": 'user', 'content': user_response})

                    # Break out of this loop to retry with updated context
                    break

                # If no parameters are missing, call the function
                result = call_function(name, {**args, **conversation_state})
                
                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'content': f'{result}'
                })

            # Step 3: Make a second API call with updated messages
            completion_2 = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=messages,
                tools=tools,
            )
            
            print("*Agent Status*: Successful")
            
            # Return final response from second API call
            return completion_2.choices[0].message.content

    except Exception as e:
        print("An error occurred:", e)
        return None