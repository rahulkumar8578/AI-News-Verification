let currentUser = null;

let currentPrediction = null;
let currentScore = null;

let currentVerificationStatus = null;
let currentVerificationReason = "";
let currentVerificationConfidence = 0;
let currentWebAnswer = "";

let currentSources = [];

let toastTimeout = null;

document.addEventListener("DOMContentLoaded", function () {

    loadTheme();

    const loggedInUserId =
        localStorage.getItem("loggedInUserId") ||
        sessionStorage.getItem("loggedInUserId");

    if (loggedInUserId) {

        const users = getUsers();

        const user = users.find(function (u) {
            return u.id === loggedInUserId;
        });

        if (user) {
            currentUser = user;
            showApplication();
        } else {
            showLogin();
        }

    } else {
        showLogin();
    }

    setupCharacterCounters();
    setupSavedAccountSuggestion();
});

function getUsers() {

    try {

        return JSON.parse(
            localStorage.getItem(
                "newsVerificationUsers"
            )
        ) || [];

    } catch (error) {

        return [];
    }
}

function saveUsers(users) {

    localStorage.setItem(
        "newsVerificationUsers",
        JSON.stringify(users)
    );
}

function hideElement(element) {

    if (!element) return;

    element.classList.add("hidden");
    element.style.display = "none";
}

function showElement(
    element,
    displayType = "block"
) {

    if (!element) return;

    element.classList.remove("hidden");
    element.style.display = displayType;
}

function showLogin() {

    const loginPage =
        document.getElementById(
            "loginPage"
        );

    const signupPage =
        document.getElementById(
            "signupPage"
        );

    const forgotPage =
        document.getElementById(
            "forgotPage"
        );

    const app =
        document.getElementById(
            "app"
        );

    showElement(
        loginPage,
        "flex"
    );

    hideElement(signupPage);
    hideElement(forgotPage);
    hideElement(app);

    setTimeout(function () {
        showSavedAccountSuggestion();
    }, 100);
}

function showSignUp() {

    const loginPage =
        document.getElementById(
            "loginPage"
        );

    const signupPage =
        document.getElementById(
            "signupPage"
        );

    const forgotPage =
        document.getElementById(
            "forgotPage"
        );

    const app =
        document.getElementById(
            "app"
        );

    hideElement(loginPage);

    showElement(
        signupPage,
        "flex"
    );

    hideElement(forgotPage);
    hideElement(app);
}

function showForgotPassword() {

    const loginPage =
        document.getElementById(
            "loginPage"
        );

    const signupPage =
        document.getElementById(
            "signupPage"
        );

    const forgotPage =
        document.getElementById(
            "forgotPage"
        );

    const app =
        document.getElementById(
            "app"
        );

    hideElement(loginPage);
    hideElement(signupPage);

    showElement(
        forgotPage,
        "flex"
    );

    hideElement(app);
}

function signUp() {

    const nameElement =
        document.getElementById(
            "signupName"
        );

    const emailElement =
        document.getElementById(
            "signupEmail"
        );

    const passwordElement =
        document.getElementById(
            "signupPassword"
        );

    const name =
        nameElement
            ? nameElement.value.trim()
            : "";

    const email =
        emailElement
            ? emailElement.value
                .trim()
                .toLowerCase()
            : "";

    const password =
        passwordElement
            ? passwordElement.value
            : "";

    if (!name || !email || !password) {

        showToast(
            "Please fill all fields.",
            "error"
        );

        return;
    }

    if (!email.includes("@")) {

        showToast(
            "Please enter a valid email.",
            "error"
        );

        return;
    }

    if (password.length < 6) {

        showToast(
            "Password must contain at least 6 characters.",
            "error"
        );

        return;
    }

    const users = getUsers();

    const existingUser =
        users.find(function (user) {
            return user.email === email;
        });

    if (existingUser) {

        showToast(
            "This email is already registered.",
            "error"
        );

        return;
    }

    const newUser = {

        id: Date.now().toString(),

        name: name,

        email: email,

        password: password,

        createdAt:
            new Date().toISOString()
    };

    users.push(newUser);

    saveUsers(users);

    if (nameElement) {
        nameElement.value = "";
    }

    if (emailElement) {
        emailElement.value = "";
    }

    if (passwordElement) {
        passwordElement.value = "";
    }

    showToast(
        "Account created successfully!",
        "success"
    );

    setTimeout(function () {
        showLogin();
    }, 800);
}

function signIn() {

    const emailElement =
        document.getElementById(
            "loginEmail"
        );

    const passwordElement =
        document.getElementById(
            "loginPassword"
        );

    const rememberElement =
        document.getElementById(
            "rememberMe"
        );

    const email =
        emailElement
            ? emailElement.value
                .trim()
                .toLowerCase()
            : "";

    const password =
        passwordElement
            ? passwordElement.value
            : "";

    const rememberMe =
        rememberElement
            ? rememberElement.checked
            : false;

    if (!email || !password) {

        showToast(
            "Please enter email and password.",
            "error"
        );

        return;
    }

    const users = getUsers();

    const user =
        users.find(function (u) {

            return (
                u.email === email &&
                u.password === password
            );

        });

    if (!user) {

        showToast(
            "Invalid email or password.",
            "error"
        );

        return;
    }

    currentUser = user;

    localStorage.removeItem(
        "loggedInUserId"
    );

    sessionStorage.removeItem(
        "loggedInUserId"
    );

    if (rememberMe) {

        localStorage.setItem(
            "loggedInUserId",
            user.id
        );

        localStorage.setItem(
            "rememberEmail",
            email
        );

        localStorage.setItem(
            "rememberPassword",
            password
        );

    } else {

        sessionStorage.setItem(
            "loggedInUserId",
            user.id
        );

        localStorage.removeItem(
            "rememberEmail"
        );

        localStorage.removeItem(
            "rememberPassword"
        );
    }

    hideSavedAccountSuggestion();

    showToast(
        "Login successful!",
        "success"
    );

    setTimeout(function () {
        showApplication();
    }, 500);
}

