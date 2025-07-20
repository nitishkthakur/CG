# Project description

## Requirements - functionality
1. login page rendered by clerk (new user hahndling also handled by clerk)
2. The app is a course provider. The user is shown predefined topics and has the option to also manually enter a topic of their choice. 
3. They are then asked about their difficulty level and what balance they would like to strike in terms of coding vs theory.
4. upon selecting, the course will be rendered by an LLM and provided chapter- by  Chapter to the user.
5. The user, then gives feedback on how to refine the table of contents.
6. Finally, after the approval from the user, the course will be finalized and made available for the user to start learning.
7. The course is delivered chapter by chapter and the user accumulates points along the way which he can redeem on other courses or other partner websites.


### Tech Stack
Frontend:
    - HTML + Tailwind CSS + Alpine  +  HTMX + JS
    - Deep and dark blue is the primary color
    - Use Material Icons and Material Design for UI components with the primary color I mentioned

Backend:
    - Python + FastAPI + SQLAlchemy + PostgreSQL + Mongo + Redis + Celery + Spark
    - LLM Inference: Groq

