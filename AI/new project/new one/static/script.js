document.addEventListener("DOMContentLoaded", function () {
    let inputBox = document.getElementById("autocomplete-input");
    let suggestionBox = document.getElementById("suggestion-box");

    inputBox.addEventListener("input", function () {
        let text = inputBox.value.trim();

        if (text === "") {
            suggestionBox.innerText = "Starting here...";
            return;
        }

        fetch("/autocomplete", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt: text })
        })
        .then(response => response.json())
        .then(data => {
            let suggestion = data.completion.trim();
            if (suggestion) {
                suggestionBox.innerText = suggestion;
            } else {
                suggestionBox.innerText = "";
            }
        });
    });

    inputBox.addEventListener("keydown", function (event) {
        if (event.key === "Tab" && suggestionBox.innerText.trim() !== "") {
            event.preventDefault(); // Prevent default tab behavior

            let text = inputBox.value.trim();
            let suggestion = suggestionBox.innerText;

            // Append the suggestion without overriding input
            inputBox.value = text + " " + suggestion;
            suggestionBox.innerText = ""; // Clear the suggestion box
        }
    });
});
