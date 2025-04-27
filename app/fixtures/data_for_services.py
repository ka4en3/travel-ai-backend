# app/fixtures/data_for_services.py

from datetime import datetime, timedelta, date
from constants.roles import RouteRole

USERS_FIXTURES = [
    {
        "email": "alice@example.com",
        "password": "password123",
        "username": "alice",
        "first_name": "Alice",
        "last_name": "Wonderland",
        "language": "en",
        "is_premium": True,
        "is_bot": False,
    },
    {
        "email": "bob@example.com",
        "password": "securepass456",
        "username": "bob",
        "first_name": "Bob",
        "last_name": "Builder",
        "language": "en",
        "is_premium": False,
        "is_bot": False,
    },
    {
        "email": "charlie@example.com",
        "password": "charliepass789",
        "username": "charlie",
        "first_name": "Charlie",
        "last_name": "Chaplin",
        "language": "en",
        "is_premium": False,
        "is_bot": False,
    },
    {
        "email": "diana@example.com",
        "password": "dianapass321",
        "username": "diana",
        "first_name": "Diana",
        "last_name": "Prince",
        "language": "fr",
        "is_premium": True,
        "is_bot": False,
    },
    {
        "email": "edward@example.com",
        "password": "edwardpass654",
        "username": "edward",
        "first_name": "Edward",
        "last_name": "Snow",
        "language": "de",
        "is_premium": False,
        "is_bot": False,
    },
    {
        "telegram_id": 100001,
        "username": "alice_bot",
        "first_name": "Alice",
        "last_name": "Wonder",
        "language": "en",
        "is_premium": True,
        "is_bot": False,
    },
    {
        "telegram_id": 100002,
        "username": "bob_travel",
        "first_name": "Bob",
        "last_name": "Builder",
        "language": "en",
        "is_premium": False,
        "is_bot": False,
    },
    {
        "telegram_id": 100003,
        "username": "charlie",
        "first_name": "Charlie",
        "last_name": "Chaplin",
        "language": "en",
        "is_premium": False,
        "is_bot": True,
    },
    {
        "telegram_id": 100004,
        "username": "diana_trips",
        "first_name": "Diana",
        "last_name": "Prince",
        "language": "fr",
        "is_premium": True,
        "is_bot": False,
    },
    {
        "telegram_id": 100005,
        "username": "ed_explorer",
        "first_name": "Edward",
        "last_name": "Snow",
        "language": "de",
        "is_premium": False,
        "is_bot": False,
    },
]