function showSavedAccountSuggestion() {

    const emailInput =
        document.getElementById(
            "loginEmail"
        );

    const suggestion =
        document.getElementById(
            "savedAccountSuggestion"
        );

    const savedEmail =
        localStorage.getItem(
            "rememberEmail"
        );

    if (
        !emailInput ||
        !suggestion ||
        !savedEmail
    ) {
        return;
    }

    const typedEmail =
        emailInput.value
            .trim()
            .toLowerCase();

    const savedEmailLower =
        savedEmail
            .trim()
            .toLowerCase();

    if (
        typedEmail === "" ||
        savedEmailLower.startsWith(
            typedEmail
        )
    ) {

        const savedAccountEmail =
            document.getElementById(
                "savedAccountEmail"
            );

        if (savedAccountEmail) {
            savedAccountEmail.textContent =
                savedEmail;
        }

        suggestion.classList.remove(
            "hidden"
        );

    } else {

        suggestion.classList.add(
            "hidden"
        );
    }
}

function fillSavedAccount() {

    const savedEmail =
        localStorage.getItem(
            "rememberEmail"
        );

    const savedPassword =
        localStorage.getItem(
            "rememberPassword"
        );

    if (!savedEmail) {
        return;
    }

    const emailInput =
        document.getElementById(
            "loginEmail"
        );

    const passwordInput =
        document.getElementById(
            "loginPassword"
        );

    if (emailInput) {
        emailInput.value =
            savedEmail;
    }

    if (
        passwordInput &&
        savedPassword
    ) {
        passwordInput.value =
            savedPassword;
    }

    const rememberMe =
        document.getElementById(
            "rememberMe"
        );

    if (rememberMe) {
        rememberMe.checked = true;
    }

    hideSavedAccountSuggestion();

    if (passwordInput) {
        passwordInput.focus();
    }
}

function hideSavedAccountSuggestion() {

    const suggestion =
        document.getElementById(
            "savedAccountSuggestion"
        );

    if (suggestion) {

        suggestion.classList.add(
            "hidden"
        );
    }
}

function setupSavedAccountSuggestion() {

    const suggestion =
        document.getElementById(
            "savedAccountSuggestion"
        );

    const emailInput =
        document.getElementById(
            "loginEmail"
        );

    if (suggestion) {

        suggestion.addEventListener(
            "click",
            function () {
                fillSavedAccount();
            }
        );
    }

    if (emailInput) {

        emailInput.addEventListener(
            "input",
            function () {
                showSavedAccountSuggestion();
            }
        );

        emailInput.addEventListener(
            "focus",
            function () {
                showSavedAccountSuggestion();
            }
        );
    }

    showSavedAccountSuggestion();
}

function resetPassword() {

    const emailElement =
        document.getElementById(
            "forgotEmail"
        );

    const passwordElement =
        document.getElementById(
            "newPassword"
        );

    const email =
        emailElement
            ? emailElement.value
                .trim()
                .toLowerCase()
            : "";

    const newPassword =
        passwordElement
            ? passwordElement.value
            : "";

    if (!email || !newPassword) {

        showToast(
            "Please fill all fields.",
            "error"
        );

        return;
    }

    if (newPassword.length < 6) {

        showToast(
            "Password must contain at least 6 characters.",
            "error"
        );

        return;
    }

    const users = getUsers();

    const index =
        users.findIndex(function (user) {
            return user.email === email;
        });

    if (index === -1) {

        showToast(
            "Email not found.",
            "error"
        );

        return;
    }

    users[index].password =
        newPassword;

    saveUsers(users);

    const rememberedEmail =
        localStorage.getItem(
            "rememberEmail"
        );

    if (
        rememberedEmail &&
        rememberedEmail.toLowerCase() === email
    ) {

        localStorage.setItem(
            "rememberPassword",
            newPassword
        );
    }

    showToast(
        "Password updated successfully!",
        "success"
    );

    setTimeout(function () {
        showLogin();
    }, 800);
}

function togglePassword(
    inputId,
    eyeId
) {

    const input =
        document.getElementById(
            inputId
        );

    const eye =
        document.getElementById(
            eyeId
        );

    if (!input) return;

    if (
        input.type ===
        "password"
    ) {

        input.type =
            "text";

        if (eye) {
            eye.textContent =
                "🙈";
        }

    } else {

        input.type =
            "password";

        if (eye) {
            eye.textContent =
                "👁";
        }
    }
}

function logout() {

    currentUser = null;

    clearCurrentAnalysis(
        false
    );

    localStorage.removeItem(
        "loggedInUserId"
    );

    sessionStorage.removeItem(
        "loggedInUserId"
    );

    showLogin();

    showToast(
        "Logged out successfully.",
        "success"
    );
}

function showApplication() {

    const loginPage =
        document.getElementById(
            "loginPage"
        );

    const signupPage =
        document.getElementById(
            "signupPage"
        );

    const forgotPage =
        document.getElementById(
            "forgotPage"
        );

    const app =
        document.getElementById(
            "app"
        );

    hideElement(loginPage);
    hideElement(signupPage);
    hideElement(forgotPage);

    showElement(
        app,
        "block"
    );

    updateUserInformation();

    loadDashboard();

    loadProfile();

    showPage("dashboard");
}

function updateUserInformation() {

    if (!currentUser) return;

    const topUserName =
        document.getElementById(
            "topUserName"
        );

    if (topUserName) {

        topUserName.textContent =
            currentUser.name;
    }

    const profileAvatar =
        document.getElementById(
            "profileAvatar"
        );

    if (profileAvatar) {

        profileAvatar.textContent =
            getInitials(
                currentUser.name
            );
    }
}

