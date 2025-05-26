document.addEventListener("DOMContentLoaded", () => {
    fetch('/api/bans/list')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const dynamicList = document.getElementById("dynamic_ban_list");

            if (!data || Object.keys(data).length === 0) {
                let text_paragraph = document.createElement("p");
                text_paragraph.textContent = "No bans logged.";
                text_paragraph.style.color = "white";
                text_paragraph.style.textAlign = "center";
                dynamicList.appendChild(text_paragraph);
                return;
            }

            for (const caseId in data) {
                const ban = data[caseId];
                const link = document.createElement("a");
                // noinspection JSUnresolvedReference
                link.href = `/ban/${ban.case_id}`;
                // noinspection JSUnresolvedReference
                link.textContent = `ban #${ban.case_id}, ${ban.banned_username} | ${ban.reason}`;
                link.className = "ban-link";

                const container = document.createElement("div");
                container.appendChild(link);
                dynamicList.appendChild(container);
            }
        })
        .catch(error => {
            console.error("Failed to fetch ban list:", error);
            const dynamicList = document.getElementById("dynamic_ban_list");
            let text_paragraph = document.createElement("p");
            text_paragraph.textContent = "Error loading banned user list.";
            text_paragraph.style.color = "red";
            text_paragraph.style.textAlign = "center";
            dynamicList.appendChild(text_paragraph);
        });
});