AICACHE_FIXTURES = [
    {
        # "id": 1,
        "user_id": 1,
        "cache_key": "Paris:Paris:3:1500.0",
        "prompt_hash": "fa1d3b3c0cb23a1dd47ff2b8f8e1d3a4",  # условный md5
        "original_prompt": "Plan a 3-day trip to Paris for a couple interested in art and food.",
        "origin": "Paris",
        "destination": "Paris",
        "duration_days": 3,
        "budget": 1500.0,
        "interests": ["culture", "food", "museums"],
        "hit_count": 1,
        "source": "bot",
        "expires_at": datetime.now() + timedelta(days=30),
        "result": {
            "name": "Paris Adventure",
            "origin": "Paris",
            "destination": "Paris",
            "duration_days": 3,
            "budget": 1500.0,
            "interests": ["culture", "food", "museums"],
            "days": [
                {
                    "day_number": 1,
                    "description": "Arrival and city walk",
                    "date": "2025-04-15",
                    "activities": [
                        {
                            "name": "Check-in at hotel",
                            "description": "Drop off luggage at the hotel",
                            "start_time": "10:30",
                            "end_time": "11:00",
                            "location": "Hotel Le Meurice",
                            "cost": 0.0,
                            "notes": "Early check-in requested",
                            "activity_type": "Accommodation",
                            "external_link": "https://lemeurice.com",
                        },
                        {
                            "name": "Walk around Louvre",
                            "description": "Explore the outside area of the Louvre",
                            "start_time": "12:00",
                            "end_time": "14:00",
                            "location": "Louvre Museum",
                            "cost": 0.0,
                            "activity_type": "Sightseeing",
                        },
                    ],
                },
                {
                    "day_number": 2,
                    "description": "Museum and food day",
                    "date": "2025-04-16",
                    "activities": [
                        {
                            "name": "Visit Musée d'Orsay",
                            "start_time": "10:00",
                            "end_time": "13:00",
                            "location": "Musée d'Orsay",
                            "cost": 15.0,
                            "activity_type": "Museum",
                        },
                        {
                            "name": "Lunch at Café de Flore",
                            "start_time": "13:30",
                            "end_time": "14:30",
                            "location": "Café de Flore",
                            "cost": 35.0,
                            "activity_type": "Food",
                        },
                    ],
                },
                {
                    "day_number": 3,
                    "description": "Shopping and departure",
                    "date": "2025-04-17",
                    "activities": [
                        {
                            "name": "Champs-Élysées shopping",
                            "start_time": "10:00",
                            "end_time": "12:00",
                            "location": "Champs-Élysées",
                            "cost": 0.0,
                            "activity_type": "Shopping",
                        },
                        {
                            "name": "Flight home",
                            "start_time": "15:00",
                            "end_time": "18:00",
                            "location": "CDG Airport",
                            "cost": 0.0,
                            "activity_type": "Transportation",
                        },
                    ],
                },
            ],
        },
    },
    {
        # "id": 2,
        "user_id": 2,
        "cache_key": "Tokyo:Tokyo:5:2500.0",
        "prompt_hash": "b7b1cde442f4b3e732ada8d0f9c5d3a0",
        "original_prompt": "Plan a 5-day trip to Tokyo for a solo traveler interested in technology and anime.",
        "origin": "Tokyo",
        "destination": "Tokyo",
        "duration_days": 5,
        "budget": 2500.0,
        "interests": ["technology", "anime", "gaming"],
        "hit_count": 3,
        "source": "bot",
        "expires_at": datetime.now() + timedelta(days=25),
        "result": {
            "name": "Tech & Anime Tokyo",
            "origin": "Tokyo",
            "destination": "Tokyo",
            "duration_days": 5,
            "budget": 2500.0,
            "interests": ["technology", "anime", "gaming"],
            "days": [
                {
                    "day_number": 1,
                    "description": "Akihabara tour",
                    "date": "2025-05-01",
                    "activities": [
                        {
                            "name": "Visit Akihabara",
                            "start_time": "10:00",
                            "end_time": "13:00",
                            "location": "Akihabara",
                            "cost": 0.0,
                            "activity_type": "Sightseeing",
                        }
                    ],
                }
            ],
        },
    },
    {
        # "id": 3,
        "user_id": 3,
        "cache_key": "New York:New York:2:1000.0",
        "prompt_hash": "c99de9bc0b824af4a1c7d2be77c87651",
        "original_prompt": "Quick weekend getaway in New York focused on landmarks and nightlife.",
        "origin": "New York",
        "destination": "New York",
        "duration_days": 2,
        "budget": 1000.0,
        "interests": ["nightlife", "sightseeing"],
        "hit_count": 2,
        "source": "api",
        "expires_at": datetime.now() + timedelta(days=20),
        "result": {
            "name": "NYC Express",
            "origin": "New York",
            "destination": "New York",
            "duration_days": 2,
            "budget": 1000.0,
            "interests": ["nightlife", "sightseeing"],
            "days": [
                {
                    "day_number": 1,
                    "description": "Landmark hopping",
                    "date": "2025-05-10",
                    "activities": [
                        {
                            "name": "Visit Times Square",
                            "start_time": "12:00",
                            "end_time": "14:00",
                            "location": "Times Square",
                            "cost": 0.0,
                            "activity_type": "Sightseeing",
                        }
                    ],
                }
            ],
        },
    },
    {
        # "id": 4,
        "user_id": 1,
        "cache_key": "Barcelona:Barcelona:4:1800.0",
        "prompt_hash": "c1d224ffd93882cb11b0021c49977ab7",
        "original_prompt": "Plan a relaxed trip to Barcelona focused on beaches and local cuisine.",
        "origin": "Barcelona",
        "destination": "Barcelona",
        "duration_days": 4,
        "budget": 1800.0,
        "interests": ["beach", "food", "culture"],
        "hit_count": 5,
        "source": "bot",
        "expires_at": datetime.now() + timedelta(days=40),
        "result": {
            "name": "Barcelona Bliss",
            "origin": "Barcelona",
            "destination": "Barcelona",
            "duration_days": 4,
            "budget": 1800.0,
            "interests": ["beach", "food", "culture"],
            "days": [
                {
                    "day_number": 1,
                    "description": "Beach day",
                    "date": "2025-06-01",
                    "activities": [
                        {
                            "name": "Relax at Barceloneta",
                            "start_time": "11:00",
                            "end_time": "16:00",
                            "location": "Barceloneta Beach",
                            "cost": 0.0,
                            "activity_type": "Beach",
                        }
                    ],
                }
            ],
        },
    },
    {
        # "id": 5,
        "user_id": 4,
        "cache_key": "Rome:Rome:3:1300.0",
        "prompt_hash": "a14a2f63f7c9d35172906c5610b9943d",
        "original_prompt": "Family trip to Rome with historical attractions.",
        "origin": "Rome",
        "destination": "Rome",
        "duration_days": 3,
        "budget": 1300.0,
        "interests": ["history", "architecture"],
        "hit_count": 4,
        "source": "bot",
        "expires_at": datetime.now() + timedelta(days=35),
        "result": {
            "name": "Roman Holiday",
            "origin": "Rome",
            "destination": "Rome",
            "duration_days": 3,
            "budget": 1300.0,
            "interests": ["history", "architecture"],
            "days": [
                {
                    "day_number": 1,
                    "description": "Ancient sights",
                    "date": "2025-06-10",
                    "activities": [
                        {
                            "name": "Visit Colosseum",
                            "start_time": "10:00",
                            "end_time": "12:00",
                            "location": "Colosseum",
                            "cost": 16.0,
                            "activity_type": "Museum",
                        }
                    ],
                }
            ],
        },
    },
]