function showPage(pageName) {

    const pages =
        document.querySelectorAll(
            ".page-section"
        );

    pages.forEach(function (page) {

        page.classList.add(
            "hidden"
        );

        page.style.display =
            "none";
    });

    const selectedPage =
        document.getElementById(
            pageName
        );

    if (selectedPage) {

        selectedPage.classList.remove(
            "hidden"
        );

        selectedPage.style.display =
            "block";
    }

    const pageTitle =
        document.getElementById(
            "pageTitle"
        );

    const titles = {

        dashboard:
            "Dashboard",

        analysis:
            "New Analysis",

        history:
            "Analysis History",

        profile:
            "My Profile"
    };

    if (pageTitle) {

        pageTitle.textContent =
            titles[pageName] ||
            "AI News Verification";
    }

    if (
        pageName ===
        "dashboard"
    ) {
        loadDashboard();
    }

    if (
        pageName ===
        "history"
    ) {
        loadHistory();
    }

    if (
        pageName ===
        "profile"
    ) {
        loadProfile();
    }
}

function toggleSidebar() {

    const sidebar =
        document.getElementById(
            "sidebar"
        );

    if (sidebar) {

        sidebar.classList.toggle(
            "active"
        );
    }
}

async function analyzeNews() {

    const headlineElement =
        document.getElementById(
            "headline"
        );

    const newsElement =
        document.getElementById(
            "news"
        );

    if (
        !headlineElement ||
        !newsElement
    ) {
        return;
    }

    const headline =
        headlineElement.value.trim();

    const news =
        newsElement.value.trim();

    if (
        !headline &&
        !news
    ) {

        showToast(
            "Please enter news headline or content.",
            "error"
        );

        return;
    }

    const result =
        document.getElementById(
            "analysisResult"
        );

    if (result) {

        result.classList.remove(
            "hidden"
        );

        result.style.display =
            "block";
    }

    const buttonText =
        document.getElementById(
            "analyzeButtonText"
        );

    if (buttonText) {

        buttonText.textContent =
            "Analyzing...";
    }

    try {

        const response =
            await fetch(
                "/predict",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({

                            headline:
                                headline,

                            news:
                                news
                        })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Prediction failed."
            );
        }

        currentPrediction =
            data.model_prediction ||
            "UNKNOWN";

        currentScore =
            Number(
                data.decision_score ||
                0
            );

        currentVerificationStatus =
            data.web_prediction ||
            "UNCERTAIN";

        currentVerificationReason =
            data.web_reason ||
            "";

        currentVerificationConfidence =
            Number(
                data.web_confidence ||
                0
            );

        currentWebAnswer =
            data.web_answer ||
            "";

        currentSources =
            Array.isArray(
                data.sources
            )
                ? data.sources
                : [];

        displayPrediction();

        displaySources(
            currentSources
        );

        saveHistory({

            headline:
                headline,

            news:
                news,

            prediction:
                currentPrediction,

            score:
                currentScore,

            verificationStatus:
                currentVerificationStatus,

            verificationReason:
                currentVerificationReason,

            verificationConfidence:
                currentVerificationConfidence,

            webAnswer:
                currentWebAnswer,

            sources:
                currentSources,

            date:
                new Date().toISOString()
        });

        showToast(
            "News analysis completed.",
            "success"
        );

    } catch (error) {

        console.error(
            "Prediction Error:",
            error
        );

        showToast(
            error.message ||
            "Error while analyzing news.",
            "error"
        );

    } finally {

        if (buttonText) {

            buttonText.textContent =
                "Check News";
        }
    }
}

function displayPrediction() {

    const predictionText =
        document.getElementById(
            "predictionText"
        );

    const modelPrediction =
        String(
            currentPrediction ||
            "UNKNOWN"
        ).toUpperCase();

    const verificationStatus =
        String(
            currentVerificationStatus ||
            "UNCERTAIN"
        ).toUpperCase();

    if (predictionText) {

        if (
            verificationStatus ===
            "TRUE"
        ) {

            predictionText.textContent =
                "TRUE";

            predictionText.className =
                "prediction-text prediction-real";

        } else if (

            verificationStatus ===
            "FALSE" ||

            verificationStatus ===
            "CONTRADICTED"

        ) {

            predictionText.textContent =
                "FALSE";

            predictionText.className =
                "prediction-text prediction-fake";

        } else {

            predictionText.textContent =
                "UNCERTAIN";

            predictionText.className =
                "prediction-text";
        }
    }

    const modelElement =
        document.getElementById(
            "modelPrediction"
        );

    if (modelElement) {

        modelElement.textContent =
            modelPrediction;
    }

    const verificationElement =
        document.getElementById(
            "verificationStatus"
        );

    if (verificationElement) {

        verificationElement.textContent =
            verificationStatus;

        verificationElement.className =
            getVerificationClass(
                verificationStatus
            );
    }

    const reasonElement =
        document.getElementById(
            "verificationReason"
        );

    if (reasonElement) {

        reasonElement.textContent =
            currentVerificationReason ||
            "No verification explanation available.";
    }

    const confidenceElement =
        document.getElementById(
            "verificationConfidence"
        );

    if (confidenceElement) {

        confidenceElement.textContent =
            currentVerificationConfidence +
            "%";
    }

    const verificationBar =
        document.getElementById(
            "verificationConfidenceBar"
        );

    if (verificationBar) {

        verificationBar.style.width =
            Math.min(
                Math.max(
                    currentVerificationConfidence,
                    0
                ),
                100
            ) +
            "%";
    }

    const webAnswerElement =
        document.getElementById(
            "webAnswer"
        );

    if (webAnswerElement) {

        webAnswerElement.textContent =
            currentWebAnswer ||
            "No web answer available.";
    }

    const scoreElement =
        document.getElementById(
            "decisionScore"
        );

    if (scoreElement) {

        scoreElement.textContent =
            Number(
                currentScore || 0
            ).toFixed(2);
    }

    const scoreBar =
        document.getElementById(
            "scoreBar"
        );

    if (scoreBar) {

        const strength =
            Math.min(
                Math.abs(
                    Number(
                        currentScore || 0
                    )
                ) * 10,
                100
            );

        scoreBar.style.width =
            strength +
            "%";
    }
}

function getVerificationClass(
    status
) {

    status =
        String(
            status || ""
        ).toUpperCase();

    if (
        status ===
        "TRUE"
    ) {

        return "verification-supported";
    }

    if (

        status ===
        "FALSE" ||

        status ===
        "CONTRADICTED"

    ) {

        return "verification-false";
    }

    return "verification-uncertain";
}

