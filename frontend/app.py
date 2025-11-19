import streamlit as st
import requests
import pandas as pd

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="School Result Management System", layout="wide")

API_URL = "http://127.0.0.1:8000"

# ------------------ SESSION STATE ------------------
if "user" not in st.session_state:
    st.session_state["user"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "login"

st.title("🎓 School Result Management System")

# ======================================================
# 🔹 SIGNUP PAGE
# ======================================================
if st.session_state["page"] == "signup":
    st.subheader("📝 Create a New Account")

    full_name = st.text_input("Full Name")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["student", "admin"])

    if st.button("Sign Up"):
        try:
            res = requests.post(
                f"{API_URL}/auth/register",
                json={
                    "username": username,
                    "password": password,
                    "role": role,
                    "full_name": full_name,
                },
                timeout=10,
            )
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
        else:
            try:
                data = res.json()
            except ValueError:
                st.error(f"Unexpected server response:\n\n{res.text}")
            else:
                if res.status_code == 200:
                    st.success("✅ Account created successfully! You can now log in.")
                    st.session_state["page"] = "login"
                    st.rerun()
                else:
                    st.error(data.get("detail", "Signup failed."))

    if st.button("⬅️ Back to Login"):
        st.session_state["page"] = "login"
        st.rerun()

# ======================================================
# 🔹 LOGIN PAGE
# ======================================================
elif st.session_state["user"] is None and st.session_state["page"] == "login":
    st.subheader("🔐 Login to Your Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            res = requests.post(
                f"{API_URL}/auth/login",
                json={"username": username, "password": password},
                timeout=10,
            )
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
        else:
            if res.status_code in [200, 201]:
                user_data = res.json()
                st.session_state["user"] = {
                    "username": user_data.get("username", username),
                    "role": user_data.get("role", "student"),
                }
                st.success(
                    f"✅ Welcome {st.session_state['user']['username']}! "
                    f"Logged in as {st.session_state['user']['role'].capitalize()}."
                )
                st.rerun()
            else:
                try:
                    st.error(res.json().get("detail", "Invalid credentials"))
                except ValueError:
                    st.error("Unexpected server response.")

    st.write("Don't have an account?")
    if st.button("🆕 Sign Up"):
        st.session_state["page"] = "signup"
        st.rerun()