ROUTES_FIXTURES = [
    {
        "origin": "Paris",
        "destination": "Paris",
        "duration_days": 3,
        "budget": 1500,
    },
    {
        "origin": "Tokyo",
        "destination": "Tokyo",
        "duration_days": 5,
        "budget": 2500.0,
        "interests": ["technology", "culture"],
    },
    {
        "origin": "New York",
        "destination": "New York",
        "duration_days": 2,
        "budget": 1000.0,
    },
    {
        "origin": "Barcelona",
        "destination": "Barcelona",
        "duration_days": 4,
        "budget": 1800,
    },
    {
        "origin": "Rome",
        "destination": "Rome",
        "duration_days": 3,
        "budget": 1300.0,
        "interests": ["no interests"],
    },
]

ROUTE_ACCESS_FIXTURES = [
    {
        "user_id": 2,
        "route_id": 2,
        "role": RouteRole.EDITOR,
    },
    {
        "user_id": 3,
        "route_id": 2,
        "role": RouteRole.VIEWER,
    },
    {
        "user_id": 2,
        "route_id": 3,
        "role": RouteRole.EDITOR,
    },
    {
        "user_id": 3,
        "route_id": 3,
        "role": RouteRole.VIEWER,
    },
    {
        "user_id": 2,
        "route_id": 4,
        "role": RouteRole.VIEWER,
    },
    {
        "user_id": 4,
        "route_id": 5,
        "role": RouteRole.EDITOR,
    },
]
