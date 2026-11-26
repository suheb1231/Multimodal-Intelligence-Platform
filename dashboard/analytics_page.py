
# Streamlit library import karna.
import streamlit as st

# Pandas library import karna.
import pandas as pd

# Plotly chart library import karna.
import plotly.express as px


# Learning analytics page display karne ke liye function.
def render_analytics_page():

    # Dashboard ka main heading.
    st.title("Learning Analytics Dashboard")

    # Sample student data create karna.
    student_data = pd.DataFrame([
        {
            "Student": "Student 1",
            "Quiz Score": 85,
            "Study Hours": 12,
            "Activities": 20,
            "Difficulties": 1,
            "Recommendation": "Explore advanced ML"
        },
        {
            "Student": "Student 2",
            "Quiz Score": 45,
            "Study Hours": 5,
            "Activities": 10,
            "Difficulties": 3,
            "Recommendation": "Revise Python basics"
        },
        {
            "Student": "Student 3",
            "Quiz Score": 70,
            "Study Hours": 9,
            "Activities": 16,
            "Difficulties": 2,
            "Recommendation": "Practice SQL queries"
        }
    ])

    # All Students aur individual students ki list banana.
    student_options = ["All Students"] + student_data["Student"].tolist()

    # Student selector display karna.
    selected_student = st.selectbox(
        "Select Student",
        student_options
    )

    # Agar All Students select kiya gaya.
    if selected_student == "All Students":

        # Complete student dataset use karna.
        filtered_data = student_data.copy()

    # Agar individual student select kiya gaya.
    else:

        # Sirf selected student ka data filter karna.
        filtered_data = student_data[
            student_data["Student"] == selected_student
        ]

    # Dashboard metrics ke liye columns banana.
    col1, col2, col3 = st.columns(3)

    # Average quiz score calculate karna.
    average_score = filtered_data["Quiz Score"].mean()

    # Total study hours calculate karna.
    total_hours = filtered_data["Study Hours"].sum()

    # Total learning activities calculate karna.
    total_activities = filtered_data["Activities"].sum()

    # Average score display karna.
    col1.metric("Average Quiz Score", f"{average_score:.1f}%")

    # Study hours display karna.
    col2.metric("Study Hours", f"{total_hours}")

    # Learning activities display karna.
    col3.metric("Activities Completed", f"{total_activities}")

    # Performance chart ka heading.
    st.subheader("Student Performance")

    # Quiz scores ka bar chart banana.
    performance_chart = px.bar(
        filtered_data,
        x="Student",
        y="Quiz Score",
        title="Quiz Performance"
    )

    # Chart dashboard par display karna.
    st.plotly_chart(performance_chart, use_container_width=True)

    # Learning activity chart ka heading.
    st.subheader("Learning Activity")

    # Study hours ka chart banana.
    activity_chart = px.bar(
        filtered_data,
        x="Student",
        y="Study Hours",
        title="Study Hours"
    )

    # Activity chart display karna.
    st.plotly_chart(activity_chart, use_container_width=True)

    # Detected difficulties ka heading.
    st.subheader("Detected Learning Difficulties")

    # Difficulty information display karna.
    st.dataframe(
        filtered_data[
            ["Student", "Difficulties"]
        ],
        use_container_width=True
    )

    # AI recommendations ka heading.
    st.subheader("AI Recommendations")

    # Har selected student ki recommendation display karna.
    st.dataframe(
        filtered_data[
            ["Student", "Recommendation"]
        ],
        use_container_width=True
    )

    # Filtered dataset future integration ke liye return karna.
    return filtered_data
