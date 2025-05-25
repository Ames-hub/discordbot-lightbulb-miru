document.addEventListener("DOMContentLoaded", () => {
    fetch('/api/buglist')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const dynamicList = document.getElementById("dynamic_list");

            if (!data || Object.keys(data).length === 0) {
                let text_paragraph = document.createElement("p");
                text_paragraph.textContent = "No bugs reported.";
                text_paragraph.style.color = "white";
                text_paragraph.style.textAlign = "center";
                dynamicList.appendChild(text_paragraph);
                return;
            }

            for (const reportId in data) {
                const bug = data[reportId];
                const link = document.createElement("a");
                // noinspection JSUnresolvedReference
                link.href = `/bug/${bug.report_id}`;
                // noinspection JSUnresolvedReference
                link.textContent = `Bug #${bug.report_id} | ${bug.stated_bug}`;
                link.className = "bug-link";

                const container = document.createElement("div");
                container.appendChild(link);
                dynamicList.appendChild(container);
            }
        })
        .catch(error => {
            console.error("Failed to fetch bug list:", error);
            const dynamicList = document.getElementById("dynamic_list");
            let text_paragraph = document.createElement("p");
            text_paragraph.textContent = "Error loading bug list.";
            text_paragraph.style.color = "red";
            text_paragraph.style.textAlign = "center";
            dynamicList.appendChild(text_paragraph);
        });
});