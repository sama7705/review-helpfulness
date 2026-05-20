const API_URL = "http://127.0.0.1:8001";

function currentPage() {
    return document.body.dataset.page;
}

function setActiveNav() {
    const page = currentPage();
    document.querySelectorAll("[data-nav]").forEach((link) => {
        link.classList.toggle("active", link.dataset.nav === page);
    });
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text ?? "";
    return div.innerHTML;
}

function percent(value) {
    return `${Math.round(Number(value) * 100)}%`;
}

function highlightKeyword(text, keyword) {
    const safeText = escapeHtml(text);
    const cleanKeyword = keyword.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

    if (!cleanKeyword) {
        return safeText;
    }

    return safeText.replace(new RegExp(`(${cleanKeyword})`, "gi"), "<mark>$1</mark>");
}

function makeReviewSnippet(text, keyword, maxLength = 650) {
    if (!text || text.length <= maxLength) {
        return text || "";
    }

    const matchIndex = text.toLowerCase().indexOf(keyword.toLowerCase());
    const start = matchIndex > 90 ? matchIndex - 90 : 0;
    const snippet = text.slice(start, start + maxLength);
    const prefix = start > 0 ? "..." : "";
    const suffix = start + maxLength < text.length ? "..." : "";

    return `${prefix}${snippet}${suffix}`;
}

async function fetchJson(path, options = {}) {
    const response = await fetch(`${API_URL}${path}`, options);

    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
}

function renderBar(label, value, maxValue, color = "#f39ab8") {
    const width = maxValue > 0 ? Math.round((value / maxValue) * 100) : 0;

    return `
        <div class="bar-row">
            <span class="bar-label" title="${escapeHtml(label)}">${escapeHtml(label)}</span>
            <div class="bar-track">
                <div class="bar-fill" style="width: ${width}%; background: ${color};"></div>
            </div>
            <span class="bar-value">${value}</span>
        </div>
    `;
}

async function loadDashboard() {
    const data = await fetchJson("/stats");

    document.getElementById("totalReviews").textContent = data.total_reviews;
    document.getElementById("helpfulReviews").textContent = data.helpful_reviews;
    document.getElementById("notHelpfulReviews").textContent = data.not_helpful_reviews;
    document.getElementById("averageRating").textContent = data.average_rating;
    document.getElementById("numberOfGames").textContent = data.number_of_games;
    document.getElementById("mostReviewedItem").textContent = data.most_reviewed_item;
}

async function analyzeReview() {
    const textarea = document.getElementById("analysisInput");
    const result = document.getElementById("analysisResult");
    const review = textarea.value.trim();

    if (!review) {
        alert("Please paste a review first.");
        return;
    }

    result.classList.remove("empty-result");
    result.innerHTML = `<p class="mini-label">Analyzing review...</p>`;

    const data = await fetchJson("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ review })
    });

    const keywords = data.keywords && data.keywords.length
        ? data.keywords.map((word) => `<span class="pill">${escapeHtml(word)}</span>`).join("")
        : `<span class="pill">No keywords found</span>`;

    result.innerHTML = `
        <div class="analysis-header">
            <div>
                <span class="mini-label">Prediction</span>
                <h2 class="result-title">${escapeHtml(data.prediction)}</h2>
            </div>
            <span class="prediction-badge">${escapeHtml(data.sentiment)}</span>
        </div>

        <div class="probability-grid">
            <div class="probability-card">
                <span class="mini-label">Helpful Probability</span>
                <strong>${data.helpful_probability}</strong>
            </div>
            <div class="probability-card">
                <span class="mini-label">Not Helpful Probability</span>
                <strong>${data.not_helpful_probability}</strong>
            </div>
        </div>

        <div class="summary-box">
            <h3>Summary</h3>
            <p>${escapeHtml(data.summary)}</p>
        </div>

        <div class="summary-box">
            <h3>Keywords</h3>
            <div class="keyword-list">${keywords}</div>
        </div>
    `;
}

function setupAnalyzePage() {
    document.getElementById("analyzeButton").addEventListener("click", analyzeReview);
}

