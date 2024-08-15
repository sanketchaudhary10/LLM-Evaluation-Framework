import sqlite3

def create_tables():
    conn = sqlite3.connect("main.db")
    curr = conn.cursor()

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
        CREATE TABLE IF NOT EXISTS questionstable (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL
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
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database initialized with necessary tables.")
