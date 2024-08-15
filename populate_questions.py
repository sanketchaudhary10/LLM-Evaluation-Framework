import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("main.db")
curr = conn.cursor()

# Function to create tables
def create_tables():
    curr.execute(
        """
        CREATE TABLE IF NOT EXISTS userstable (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """
    )
    curr.execute(
        """
        CREATE TABLE IF NOT EXISTS questionstable(
            questionID INTEGER PRIMARY KEY, 
            Question TEXT NOT NULL
        )
        """
    )
    curr.execute(
        """
        CREATE TABLE IF NOT EXISTS responsestable (
            response_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question_id INTEGER,
            model1_response INTEGER,
            model2_response INTEGER,
            FOREIGN KEY(user_id) REFERENCES userstable(user_id),
            FOREIGN KEY(question_id) REFERENCES questionstable(question_id)
        )
        """
    )
    curr.execute(
        """
        CREATE TABLE IF NOT EXISTS prompts_table (
            prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL
        )
        """
    )
    curr.execute(
        """
        CREATE TABLE IF NOT EXISTS model_responses_table (
            response_id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER,
            model_type TEXT NOT NULL,
            response TEXT NOT NULL,
            FOREIGN KEY(prompt_id) REFERENCES prompts_table(prompt_id)
        )
        """
    )
    conn.commit()

# Function to add a prompt
def add_prompt(prompt):
    curr.execute("INSERT INTO prompts_table (prompt) VALUES (?)", (prompt,))
    conn.commit()
    return curr.lastrowid

# Function to add a model response
def add_model_response(prompt_id, model_type, response):
    curr.execute(
        "INSERT INTO model_responses_table (prompt_id, model_type, response) VALUES (?, ?, ?)",
        (prompt_id, model_type, response),
    )
    conn.commit()

# Function to populate prompts and model responses from CSV
def populate_from_csv(csv_file):
    df = pd.read_csv(csv_file)
    for index, row in df.iterrows():
        prompt_id = add_prompt(row['Prompt'])
        add_model_response(prompt_id, 'model_1', row['model_1'])
        add_model_response(prompt_id, 'model_2', row['model_2'])


def load_questions_from_csv(file_path):
    questions_df = pd.read_csv(file_path)
    for index, row in questions_df.iterrows():
        curr.execute(
            "INSERT OR REPLACE INTO questionstable (questionID, Question) VALUES (?, ?)",
            (row['QuestionID'], row['Questions'])
        )
    conn.commit()


def main():
    create_tables()
    populate_from_csv("prompts.csv")
    print("Database and tables created, prompts and model responses added.")
    load_questions_from_csv("questions_new.csv")


if __name__ == "__main__":
    main()



# import sqlite3
# import pandas as pd

# def add_prompt(prompt):
#     with sqlite3.connect("main.db") as conn:
#         curr = conn.cursor()
#         curr.execute("INSERT INTO prompts_table (prompt) VALUES (?)", (prompt,))
#         conn.commit()
#         return curr.lastrowid

# def add_model_response(prompt_id, model_type, response):
#     with sqlite3.connect("main.db") as conn:
#         curr = conn.cursor()
#         curr.execute(
#             "INSERT INTO model_responses_table (prompt_id, model_type, response) VALUES (?, ?, ?)",
#             (prompt_id, model_type, response),
#         )
#         conn.commit()

# def populate_from_csv(csv_file):
#     df = pd.read_csv(csv_file)
#     for index, row in df.iterrows():
#         prompt_id = add_prompt(row['prompts'])
#         add_model_response(prompt_id, 'model_1', row['model_1'])
#         add_model_response(prompt_id, 'model_2', row['model_2'])

# if __name__ == "__main__":
#     populate_from_csv("/mnt/data/prompts.csv")
#     print("Database populated with prompts and model responses from CSV.")