function displaySources(
    sources
) {

    const list =
        document.getElementById(
            "evidenceList"
        );

    if (!list) return;

    list.innerHTML = "";

    if (
        !sources ||
        sources.length === 0
    ) {

        list.innerHTML = `

            <div class="empty-state">

                No web evidence available.

            </div>

        `;

        return;
    }

    sources.forEach(
        function (
            source,
            index
        ) {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "evidence-item";

            const title =
                escapeHtml(
                    source.title ||
                    "Untitled Source"
                );

            const content =
                escapeHtml(
                    source.content ||
                    "No description available."
                );

            const url =
                source.url ||
                "";

            item.innerHTML = `

                <h4>

                    ${index + 1}.
                    ${title}

                </h4>

                <p>

                    ${content}

                </p>

                <div class="evidence-buttons">

                    <button
                        type="button"
                        class="secondary-btn"
                        data-url="${escapeHtml(url)}"
                        onclick="openEvidenceFromButton(this)">

                        Open Source

                    </button>

                    <button
                        type="button"
                        class="secondary-btn"
                        data-url="${escapeHtml(url)}"
                        onclick="copyEvidenceFromButton(this)">

                        Copy Link

                    </button>

                </div>

            `;

            list.appendChild(
                item
            );
        }
    );
}

function openEvidenceFromButton(
    button
) {

    const url =
        button.getAttribute(
            "data-url"
        );

    if (!url) {

        showToast(
            "Source link not available.",
            "error"
        );

        return;
    }

    window.open(
        url,
        "_blank"
    );
}

async function copyEvidenceFromButton(
    button
) {

    const url =
        button.getAttribute(
            "data-url"
        );

    if (!url) {

        showToast(
            "Source link not available.",
            "error"
        );

        return;
    }

    try {

        await navigator.clipboard
            .writeText(url);

        showToast(
            "Evidence link copied!",
            "success"
        );

    } catch (error) {

        showToast(
            "Unable to copy link.",
            "error"
        );
    }
}

async function copyEvidenceLink() {

    if (
        !currentSources ||
        currentSources.length === 0
    ) {

        showToast(
            "No evidence link available.",
            "error"
        );

        return;
    }

    const url =
        currentSources[0].url;

    if (!url) {

        showToast(
            "Source link not available.",
            "error"
        );

        return;
    }

    try {

        await navigator.clipboard
            .writeText(url);

        showToast(
            "Evidence link copied!",
            "success"
        );

    } catch (error) {

        showToast(
            "Unable to copy link.",
            "error"
        );
    }
}

async function copyResult() {

    if (!currentPrediction) {

        showToast(
            "Analyze news first.",
            "error"
        );

        return;
    }

    const headline =
        document.getElementById(
            "headline"
        )?.value || "";

    const news =
        document.getElementById(
            "news"
        )?.value || "";

    const text = `

AI News Verification Result

Headline:
${headline}

Model Prediction:
${currentPrediction}

Web Verification:
${currentVerificationStatus}

Verification Confidence:
${currentVerificationConfidence}%

Verification Reason:
${currentVerificationReason}

Decision Score:
${Number(
    currentScore || 0
).toFixed(2)}

Web Evidence:
${currentWebAnswer}

News:
${news}

`.trim();

    try {

        await navigator.clipboard
            .writeText(text);

        showToast(
            "Result copied!",
            "success"
        );

    } catch (error) {

        showToast(
            "Unable to copy result.",
            "error"
        );
    }
}

function shareWhatsApp() {

    if (!currentPrediction) {

        showToast(
            "Analyze news first.",
            "error"
        );

        return;
    }

    const headline =
        document.getElementById(
            "headline"
        )?.value || "";

    const text = `

AI News Verification

Headline:
${headline}

Model Prediction:
${currentPrediction}

Web Verification:
${currentVerificationStatus}

Verification Confidence:
${currentVerificationConfidence}%

Decision Score:
${Number(
    currentScore || 0
).toFixed(2)}

`.trim();

    window.open(

        "https://wa.me/?text=" +
        encodeURIComponent(
            text
        ),

        "_blank"
    );
}

function shareTelegram() {

    if (!currentPrediction) {

        showToast(
            "Analyze news first.",
            "error"
        );

        return;
    }

    const headline =
        document.getElementById(
            "headline"
        )?.value || "";

    const text = `

AI News Verification

Headline:
${headline}

Model Prediction:
${currentPrediction}

Web Verification:
${currentVerificationStatus}

Verification Confidence:
${currentVerificationConfidence}%

Decision Score:
${Number(
    currentScore || 0
).toFixed(2)}

`.trim();

    let evidenceUrl = "";

    if (
        currentSources &&
        currentSources.length > 0
    ) {

        evidenceUrl =
            currentSources[0].url ||
            "";
    }

    const url =
        "https://t.me/share/url?url=" +
        encodeURIComponent(
            evidenceUrl
        ) +
        "&text=" +
        encodeURIComponent(
            text
        );

    window.open(
        url,
        "_blank"
    );
}

