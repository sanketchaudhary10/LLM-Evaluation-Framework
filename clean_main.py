import streamlit as st
import sqlite3
import time
import pandas as pd
import csv
import json

st.set_page_config(layout="wide", page_title="Mental Health Chatbot Evaluation")
st.markdown("<div id='top'></div>", unsafe_allow_html=True)
# create user responses JSON in session_state
if "user_responses" not in st.session_state:
    st.session_state["user_responses"] = {}
    st.session_state["user_responses"]["responses"] = []

# Database connection
conn = sqlite3.connect("main_db.db")
curr = conn.cursor()

# Functions to handle database operations
def create_usertable():
    curr.execute(
        "CREATE TABLE IF NOT EXISTS userstable(user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)"
    )
    conn.commit()

def create_responsestable():
    curr.execute(
        "CREATE TABLE IF NOT EXISTS responsestable(response_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, question_id INTEGER, model1_response INTEGER, model2_response INTEGER, FOREIGN KEY(user_id) REFERENCES userstable(user_id), FOREIGN KEY(question_id) REFERENCES questionstable(question_id))"
    )
    conn.commit()

def create_questionstable():
    curr.execute(
        "CREATE TABLE IF NOT EXISTS questionstable(question_id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT NOT NULL)"
    )
    conn.commit()

def add_userdata(username, password):
    curr.execute(
        "INSERT INTO userstable(username, password) VALUES (?, ?)", (username, password)
    )
    conn.commit()

def save_userresponse(user_id, question_id, model1_response, model2_response):
    curr.execute(
        "REPLACE INTO responsestable(user_id, question_id, model1_response, model2_response) VALUES (?, ?, ?, ?)",
        (user_id, question_id, model1_response, model2_response),
    )
    conn.commit()

def login_user(username, password):
    curr.execute(
        "SELECT * FROM userstable WHERE username =? AND password =?",
        (username, password),
    )
    return curr.fetchone()

def get_userresponses(user_id):
    curr.execute(
        "SELECT question_id, model1_response, model2_response FROM responsestable WHERE user_id =?",
        (user_id,),
    )
    return curr.fetchall()

def get_questions():
    curr.execute("SELECT question_id, question FROM questionstable")
    return curr.fetchall()

def get_user_id(username):
    curr.execute(
        "SELECT user_id FROM userstable WHERE username =?", (username,)
    )
    return curr.fetchone()[0]

def logout_user():
    st.session_state.clear()

# Initialize tables
create_usertable()
create_responsestable()
create_questionstable()

questions_data = get_questions()
question_ids = [q[0] for q in questions_data]
questions = [q[1] for q in questions_data]
num_per_page = 5
total_pages = len(questions) // num_per_page + 1


