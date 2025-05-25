async function markAsResolved(bug_id) {
    try {
        const response = await fetch("/api/bug/set_resolved", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({"bug_id": bug_id})
        });

        if (response.ok) {
            alert("Bug marked as resolved!");
            location.reload();
        } else {
            alert("Failed to mark as resolved.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Error sending request.");
    }

    try {
        const response = await fetch("/api/bot/order/alert_user", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "bug_id": bug_id
            })
        });

        if (response.ok) {
            alert("Bug marked as resolved!");
            location.reload();
        } else {
            alert("Failed to mark as resolved.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Error sending request.");
    }
}