function exportPDF() {

    if (!currentPrediction) {

        showToast(
            "Analyze news first.",
            "error"
        );

        return;
    }

    if (!window.jspdf) {

        showToast(
            "PDF library is not loaded.",
            "error"
        );

        return;
    }

    const {
        jsPDF
    } = window.jspdf;

    const pdf =
        new jsPDF();

    const headline =
        document.getElementById(
            "headline"
        )?.value || "";

    const news =
        document.getElementById(
            "news"
        )?.value || "";

    pdf.setFontSize(18);

    pdf.text(
        "AI News Verification Report",
        20,
        20
    );

    pdf.setFontSize(12);

    pdf.text(
        "Model Prediction: " +
        currentPrediction,
        20,
        35
    );

    pdf.text(
        "Web Verification: " +
        currentVerificationStatus,
        20,
        45
    );

    pdf.text(
        "Verification Confidence: " +
        currentVerificationConfidence +
        "%",
        20,
        55
    );

    pdf.text(
        "Decision Score: " +
        Number(
            currentScore || 0
        ).toFixed(2),
        20,
        65
    );

    let y = 80;

    pdf.text(
        "Verification Reason:",
        20,
        y
    );

    y += 8;

    const reasonLines =
        pdf.splitTextToSize(
            currentVerificationReason ||
            "Not available.",
            170
        );

    pdf.text(
        reasonLines,
        20,
        y
    );

    y +=
        reasonLines.length * 6 +
        10;

    pdf.text(
        "Headline:",
        20,
        y
    );

    y += 8;

    const headlineLines =
        pdf.splitTextToSize(
            headline,
            170
        );

    pdf.text(
        headlineLines,
        20,
        y
    );

    y +=
        headlineLines.length * 6 +
        10;

    pdf.text(
        "News Content:",
        20,
        y
    );

    y += 8;

    const newsLines =
        pdf.splitTextToSize(
            news,
            170
        );

    pdf.text(
        newsLines,
        20,
        y
    );

    y +=
        newsLines.length * 6 +
        15;

    pdf.text(
        "Web Evidence:",
        20,
        y
    );

    y += 8;

    const answerLines =
        pdf.splitTextToSize(
            currentWebAnswer ||
            "No web answer available.",
            170
        );

    pdf.text(
        answerLines,
        20,
        y
    );

    y +=
        answerLines.length * 6 +
        15;

    pdf.text(
        "Evidence Sources:",
        20,
        y
    );

    y += 8;

    currentSources.forEach(
        function (
            source,
            index
        ) {

            if (y > 270) {

                pdf.addPage();

                y = 20;
            }

            const title =
                source.title ||
                "Source";

            const lines =
                pdf.splitTextToSize(
                    title,
                    170
                );

            pdf.text(
                (index + 1) +
                ". " +
                lines.join(" "),
                20,
                y
            );

            y +=
                lines.length * 6 +
                4;
        }
    );

    pdf.save(
        "AI-News-Verification-Report.pdf"
    );

    showToast(
        "PDF downloaded!",
        "success"
    );
}

function downloadReport() {

    if (!currentPrediction) {

        showToast(
            "Analyze news first.",
            "error"
        );

        return;
    }

    const headline =
        document.getElementById(
            "headline"
        )?.value || "";

    const news =
        document.getElementById(
            "news"
        )?.value || "";

    const html = `

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>
AI News Verification Report
</title>

<style>

body {

    font-family: Arial;

    padding: 40px;

    line-height: 1.6;
}

h1 {

    text-align: center;
}

.section {

    margin-bottom: 25px;
}

.source {

    margin-bottom: 20px;
}

.status {

    font-size: 20px;

    font-weight: bold;
}

</style>

</head>

<body>

<h1>
AI News Verification Report
</h1>

<div class="section">

<h2>
Model Prediction
</h2>

<p class="status">

${escapeHtml(
    currentPrediction
)}

</p>

</div>

<div class="section">

<h2>
Web Verification
</h2>

<p class="status">

${escapeHtml(
    currentVerificationStatus
)}

</p>

<p>

<strong>
Confidence:
</strong>

${currentVerificationConfidence}%

</p>

<p>

<strong>
Reason:
</strong>

${escapeHtml(
    currentVerificationReason
)}

</p>

</div>

<div class="section">

<h2>
Decision Score
</h2>

<p>

${Number(
    currentScore || 0
).toFixed(2)}

</p>

</div>

<div class="section">

<h2>
Headline
</h2>

<p>

${escapeHtml(
    headline
)}

</p>

</div>

<div class="section">

<h2>
News
</h2>

<p>

${escapeHtml(
    news
)}

</p>

</div>

<div class="section">

<h2>
Web Evidence Summary
</h2>

<p>

${escapeHtml(
    currentWebAnswer ||
    "No web answer available."
)}

</p>

</div>

<h2>
Evidence Sources
</h2>

${currentSources.map(
    function (
        source,
        index
    ) {

        return `

        <div class="source">

            <strong>

                ${index + 1}.
                ${escapeHtml(
                    source.title ||
                    "Source"
                )}

            </strong>

            <p>

                ${escapeHtml(
                    source.content ||
                    ""
                )}

            </p>

            <a
                href="${escapeHtml(
                    source.url ||
                    "#"
                )}"
                target="_blank">

                Open Source

            </a>

        </div>

        `;

    }
).join("")}

</body>

</html>

`;

    const blob =
        new Blob(
            [html],
            {
                type:
                    "text/html"
            }
        );

    const url =
        URL.createObjectURL(
            blob
        );

    const link =
        document.createElement(
            "a"
        );

    link.href = url;

    link.download =
        "AI-News-Verification-Report.html";

    document.body.appendChild(
        link
    );

    link.click();

    link.remove();

    URL.revokeObjectURL(
        url
    );

    showToast(
        "Report downloaded!",
        "success"
    );
}

function printReport() {

    if (!currentPrediction) {

        showToast(
            "Analyze news first.",
            "error"
        );

        return;
    }

    const headline =
        document.getElementById(
            "headline"
        )?.value || "";

    const news =
        document.getElementById(
            "news"
        )?.value || "";

    const win =
        window.open(
            "",
            "_blank",
            "width=900,height=700"
        );

    if (!win) {

        showToast(
            "Please allow pop-ups.",
            "error"
        );

        return;
    }

    win.document.write(`

<!DOCTYPE html>

<html>

<head>

<title>
AI News Verification Report
</title>

<style>

body {

    font-family: Arial;

    padding: 40px;

    line-height: 1.6;
}

h1 {

    text-align: center;
}

.status {

    font-size: 20px;

    font-weight: bold;
}

.source {

    margin-bottom: 20px;
}

</style>

</head>

<body>

<h1>
AI News Verification Report
</h1>

<h2>
Model Prediction
</h2>

<p class="status">

${escapeHtml(
    currentPrediction
)}

</p>

<h2>
Web Verification
</h2>

<p class="status">

${escapeHtml(
    currentVerificationStatus
)}

</p>

<p>

<strong>
Confidence:
</strong>

${currentVerificationConfidence}%

</p>

<p>

<strong>
Reason:
</strong>

${escapeHtml(
    currentVerificationReason
)}

</p>

<h2>
Decision Score
</h2>

<p>

${Number(
    currentScore || 0
).toFixed(2)}

</p>

<h2>
Headline
</h2>

<p>

${escapeHtml(
    headline
)}

</p>

<h2>
News
</h2>

<p>

${escapeHtml(
    news
)}

</p>

<h2>
Web Evidence Summary
</h2>

<p>

${escapeHtml(
    currentWebAnswer ||
    "No web answer available."
)}

</p>

<h2>
Evidence Sources
</h2>

${currentSources.map(
    function (
        source,
        index
    ) {

        return `

        <div class="source">

            <strong>

                ${index + 1}.
                ${escapeHtml(
                    source.title ||
                    "Source"
                )}

            </strong>

            <br>

            ${escapeHtml(
                source.url ||
                ""
            )}

        </div>

        `;

    }
).join("")}

</body>

</html>

`);

    win.document.close();

    setTimeout(
        function () {
            win.print();
        },
        500
    );
}

