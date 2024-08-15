import streamlit as st
import sqlite3
import time
import pandas as pd

st.set_page_config(layout="wide", page_title="Mental Health Chatbot Evaluation")
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

# Connect to the database
conn = sqlite3.connect("main.db", check_same_thread=False)
curr = conn.cursor()

# Create user responses JSON in session_state
if "user_responses" not in st.session_state:
    st.session_state["user_responses"] = {}
    st.session_state["user_responses"]["responses"] = []

# Function to create the user table if it doesn't exist
def create_usertable():
    curr.execute(
        "CREATE TABLE IF NOT EXISTS userstable(username TEXT NOT NULL, password TEXT NOT NULL)"
    )
    conn.commit()

# Function to create the responses table if it doesn't exist
def create_responsestable():
    curr.execute(
        """CREATE TABLE IF NOT EXISTS responsestable(
            username TEXT NOT NULL, 
            promptID INTEGER NOT NULL,
            questionID INTEGER NOT NULL, 
            model1_response INTEGER, 
            model2_response INTEGER,
            PRIMARY KEY (username, promptID, questionID)
        )"""
    )
    conn.commit()

def create_questionstable():
    curr.execute(
        "CREATE TABLE IF NOT EXISTS questionstable("
        "questionID INTEGER PRIMARY KEY, "
        "Construct TEXT NOT NULL, "
        "Question TEXT NOT NULL)"
    )
    conn.commit()

def create_promptstable():
    curr.execute(
        "CREATE TABLE IF NOT EXISTS prompts_table(prompt_id INTEGER PRIMARY KEY AUTOINCREMENT, prompt TEXT NOT NULL)"
    )
    conn.commit()

def create_modelresponsestable():
    curr.execute(
        "CREATE TABLE IF NOT EXISTS model_responses_table(response_id INTEGER PRIMARY KEY AUTOINCREMENT, prompt_id INTEGER, model_type TEXT NOT NULL, response TEXT NOT NULL, FOREIGN KEY(prompt_id) REFERENCES prompts_table(prompt_id))"
    )
    conn.commit()

def add_userdata(username, password):
    curr.execute(
        "INSERT INTO userstable(username, password) VALUES (?, ?)", (username, password)
    )
    conn.commit()

def save_userresponse(username, prompt_id, responses):
    print(f"Saving responses for user {username}, prompt {prompt_id}: {responses}")
    for question_id, (model1_response, model2_response) in responses.items():
        curr.execute(
            "INSERT OR REPLACE INTO responsestable(username, promptID, questionID, model1_response, model2_response) VALUES (?, ?, ?, ?, ?)",
            (username, prompt_id, question_id, model1_response, model2_response),
        )
    conn.commit()
    print("Responses saved successfully")

def login_user(username, password):
    curr.execute(
        "SELECT * FROM userstable WHERE username =? AND password =?",
        (username, password),
    )
    fetch_data_users = curr.fetchall()
    return fetch_data_users

def get_userresponses(username):
    curr.execute(
        "SELECT questionID, model1_response, model2_response FROM responsestable WHERE username =?",
        (username,),
    )
    return curr.fetchall()

def get_questions():
    curr.execute("SELECT questionID, Question FROM questionstable")
    return curr.fetchall()

def get_prompts_and_responses():
    curr.execute(
        """
        SELECT pt.prompt_id, pt.prompt, 
               MAX(CASE WHEN mrt.model_type = 'model_1' THEN mrt.response END) as model1_response,
               MAX(CASE WHEN mrt.model_type = 'model_2' THEN mrt.response END) as model2_response
        FROM prompts_table pt
        LEFT JOIN model_responses_table mrt ON pt.prompt_id = mrt.prompt_id
        GROUP BY pt.prompt_id, pt.prompt
        ORDER BY pt.prompt_id
        """
    )
    return curr.fetchall()

def logout_user():
    st.session_state.clear()

# Initialize tables
create_usertable()
create_responsestable()
create_questionstable()
create_promptstable()
create_modelresponsestable()

questions_data = get_questions()
question_ids = [q[0] for q in questions_data]
questions = [q[1] for q in questions_data]
num_per_page = 5

