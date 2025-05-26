async function markAsResolved(bug_id) {
    let resolved_bug
    try {
        const response = await fetch("/api/bug/set_resolved", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({"bug_id": bug_id})
        });

        if (response.ok) {
            resolved_bug = true
            location.reload();
        } else {
            resolved_bug = false
        }
    } catch (error) {
        console.error("Error:", error);
        resolved_bug = false
    }

    let resolution = document.getElementById("action_taken").value

    let alerted_user
    try {
        const response = await fetch("/api/bot/order/queue", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "bug_id": bug_id,
                "resolution": resolution,
                "order": "ALERT_USER_BUG_REPORT_RESOLUTION"
            })
        });

        if (response.ok) {
            alerted_user = true
            location.reload();
        } else {
            alerted_user = false
        }
    } catch (error) {
        console.error("Error:", error);
        alerted_user = false
    }

    if (alerted_user && resolved_bug) {
        alert("Bug marked as resolved and the reporter was informed of the outcome.")
    }
    else if (alerted_user) {
        alert("Reporter informed the bug is resolved. Couldn't mark as resolved in API.")
    }
    else if (resolved_bug) {
        alert("Bug marked as resolved. Couldn't alert reporter of outcome.")
    }
    else {
        alert("Could not mark bug as resolved and couldn't alert reporter of outcome.")
    }
}