function clearCurrentAnalysis(
    showMessage = true
) {

    const headline =
        document.getElementById(
            "headline"
        );

    const news =
        document.getElementById(
            "news"
        );

    const result =
        document.getElementById(
            "analysisResult"
        );

    if (headline) {
        headline.value = "";
    }

    if (news) {
        news.value = "";
    }

    if (result) {

        result.classList.add(
            "hidden"
        );

        result.style.display =
            "none";
    }

    currentPrediction = null;

    currentScore = null;

    currentVerificationStatus =
        null;

    currentVerificationReason =
        "";

    currentVerificationConfidence =
        0;

    currentWebAnswer =
        "";

    currentSources = [];

    const evidence =
        document.getElementById(
            "evidenceList"
        );

    if (evidence) {

        evidence.innerHTML = `

            <div class="empty-state">

                No evidence available yet.

            </div>

        `;
    }

    updateCharacterCounters();

    if (showMessage) {

        showToast(
            "Analysis cleared.",
            "success"
        );
    }
}

function clearAnalysis() {

    clearCurrentAnalysis(
        true
    );
}

function getHistory() {

    if (!currentUser) {
        return [];
    }

    try {

        return JSON.parse(
            localStorage.getItem(
                "history_" +
                currentUser.id
            )
        ) || [];

    } catch (error) {

        return [];
    }
}

function saveHistory(item) {

    if (!currentUser) return;

    const history =
        getHistory();

    history.unshift(
        item
    );

    localStorage.setItem(
        "history_" +
        currentUser.id,

        JSON.stringify(
            history
        )
    );
}

function loadHistory() {

    const list =
        document.getElementById(
            "historyList"
        );

    if (!list) return;

    const search =
        document.getElementById(
            "historySearch"
        )?.value
        .trim()
        .toLowerCase() ||
        "";

    const filter =
        document.getElementById(
            "historyFilter"
        )?.value
        .toUpperCase() ||
        "ALL";

    const history =
        getHistory();

    const filtered =
        history.filter(
            function (item) {

                const verification =
                    String(
                        item.verificationStatus ||
                        "UNCERTAIN"
                    ).toUpperCase();

                let webPrediction =
                    "UNCERTAIN";

                if (
                    verification ===
                    "TRUE"
                ) {

                    webPrediction =
                        "REAL";

                } else if (

                    verification ===
                    "FALSE" ||

                    verification ===
                    "CONTRADICTED"

                ) {

                    webPrediction =
                        "FAKE";
                }

                const matchesSearch =

                    !search ||

                    String(
                        item.headline ||
                        ""
                    )
                    .toLowerCase()
                    .includes(
                        search
                    ) ||

                    String(
                        item.news ||
                        ""
                    )
                    .toLowerCase()
                    .includes(
                        search
                    );

                const matchesFilter =
                    filter === "ALL" ||
                    webPrediction === filter;

                return (
                    matchesSearch &&
                    matchesFilter
                );
            }
        );

    list.innerHTML = "";

    if (
        filtered.length ===
        0
    ) {

        list.innerHTML = `

            <div class="empty-state">

                No analysis history available.

            </div>

        `;

        return;
    }

    filtered.forEach(
        function (item) {

            const originalIndex =
                history.indexOf(
                    item
                );

            const prediction =
                String(
                    item.prediction ||
                    ""
                ).toUpperCase();

            const verification =
                String(
                    item.verificationStatus ||
                    "UNCERTAIN"
                ).toUpperCase();

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "history-item";

            card.innerHTML = `

                <div class="history-content">

                    <h3>

                        ${escapeHtml(
                            item.headline ||
                            "Untitled News"
                        )}

                    </h3>

                    <p>

                        ${escapeHtml(
                            truncate(
                                item.news ||
                                "",
                                150
                            )
                        )}

                    </p>

                    <small>

                        ${
                            item.date
                                ? new Date(
                                    item.date
                                ).toLocaleString()
                                : ""
                        }

                    </small>

                </div>

                <div class="history-result">

                    <span class="history-badge
                        ${
                            prediction ===
                            "FAKE"
                                ? "fake"
                                : "real"
                        }">

                        Model:
                        ${escapeHtml(
                            prediction
                        )}

                    </span>

                    <span class="history-badge">

                        Web:
                        ${escapeHtml(
                            verification
                        )}

                    </span>

                    <span>

                        Score:
                        ${Number(
                            item.score ||
                            0
                        ).toFixed(2)}

                    </span>

                    <button
                        type="button"
                        onclick="deleteHistoryItem(${originalIndex})">

                        Delete

                    </button>

                </div>

            `;

            list.appendChild(
                card
            );
        }
    );
}

function deleteHistoryItem(
    index
) {

    const history =
        getHistory();

    if (
        index < 0 ||
        index >= history.length
    ) {
        return;
    }

    history.splice(
        index,
        1
    );

    localStorage.setItem(
        "history_" +
        currentUser.id,

        JSON.stringify(
            history
        )
    );

    loadHistory();

    showToast(
        "History item deleted.",
        "success"
    );
}