total_pages_questions = len(questions) // num_per_page + (1 if len(questions) % num_per_page != 0 else 0)
prompts_data = get_prompts_and_responses()
total_pages_prompts = len(prompts_data)

def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state.logged_in:
        menu = ["Home", "Survey", "Logout"]
    else:
        menu = ["Home", "Login", "Signup"]

    choice = st.sidebar.selectbox("Menu", menu)

    if "last_active_time" not in st.session_state:
        st.session_state["last_active_time"] = time.time()

    # Initialize session state variables
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    if "current_question_page" not in st.session_state:
        st.session_state.current_question_page = 1

    if st.session_state.logged_in:
        username = st.session_state["username"]
        responses = get_userresponses(username)
        for questionID, model1_response, model2_response in responses:
            st.session_state[f"radio{questionID}1"] = model1_response
            st.session_state[f"radio{questionID}2"] = model2_response

    if choice == "Home":
        st.subheader("Home")
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

    elif choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            result = login_user(username, password)
            if result:
                st.success(f"Logged in as {username}")
                st.session_state.logged_in = True
                st.session_state["username"] = username
                st.experimental_rerun()
            else:
                st.warning("Incorrect Username/Password")
    
    elif choice == "Signup":
        username = st.text_input("Create Username")
        password = st.text_input("Create Password", type="password")
        if st.button("Signup"):
            add_userdata(username, password)
            st.success("Account created successfully!")
            st.info("Go to Login Menu to login")
    
    elif choice == "Logout":
        logout_user()
        st.experimental_rerun()

    elif choice == "Survey" and st.session_state.logged_in:
        if "current_question_page" not in st.session_state:
            st.session_state.current_question_page = 1

        prompts_and_responses = get_prompts_and_responses()
        total_pages = len(prompts_and_responses)

        if prompts_and_responses:
            current_page = st.session_state.current_page
            prompt_id, prompt, model1_response, model2_response = prompts_and_responses[current_page - 1]

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

            st.subheader("Prompt")
            st.write(prompt)

            st.subheader("Model Responses")
            col1, col2 = st.columns(2)

            with col1:
                st.write("Model 1 Response")
                st.write(model1_response)

            with col2:
                st.write("Model 2 Response")
                st.write(model2_response)

            st.subheader("Questions")
            num_per_page = 5
            total_question_pages = len(questions) // num_per_page + (1 if len(questions) % num_per_page != 0 else 0)
            start = (st.session_state.current_question_page - 1) * num_per_page
            end = min(start + num_per_page, len(questions))
            for i in range(start, end):
                question_id = question_ids[i]
                question = questions[i]
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"Q{question_id}: {question}")
                    response1 = st.radio(f"Rate Model 1 Response for Q{question_id}", [1, 2, 3, 4, 5], key=f"radio{question_id}_model1")

                with col2:
                    st.write(f"Q{question_id}: {question}")
                    response2 = st.radio(f"Rate Model 2 Response for Q{question_id}", [1, 2, 3, 4, 5], key=f"radio{question_id}_model2")

                # Save responses
                save_userresponse(
                    st.session_state["username"],
                    prompt_id,
                    {question_id: (response1, response2)}
                )

            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.session_state.current_question_page > 1:
                    if st.button("Previous Questions"):
                        st.session_state.current_question_page -= 1
                        st.experimental_rerun()

            with col3:
                if st.session_state.current_question_page < total_question_pages:
                    if st.button("Next Questions"):
                        st.session_state.current_question_page += 1
                        st.experimental_rerun()
                elif st.session_state.current_question_page == total_question_pages:
                    if st.button("Submit Survey"):
                        st.success("Survey completed! Thank you for your feedback.")
            
            # Progress bar and Go to top link
            st.progress(
                st.session_state.current_question_page / total_question_pages,
                text=f"Questions Page {st.session_state.current_question_page} of {total_question_pages}",
            )
            st.markdown(
                "<a href='#top'>Go to top</a>", unsafe_allow_html=True
            )

        else:
            st.error("No prompts and responses available. Please contact the administrator.")

if __name__ == "__main__":
    main()