async function searchReviews() {
    const queryInput = document.getElementById("searchInput");
    const results = document.getElementById("searchResults");
    const query = queryInput.value.trim();

    if (!query) {
        alert("Please enter a search keyword.");
        return;
    }

    results.innerHTML = `
        <article class="empty-result panel">
            <span class="empty-icon">IR</span>
            <p>Searching reviews...</p>
        </article>
    `;

    const data = await fetchJson("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
    });

    if (!data.length) {
        results.innerHTML = `
            <article class="empty-result panel">
                <span class="empty-icon">0</span>
                <p>No reviews found for "${escapeHtml(query)}".</p>
            </article>
        `;
        return;
    }

    results.innerHTML = data.map((review) => `
        <article class="review-card">
            <h2>${escapeHtml(review.item_name)}</h2>
            <p class="review-text">${highlightKeyword(makeReviewSnippet(review.review_text, query), query)}</p>
            <div class="meta-row">
                <span class="pill">Rating: ${review.rating}</span>
                <span class="pill">Helpful Votes: ${review.helpful_votes}</span>
                <span class="pill">Dataset Label: ${escapeHtml(review.dataset_label)}</span>
                <span class="pill">AI Prediction: ${escapeHtml(review.ai_prediction)}</span>
                <span class="pill">Helpful Probability: ${review.helpful_probability}</span>
            </div>
        </article>
    `).join("");
}

function setupSearchPage() {
    const searchButton = document.getElementById("searchButton");
    const searchInput = document.getElementById("searchInput");

    searchButton.addEventListener("click", searchReviews);
    searchInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            searchReviews();
        }
    });
}

function renderComparisonStats(comparison) {
    document.getElementById("comparisonStats").innerHTML = `
        <article class="stat-card card-green">
            <span>Helpful Percentage</span>
            <strong>${comparison.helpful.percentage}%</strong>
        </article>
        <article class="stat-card card-pink">
            <span>Not Helpful Percentage</span>
            <strong>${comparison.not_helpful.percentage}%</strong>
        </article>
        <article class="stat-card card-purple">
            <span>Helpful Avg Rating</span>
            <strong>${comparison.helpful.average_rating}</strong>
        </article>
        <article class="stat-card card-lavender">
            <span>Not Helpful Avg Rating</span>
            <strong>${comparison.not_helpful.average_rating}</strong>
        </article>
    `;
}

async function loadInsights() {
    const [stats, comparison] = await Promise.all([
        fetchJson("/stats"),
        fetchJson("/comparison")
    ]);

    const maxLabelCount = Math.max(stats.helpful_reviews, stats.not_helpful_reviews);
    document.getElementById("labelChart").innerHTML = `
        ${renderBar("Helpful", stats.helpful_reviews, maxLabelCount, "#f39ab8")}
        ${renderBar("Not Helpful", stats.not_helpful_reviews, maxLabelCount, "#d9a7d7")}
    `;

    const items = Object.entries(stats.games || {});
    const maxItemCount = Math.max(...items.map((item) => item[1]), 1);
    document.getElementById("itemChart").innerHTML = items
        .map(([item, count]) => renderBar(item, count, maxItemCount))
        .join("");

    const ratingWidth = Math.round((stats.average_rating / 5) * 100);
    document.getElementById("ratingChart").innerHTML = `
        <div class="bar-row">
            <span class="bar-label">Average Rating</span>
            <div class="bar-track">
                <div class="bar-fill" style="width: ${ratingWidth}%; background: #f3b6a7;"></div>
            </div>
            <span class="bar-value">${stats.average_rating}/5</span>
        </div>
    `;

    renderComparisonStats(comparison);
    document.getElementById("comparisonText").textContent = comparison.explanation;
}

async function initPage() {
    setActiveNav();

    try {
        if (currentPage() === "dashboard") {
            await loadDashboard();
        }

        if (currentPage() === "analyze") {
            setupAnalyzePage();
        }

        if (currentPage() === "search") {
            setupSearchPage();
        }

        if (currentPage() === "insights") {
            await loadInsights();
        }
    } catch (error) {
        console.error(error);
        alert("Could not connect to the backend. Make sure FastAPI is running on http://127.0.0.1:8001.");
    }
}

initPage();