def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state.logged_in:
        menu = ["Home", "Survey", "Logout"]
    else:
        menu = ["Home", "Login", "Signup"]

    choice = st.sidebar.selectbox("Menu", menu)

    create_usertable()

    if "last_active_time" not in st.session_state:
        st.session_state["last_active_time"] = time.time()

    # Checking if the user is inactive for a certain period
    if time.time() - st.session_state.last_active_time > 300:  # 300 seconds = 5 minutes
        logout_user()

    # session state

    if choice == "Home":
        st.subheader("Home")
        st.subheader("Welcome to Evaluation Framework")
        raw_text = """
    ## Instructions
Thank you for participating in our evaluation survey. Your feedback is crucial in improving the performance and capabilities of our Large Language Model. Please read the instructions carefully before proceeding with the survey.

### Objectives:
* To assess the accuracy, relevance, and coherence of the model's responses.
* To gather user satisfaction and overall experience with the model.

### Instructions for Participants:
* Understand the Questions: Each question is designed to evaluate specific aspects of the Large Language Model. Please read each question thoroughly.

* Interaction with the Model: You will interact directly with the model through a series of prompts. Record your interactions as specified.
* Provide Detailed Feedback:
** Accuracy: Rate the accuracy of the model's responses.
** Relevance: Evaluate how relevant the responses are to the given prompts.
** Coherence: Judge how coherent and logically structured the responses are.
** Overall Experience: Reflect on your overall experience and satisfaction with the model.

* Use the Rating Scale: Each question must be answered using the following scale:
1 (Very Poor)
2 (Poor)
3 (Average)
4 (Good)
5 (Excellent)

* Comment Section: Use the comment section to provide additional insights or specific examples that support your ratings.
* Confidentiality: All responses will be treated with strict confidentiality. Personal information is collected solely for the purpose of this research and will not be shared with third parties.
* Completion: Ensure you answer all questions to the best of your ability. Incomplete surveys may not be eligible for analysis.
* Submit the Survey: Once you have completed all sections of the survey, submit your answers using the designated button at the end of the form.
* Technical Issues: If you encounter any technical issues during the survey, please contact the support team at [support@example.com].
* Thank You: We appreciate your time and effort in helping us improve our model. Your insights are invaluable.

Please proceed by clicking on the “Start Survey” button below. We look forward to your valuable feedback!
    """
        st.markdown(raw_text)
        # button to go to survey
        if st.button("Start Survey"):
            choice = "Survey"
            # run the page again
            st.rerun()

    elif choice == "Login":
        st.subheader("Login Section")

        if not st.session_state.logged_in:
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                result = login_user(username, password)
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.last_active_time = (
                        time.time()
                    )  # Update last active time
                    st.success("Logged In as {}".format(username))
                    st.info("Session State: {}".format(st.session_state))
                    st.session_state["user_responses"]["username"] = st.session_state[
                        "username"
                    ]
                    st.rerun()
                else:
                    st.warning("Invalid Credentials")
        else:
            st.info("You are already logged in.")

    elif choice == "Signup":
        st.subheader("Create New Account")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")

        if st.button("Signup"):
            add_userdata(new_username, new_password)
            st.success("Account created successfully! Please login.")

    elif choice == "Survey":
        response_file = "responses.csv"
        file_pointer = csv.writer(open(response_file, "a", newline=""))

        # Load data
        df = pd.read_csv("prompts.csv")

        # Initialize session state for counter
        if "counter" not in st.session_state:
            st.session_state.counter = 0

        if st.session_state.counter >= len(df):
            st.error("Survey data is out of bounds.")
            st.stop()


        col1, col2, col3 = st.columns([4, 2, 1])
        col3.write("")

        current_response = {}

        # Function to display the next prompt
        def next_prompt():
            if "counter" in st.session_state:
                st.session_state.counter += 1
                st.session_state.current_page = 1
                if st.session_state.counter >= len(questions):
                    st.write("Thank you for participating in the survey!")
                    st.stop()

                st.rerun()


        prompt = df["questionText"].values[st.session_state.counter]
        option1 = df["answerText"].values[st.session_state.counter]
        option2 = df["modifiedResponse"].values[st.session_state.counter]
        prompt_id = df["questionID"].values[st.session_state.counter]

        current_response["promptID"] = prompt_id

        try:
            option2 = option2.replace("<s>", "").replace("</s>", "")
            option2 = option2.split("[/INST]")[1]
        except Exception as e:
            print(f"Error parsing option2: {e}")
            pass

        st.markdown(
            "<h1 style='text-align: center; color: darkred;'>Mental Health Chatbot Evaluation</h1>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='text-align: center;'>Please provide your feedback on the below chatbot responses. Rate the responses on a scale of 1 to 5, with 1 being the lowest and 5 being the highest.</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align: center;'>Contact us at dsail@iu.edu for any queries or feedback. Thank you for your time and effort!</p>",
            unsafe_allow_html=True,
        )

        if "current_page" not in st.session_state:
            st.session_state.current_page = 1

        for i in range(total_pages):
            if st.session_state.current_page == i + 1:
                curr_questions = questions[
                    (st.session_state.current_page - 1) * num_per_page : (
                        (st.session_state.current_page - 1) * num_per_page
                    )
                    + num_per_page
                ]

                with st.form(key="my_form"):
                    st.markdown(
                        "<h2 style='text-align: center; color: darkred;'>Prompt</h2>",
                        unsafe_allow_html=True,
                    )
                    st.write(prompt)
                    with st.container():
                        col1, col2 = st.columns(2)

                        col1.header("Answer 1")
                        col1.markdown(option1, unsafe_allow_html=True)
                        col2.header("Answer 2")
                        col2.markdown(option2, unsafe_allow_html=True)
                    st.divider()

                    with st.container():
                        col1, col2 = st.columns(2)
                        for question, id in zip(curr_questions, range(1, 6)):
                            # Replace sliders with radio buttons
                            col1.radio(f"{question}", [1, 2, 3, 4, 5], index=2, key=f"radio{id}1")
                            col2.radio(f"{question}", [1, 2, 3, 4, 5], index=2, key=f"radio{id}2")

                        if not st.session_state.current_page == 1:
                            with col1:
                                prev_page = st.form_submit_button("Previous Page")
                        with col2:
                            submitted = st.form_submit_button("Next Page")

                        st.progress(
                            st.session_state.current_page / total_pages,
                            text=f"Page {st.session_state.current_page} of {total_pages}",
                        )
                        st.markdown(
                            "<a href='#top'>Go to top</a>", unsafe_allow_html=True
                        )

                    if submitted:
                        for question, id in zip(curr_questions, range(1, 6)):
                            current_response["promptID"] = prompt_id
                            current_response["questionID"] = id
                            current_response[f"{id}_model1"] = st.session_state[f"radio{id}1"]
                            current_response[f"{id}_model2"] = st.session_state[f"radio{id}2"]

                            st.session_state["user_responses"]["responses"].append(
                                current_response
                            )

                        with open("user_responses.json", "w") as f:
                            json.dump(st.session_state["user_responses"], f)


                        st.session_state.current_page += 1
                        st.rerun()
                    if not st.session_state.current_page == 1:
                        if prev_page:
                            st.session_state.current_page -= 1
                            st.rerun()

        if st.session_state.current_page == total_pages + 1:
            next_prompt()


if __name__ == "__main__":
    main()