function clearAllHistory() {

    if (!currentUser) return;

    const confirmDelete =
        confirm(
            "Are you sure you want to clear all history?"
        );

    if (!confirmDelete) return;

    localStorage.removeItem(
        "history_" +
        currentUser.id
    );

    loadHistory();

    loadDashboard();

    showToast(
        "History cleared.",
        "success"
    );
}

function clearHistory() {

    clearAllHistory();
}

function exportHistoryCSV() {

    const history =
        getHistory();

    if (
        history.length ===
        0
    ) {

        showToast(
            "No history available.",
            "error"
        );

        return;
    }

    let csv =
        "Date,Headline,Model Prediction,Web Verification,Confidence,Score,News\n";

    history.forEach(
        function (item) {

            csv +=

                `"${csvEscape(
                    item.date ||
                    ""
                )}",` +

                `"${csvEscape(
                    item.headline ||
                    ""
                )}",` +

                `"${csvEscape(
                    item.prediction ||
                    ""
                )}",` +

                `"${csvEscape(
                    item.verificationStatus ||
                    ""
                )}",` +

                `"${csvEscape(
                    item.verificationConfidence ||
                    ""
                )}",` +

                `"${csvEscape(
                    item.score ||
                    ""
                )}",` +

                `"${csvEscape(
                    item.news ||
                    ""
                )}"\n`;
        }
    );

    const blob =
        new Blob(
            [csv],
            {
                type:
                    "text/csv;charset=utf-8;"
            }
        );

    const url =
        URL.createObjectURL(
            blob
        );

    const link =
        document.createElement(
            "a"
        );

    link.href = url;

    link.download =
        "AI-News-History.csv";

    document.body.appendChild(
        link
    );

    link.click();

    link.remove();

    URL.revokeObjectURL(
        url
    );

    showToast(
        "History exported!",
        "success"
    );
}

function loadDashboard() {

    if (!currentUser) return;

    const history =
        getHistory();

    const total =
        history.length;

    const real =
        history.filter(
            function (item) {

                return String(
                    item.prediction
                ).toUpperCase() ===
                "REAL";

            }
        ).length;

    const fake =
        history.filter(
            function (item) {

                return String(
                    item.prediction
                ).toUpperCase() ===
                "FAKE";

            }
        ).length;

    let average = 0;

    if (
        history.length >
        0
    ) {

        const totalScore =
            history.reduce(
                function (
                    sum,
                    item
                ) {

                    return (
                        sum +
                        Math.abs(
                            Number(
                                item.score ||
                                0
                            )
                        )
                    );

                },
                0
            );

        average =
            totalScore /
            history.length;
    }

    const totalElement =
        document.getElementById(
            "totalChecked"
        );

    const realElement =
        document.getElementById(
            "realCount"
        );

    const fakeElement =
        document.getElementById(
            "fakeCount"
        );

    const averageElement =
        document.getElementById(
            "averageScore"
        );

    if (totalElement) {
        totalElement.textContent =
            total;
    }

    if (realElement) {
        realElement.textContent =
            real;
    }

    if (fakeElement) {
        fakeElement.textContent =
            fake;
    }

    if (averageElement) {
        averageElement.textContent =
            average.toFixed(2);
    }

    updateChart(
        real,
        fake,
        total
    );

    loadRecentAnalyses(
        history
    );
}

function updateChart(
    real,
    fake,
    total
) {

    const realBar =
        document.getElementById(
            "realBar"
        );

    const fakeBar =
        document.getElementById(
            "fakeBar"
        );

    const realValue =
        document.getElementById(
            "realBarValue"
        );

    const fakeValue =
        document.getElementById(
            "fakeBarValue"
        );

    let realPercent = 0;

    let fakePercent = 0;

    if (total > 0) {

        realPercent =
            (real / total) *
            100;

        fakePercent =
            (fake / total) *
            100;
    }

    if (realBar) {

        realBar.style.width =
            realPercent +
            "%";
    }

    if (fakeBar) {

        fakeBar.style.width =
            fakePercent +
            "%";
    }

    if (realValue) {

        realValue.textContent =
            real +
            " (" +
            realPercent.toFixed(1) +
            "%)";
    }

    if (fakeValue) {

        fakeValue.textContent =
            fake +
            " (" +
            fakePercent.toFixed(1) +
            "%)";
    }
}

function loadRecentAnalyses(
    history
) {

    const container =
        document.getElementById(
            "recentAnalyses"
        );

    if (!container) return;

    container.innerHTML = "";

    const recent =
        history.slice(
            0,
            5
        );

    if (
        recent.length ===
        0
    ) {

        container.innerHTML = `

            <div class="empty-state">

                No analyses yet.

            </div>

        `;

        return;
    }

    recent.forEach(
        function (item) {

            const prediction =
                String(
                    item.prediction ||
                    ""
                ).toUpperCase();

            const verification =
                String(
                    item.verificationStatus ||
                    "UNCERTAIN"
                ).toUpperCase();

            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "recent-analysis";

            div.innerHTML = `

                <div>

                    <strong>

                        ${escapeHtml(
                            item.headline ||
                            "Untitled"
                        )}

                    </strong>

                    <small>

                        ${
                            item.date
                                ? new Date(
                                    item.date
                                ).toLocaleString()
                                : ""
                        }

                    </small>

                </div>

                <span class="
                    history-badge
                    ${
                        prediction ===
                        "FAKE"
                            ? "fake"
                            : "real"
                    }
                ">

                    Model:
                    ${escapeHtml(
                        prediction
                    )}

                </span>

                <span class="
                    history-badge
                ">

                    Web:
                    ${escapeHtml(
                        verification
                    )}

                </span>

            `;

            container.appendChild(
                div
            );
        }
    );
}

