const resumeForm = document.getElementById("resumeForm");

resumeForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const fileInput = document.getElementById("resumeFile");
    const result = document.getElementById("result");
    const file = fileInput.files[0];

    if (!file) {
        result.textContent = "Please select a PDF resume first.";
        return;
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
        result.textContent = "Please select a PDF file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    result.textContent = "Analyzing your resume... Please wait.";

    try {
        const response = await fetch(
            "https://ai-careermate-mbgj.onrender.com/upload-resume",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Resume analysis failed.");
        }

        // Save detected skills for Job Match Analysis
        const detectedSkills = Array.isArray(data.skills)
            ? data.skills
            : [];

        sessionStorage.setItem(
            "careerMateResumeSkills",
            detectedSkills.join(", ")
        );

        // Clear previous results
        result.replaceChildren();

        // Resume analysis heading
        const heading = document.createElement("h2");
        heading.textContent = "Resume Analysis Results";
        result.appendChild(heading);

        // Filename
        const filename = document.createElement("p");
        filename.textContent = "Filename: " + data.filename;
        result.appendChild(filename);

        // File size
        const fileSize = document.createElement("p");
        fileSize.textContent =
            "File size: " + (data.size_bytes / 1024).toFixed(2) + " KB";
        result.appendChild(fileSize);

        // Detected skills
        const skillsHeading = document.createElement("h3");
        skillsHeading.textContent =
            "Detected Skills (" + detectedSkills.length + ")";
        result.appendChild(skillsHeading);

        const skillsList = document.createElement("ul");

        if (detectedSkills.length > 0) {
            detectedSkills.forEach(function (skill) {
                const item = document.createElement("li");
                item.textContent = skill;
                skillsList.appendChild(item);
            });
        } else {
            const item = document.createElement("li");
            item.textContent = "No listed skills were detected.";
            skillsList.appendChild(item);
        }

        result.appendChild(skillsList);

        // Resume score
        const headingScore = document.createElement("h3");
        headingScore.textContent =
            "Resume Completeness Score: " +
            data.resume_score.score +
            "/" +
            data.resume_score.maximum_score;

        result.appendChild(headingScore);

        // Score breakdown
        const breakdownHeading = document.createElement("h3");
        breakdownHeading.textContent = "Score Breakdown";
        result.appendChild(breakdownHeading);

        const breakdownList = document.createElement("ul");
        const breakdown = data.resume_score.breakdown;

        const categories = [
            ["Technical Skills", breakdown.technical_skills, 30],
            ["Education", breakdown.education, 20],
            ["Projects", breakdown.projects, 20],
            ["Certifications", breakdown.certifications, 15],
            ["Contact Information", breakdown.contact_information, 15]
        ];

        categories.forEach(function (category) {
            const item = document.createElement("li");
            item.textContent =
                category[0] + ": " + category[1] + "/" + category[2];

            breakdownList.appendChild(item);
        });

        result.appendChild(breakdownList);

        // Suggestions
        const suggestionsHeading = document.createElement("h3");
        suggestionsHeading.textContent = "Suggestions for Improvement";
        result.appendChild(suggestionsHeading);

        const suggestionsList = document.createElement("ul");

        const suggestions =
            data.resume_score.suggestions || [];

        suggestions.forEach(function (suggestion) {
            const item = document.createElement("li");
            item.textContent = suggestion;
            suggestionsList.appendChild(item);
        });

        result.appendChild(suggestionsList);

        // Disclaimer
        const note = document.createElement("p");
        note.textContent =
            "Note: This is a basic rule-based completeness score, " +
            "not a measure of your employability.";

        result.appendChild(note);

        // Continue to Job Match Analysis
        const jobMatchButton = document.createElement("button");
        jobMatchButton.type = "button";
        jobMatchButton.textContent = "Continue to Job Match Analysis";

        jobMatchButton.addEventListener("click", function () {
            window.location.href = "job-match.html";
        });

        result.appendChild(jobMatchButton);

    } catch (error) {
        result.textContent = "Analysis error: " + error.message;
    }
});