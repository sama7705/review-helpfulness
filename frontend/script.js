async function predictReview() {
    const reviewText = document.getElementById("reviewInput").value;

    if (reviewText.trim() === "") {
        alert("Please enter a review first.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: reviewText
            })
        });

        const data = await response.json();

        document.getElementById("originalText").innerText = data.review;
        document.getElementById("processedText").innerText = data.processed_text;
        document.getElementById("prediction").innerText = data.prediction;
        document.getElementById("confidence").innerText = (data.confidence * 100).toFixed(1) + "%";

        document.getElementById("resultBox").classList.remove("hidden");

    } catch (error) {
        alert("Error connecting to backend. Make sure the backend server is running.");
        console.log(error);
    }
}