function loadProfile() {

    if (!currentUser) return;

    const avatar =
        document.getElementById(
            "profileAvatarLarge"
        );

    const name =
        document.getElementById(
            "profileName"
        );

    const nameInput =
        document.getElementById(
            "profileNameInput"
        );

    const emailInput =
        document.getElementById(
            "profileEmailInput"
        );

    if (avatar) {

        avatar.textContent =
            getInitials(
                currentUser.name
            );
    }

    if (name) {

        name.textContent =
            currentUser.name;
    }

    if (nameInput) {

        nameInput.value =
            currentUser.name;
    }

    if (emailInput) {

        emailInput.value =
            currentUser.email;
    }
}

function updateProfile() {

    if (!currentUser) return;

    const nameInput =
        document.getElementById(
            "profileNameInput"
        );

    const name =
        nameInput
            ? nameInput.value.trim()
            : "";

    if (!name) {

        showToast(
            "Name cannot be empty.",
            "error"
        );

        return;
    }

    const users =
        getUsers();

    const index =
        users.findIndex(
            function (user) {

                return (
                    user.id ===
                    currentUser.id
                );

            }
        );

    if (index === -1) return;

    users[index].name =
        name;

    saveUsers(users);

    currentUser =
        users[index];

    updateUserInformation();

    loadProfile();

    showToast(
        "Profile updated successfully!",
        "success"
    );
}

function toggleTheme() {

    document.body.classList.toggle(
        "dark-mode"
    );

    const dark =
        document.body.classList.contains(
            "dark-mode"
        );

    localStorage.setItem(
        "newsTheme",
        dark
            ? "dark"
            : "light"
    );
}

function loadTheme() {

    const theme =
        localStorage.getItem(
            "newsTheme"
        );

    if (
        theme ===
        "dark"
    ) {

        document.body.classList.add(
            "dark-mode"
        );
    }
}

function showToast(
    message,
    type = "success"
) {

    const container =
        document.getElementById(
            "toastContainer"
        );

    if (!container) {

        console.log(
            message
        );

        return;
    }

    const oldToast =
        document.getElementById(
            "toast"
        );

    if (oldToast) {

        oldToast.remove();
    }

    if (toastTimeout) {

        clearTimeout(
            toastTimeout
        );

        toastTimeout =
            null;
    }

    const toast =
        document.createElement(
            "div"
        );

    toast.id =
        "toast";

    toast.className =
        "toast " +
        type;

    toast.textContent =
        message;

    container.appendChild(
        toast
    );

    requestAnimationFrame(
        function () {

            toast.classList.add(
                "show"
            );
        }
    );

    toastTimeout =
        setTimeout(
            function () {

                toast.classList.remove(
                    "show"
                );

                setTimeout(
                    function () {

                        if (
                            toast.parentNode
                        ) {

                            toast.remove();
                        }

                    },
                    300
                );

                toastTimeout =
                    null;

            },
            5000
        );
}

function setupCharacterCounters() {

    const headline =
        document.getElementById(
            "headline"
        );

    const news =
        document.getElementById(
            "news"
        );

    if (headline) {

        headline.addEventListener(
            "input",
            updateCharacterCounters
        );
    }

    if (news) {

        news.addEventListener(
            "input",
            updateCharacterCounters
        );
    }

    updateCharacterCounters();
}

function updateCharacterCounters() {

    const headline =
        document.getElementById(
            "headline"
        );

    const news =
        document.getElementById(
            "news"
        );

    const headlineCount =
        document.getElementById(
            "headlineCount"
        );

    const newsCount =
        document.getElementById(
            "newsCount"
        );

    if (
        headlineCount &&
        headline
    ) {

        headlineCount.textContent =
            headline.value.length;
    }

    if (
        newsCount &&
        news
    ) {

        newsCount.textContent =
            news.value.length;
    }
}

function escapeHtml(text) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        String(text);

    return div.innerHTML;
}

function truncate(
    text,
    length
) {

    text =
        String(
            text || ""
        );

    if (
        text.length <=
        length
    ) {

        return text;
    }

    return (
        text.substring(
            0,
            length
        ) +
        "..."
    );
}

function getInitials(name) {

    const words =
        String(
            name || ""
        )
        .trim()
        .split(/\s+/);

    if (
        words.length ===
        0
    ) {

        return "U";
    }

    if (
        words.length ===
        1
    ) {

        return words[0]
            .substring(
                0,
                2
            )
            .toUpperCase();
    }

    return (
        words[0][0] +
        words[1][0]
    ).toUpperCase();
}

function csvEscape(value) {

    return String(
        value || ""
    ).replace(
        /"/g,
        '""'
    );
}

window.showLogin =
    showLogin;

window.showSignUp =
    showSignUp;

window.showForgotPassword =
    showForgotPassword;

window.signUp =
    signUp;

window.signIn =
    signIn;

window.resetPassword =
    resetPassword;

window.togglePassword =
    togglePassword;

window.logout =
    logout;

window.showPage =
    showPage;

window.toggleSidebar =
    toggleSidebar;

window.analyzeNews =
    analyzeNews;

window.openEvidenceFromButton =
    openEvidenceFromButton;

window.copyEvidenceFromButton =
    copyEvidenceFromButton;

window.copyEvidenceLink =
    copyEvidenceLink;

window.copyResult =
    copyResult;

window.shareWhatsApp =
    shareWhatsApp;

window.shareTelegram =
    shareTelegram;

window.exportPDF =
    exportPDF;

window.downloadReport =
    downloadReport;

window.printReport =
    printReport;

window.clearAnalysis =
    clearAnalysis;

window.loadHistory =
    loadHistory;

window.deleteHistoryItem =
    deleteHistoryItem;

window.clearAllHistory =
    clearAllHistory;

window.clearHistory =
    clearHistory;

window.exportHistoryCSV =
    exportHistoryCSV;

window.loadDashboard =
    loadDashboard;

window.loadProfile =
    loadProfile;

window.updateProfile =
    updateProfile;

window.toggleTheme =
    toggleTheme;

window.showSavedAccountSuggestion =
    showSavedAccountSuggestion;

window.fillSavedAccount =
    fillSavedAccount;

window.hideSavedAccountSuggestion =
    hideSavedAccountSuggestion;

window.setupSavedAccountSuggestion =
    setupSavedAccountSuggestion;

window.showToast =
    showToast;