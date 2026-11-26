
# AI recommendation ko review karne ke liye function.
def review_recommendation(recommendation, status):

    # Allowed review statuses define karna.
    allowed_statuses = ["approved", "rejected", "pending"]

    # Check karna ki diya gaya status valid hai ya nahi.
    if status not in allowed_statuses:

        # Invalid status hone par error return karna.
        return {
            "success": False,
            "message": "Invalid review status."
        }

    # Recommendation aur uska review status store karna.
    review_result = {
        "recommendation": recommendation,
        "status": status,
        "success": True
    }

    # Final review result return karna.
    return review_result
