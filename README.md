# LLM-Evaluation-Framework

This repository contains the source code for a Large Language Model (LLM) Evaluation Framework. The framework is designed as a full-stack web application that enables users to evaluate LLM-generated responses through a survey. The application is developed using Streamlit, HTML, CSS, and SQL and is currently deployed on Jetstream and Azure.

# Features
- User Authentication: Users can register, log in, and log out securely.
- Survey Interface: The application presents a survey where users can evaluate model responses to various prompts by answering a set of questions using radio buttons.
- Real-Time Data Storage: User responses are saved in real-time and stored in a database.
- Session Persistence: Users can log out and return to the survey at the point where they left off, ensuring a seamless experience.
- Database Management: The application utilizes SQLite to manage user data, survey questions, prompts, and model responses.
- Instructions and Guidance: Users are provided with clear instructions on how to participate in the survey and evaluate the models.

# Tech Stack
- Frontend: Streamlit, HTML, CSS
- Backend: Python, SQLite
- Deployment: Jetstream, Azure