# ======================================================
# 🔹 MAIN DASHBOARD (AFTER LOGIN)
# ======================================================
else:
    user = st.session_state.get("user", {}) or {}
    role = user.get("role", "student")

    st.sidebar.title("📘 Menu")
    if role == "admin":
        menu = ["Dashboard", "Upload Results", "View Reports", "Logout"]
    else:
        menu = ["My Results", "Logout"]

    choice = st.sidebar.selectbox("Select Option", menu)
    st.sidebar.write(
        f"👤 Logged in as **{user.get('username', 'Unknown')}** ({role.capitalize()})"
    )

    # ==================================================
    # 🔸 Admin Dashboard (Ordered by Session → Term)
    # ==================================================
    if choice == "Dashboard" and role == "admin":
        st.subheader("📊 Admin Dashboard")

        resp = requests.get(f"{API_URL}/results/all")
        if resp.status_code != 200:
            st.error("No results found or unable to fetch data.")
        else:
            df = pd.DataFrame(resp.json())

            if df.empty:
                st.warning("No result records found.")
            else:
                # ✅ Term order mapping for consistent sorting
                term_order = {
                    "First Term": 1,
                    "1st Term": 1,
                    "Second Term": 2,
                    "2nd Term": 2,
                    "Third Term": 3,
                    "3rd Term": 3,
                }

                # Add default values if columns are missing
                if "term" not in df.columns:
                    df["term"] = "Unknown Term"
                if "session" not in df.columns:
                    df["session"] = "Unknown Session"

                # Sort the data
                df["term_order"] = df["term"].map(term_order).fillna(99)
                df = df.sort_values(by=["session", "term_order"], ascending=[False, True])

                # Filtering options
            session_value = df["session"].iloc[0] if not df.empty else "Unknown Session"            
            classes = sorted(df["student_class"].unique())
            selected_class = st.radio("Select Class:", classes, horizontal=True)


            terms = (
                df.loc[df["student_class"] == selected_class, "term"]
                .dropna()
                .unique()
                .tolist()
            )
            selected_term = st.radio("Select Term:", terms, horizontal=True)

            subjects = (
                df.loc[
                    (df["student_class"] == selected_class) &
                    (df["term"] == selected_term),
                    "subject"
                ]
                .dropna()
                .unique()
                .tolist()
            )
            selected_subject = st.radio("Select Subject:", subjects, horizontal=True)

            # ✅ Apply filters
            filtered_df = df[
                (df["student_class"] == selected_class)
                & (df["term"] == selected_term)
                & (df["subject"] == selected_subject)
            ]

            # --- DISPLAY RESULTS ---
            st.markdown(f"### 🗂 {selected_class} — {selected_term} ({session_value})")
            st.dataframe(
                filtered_df[["session", "term", "student_class", "subject", "name", "percentage"]]
            )

            # ✅ Summary — Average per Class per Term
            avg_scores = (
                filtered_df.groupby(["session", "term", "subject", "student_class"])["percentage"]
                .median()
                .reset_index()
                .rename(columns={"percentage": "Average (%)"})
            )

            st.write("### 📈 Average Score per Class per Term")
            st.dataframe(avg_scores)

            # ✅ Top Scorers per Subject
            top_scores = (
                filtered_df.loc[
                    filtered_df.groupby(["session", "term", "student_class", "subject"])["percentage"].idxmax()
                ]
                .sort_values(["session", "term", "student_class", "subject"])
                .reset_index(drop=True)
            )

            st.write("### 🏆 Highest Scorer per Subject per Class")
            st.dataframe(
                top_scores[["session", "term", "student_class", "subject", "name", "percentage"]]
            )
    # ==================================================
    # 🔸 Upload Results (Admin Only)
    # ==================================================
    elif choice == "Upload Results" and role == "admin":
        st.subheader("📤 Upload Student Results")
        st.info("📁 Filename should include term and session, e.g. First_Term_2024_2025.xlsx")

        uploaded_file = st.file_uploader("Upload Excel or CSV File", type=["xlsx", "csv"])

        if uploaded_file:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                res = requests.post(f"{API_URL}/results/upload", files=files, timeout=20)
            except requests.exceptions.RequestException as e:
                st.error(f"Upload error: {e}")
            else:
                try:
                    msg = res.json()
                except ValueError:
                    st.error("Invalid response from server.")
                else:
                    if res.status_code == 200:
                        term = msg.get("term", "Unknown Term")
                        session = msg.get("session", "Unknown Session")
                        st.markdown(
                            f"### 🗓️ **{term} — {session}**\n"
                            f"✅ {msg.get('message', 'Upload successful!')}"
                        )
                        st.success(f"Total Records Added: {msg.get('records_added', 0)}")
                    else:
                        st.error(msg.get("detail", "Upload failed."))

    # ==================================================
    # 🔸 View Reports (Admin Only)
    # ==================================================
    elif choice == "View Reports" and role == "admin":
        st.subheader("📈 Performance Reports")
        st.info("Detailed analytics coming soon...")

    # ==================================================
    # 🔸 Student Result Page
    # ==================================================
    elif choice == "My Results" and role == "student":
        st.subheader("🎯 My Academic Results")

        try:
            res = requests.get(
                f"{API_URL}/results/myResults",
                params={"username": user["username"]},
                timeout=10,
            )
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
        else:
            if res.status_code == 200:
                try:
                    df = pd.DataFrame(res.json())
                except ValueError:
                    st.error("Server returned invalid response.")
                    df = pd.DataFrame()
            else:
                st.warning("Unable to fetch your results at this time.")
                df = pd.DataFrame()

            if not df.empty:
                # Sort results by session → term
                term_order = {
                    "First Term": 1,
                    "1st Term": 1,
                    "Second Term": 2,
                    "2nd Term": 2,
                    "Third Term": 3,
                    "3rd Term": 3,
                }

                if "term" in df.columns:
                    df["term_order"] = df["term"].map(term_order)
                    df = df.sort_values(by=["session", "term_order"], ascending=[False, True])
                else:
                    df["term"] = "Unknown Term"
                    df = df.sort_values(by=["session"], ascending=False)

                st.write("### 📋 Your Scores (Ordered by Session & Term)")
                st.dataframe(df[["session", "term", "student_class", "subject", "percentage", "min_score_in_class", "median_score_in_class", "max_score_in_class"]])
            else:
                st.info("No results found for your account yet.")

    # ==================================================
    # 🔸 Logout
    # ==================================================
    elif choice == "Logout":
        st.session_state["user"] = None
        st.session_state["page"] = "login"
        st.success("✅ Logged out successfully.")
        st.rerun()
