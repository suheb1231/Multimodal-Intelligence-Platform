
# Streamlit library import karna.
import streamlit as st

# Existing review manager import karna.
from review.review_manager import review_recommendation


# Review dashboard display karne ke liye function.
def render_review_page():

    # Dashboard heading display karna.
    st.title("Recommendation Review Dashboard")

    # Sample AI recommendations create karna.
    recommendations = [
        "Revise Python fundamentals",
        "Practice SQL queries",
        "Explore Machine Learning basics"
    ]

    # Har recommendation ke liye review interface banana.
    for index, recommendation in enumerate(recommendations):

        # Recommendation ko separate section mein display karna.
        with st.container():

            # Recommendation heading display karna.
            st.subheader(f"Recommendation {index + 1}")

            # Recommendation ka text display karna.
            st.write(recommendation)

            # Approve aur reject buttons ke liye columns banana.
            col1, col2 = st.columns(2)

            # Approve button display karna.
            with col1:

                # Button click hone par recommendation approve karna.
                if st.button("Approve", key=f"approve_{index}"):

                    # Review manager ko approved status bhejna.
                    result = review_recommendation(
                        recommendation,
                        "approved"
                    )

                    # Review result display karna.
                    st.success(result["message"] if "message" in result else "Recommendation approved.")

            # Reject button display karna.
            with col2:

                # Button click hone par recommendation reject karna.
                if st.button("Reject", key=f"reject_{index}"):

                    # Review manager ko rejected status bhejna.
                    result = review_recommendation(
                        recommendation,
                        "rejected"
                    )

                    # Review result display karna.
                    st.warning(result["message"] if "message" in result else "Recommendation rejected.")
