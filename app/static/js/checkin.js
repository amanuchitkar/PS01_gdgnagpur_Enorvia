/**
 * Kindered Emotional Check-in Assessment
 * 10 original multiple-choice questions covering mood, sleep, energy,
 * anxiety, stress, concentration, motivation, appetite, social interaction,
 * and emotional balance.
 *
 * Scoring: Each answer maps to 0-3 points (higher = better wellbeing).
 * Total max = 30. Categories:
 *   25-30: Thriving
 *   18-24: Doing Well
 *   10-17: Needs Attention
 *    0-9:  High Emotional Strain
 */

const questions = [
    {
        id: 'mood',
        text: 'Over the past two weeks, how would you describe your overall mood?',
        options: [
            { label: 'Mostly positive and upbeat', score: 3 },
            { label: 'Generally okay with some low moments', score: 2 },
            { label: 'Frequently low or flat', score: 1 },
            { label: 'Persistently down or hopeless', score: 0 },
        ]
    },
    {
        id: 'sleep',
        text: 'How would you rate the quality of your sleep recently?',
        options: [
            { label: 'I sleep well and wake feeling rested', score: 3 },
            { label: 'Decent sleep most nights, occasional trouble', score: 2 },
            { label: 'Often restless, waking frequently or too early', score: 1 },
            { label: 'Very poor — I rarely feel rested', score: 0 },
        ]
    },
    {
        id: 'energy',
        text: 'How are your energy levels throughout a typical day?',
        options: [
            { label: 'Steady energy that carries me through the day', score: 3 },
            { label: 'Adequate but I hit a slump in the afternoon', score: 2 },
            { label: 'Low energy that makes daily tasks harder', score: 1 },
            { label: 'Exhausted most of the time, even after rest', score: 0 },
        ]
    },
    {
        id: 'anxiety',
        text: 'How often do you feel worried, nervous, or on edge?',
        options: [
            { label: 'Rarely — I feel generally calm', score: 3 },
            { label: 'Occasionally, but I manage it well', score: 2 },
            { label: 'Often, and it sometimes disrupts my day', score: 1 },
            { label: 'Almost constantly — it is hard to relax', score: 0 },
        ]
    },
    {
        id: 'stress',
        text: 'How well are you coping with the demands and pressures in your life?',
        options: [
            { label: 'Handling things comfortably', score: 3 },
            { label: 'Managing, though it takes effort', score: 2 },
            { label: 'Feeling stretched and overwhelmed at times', score: 1 },
            { label: 'Completely overwhelmed — I struggle to cope', score: 0 },
        ]
    },
    {
        id: 'concentration',
        text: 'How is your ability to focus and concentrate on tasks?',
        options: [
            { label: 'Clear-headed and able to stay on track', score: 3 },
            { label: 'Mostly focused, occasional distractions', score: 2 },
            { label: 'Difficulty concentrating — my mind wanders a lot', score: 1 },
            { label: 'Very hard to focus on anything at all', score: 0 },
        ]
    },
    {
        id: 'motivation',
        text: 'How motivated do you feel to engage in your daily activities or interests?',
        options: [
            { label: 'Enthusiastic and looking forward to things', score: 3 },
            { label: 'Reasonably motivated most days', score: 2 },
            { label: 'Low drive — I push myself through routines', score: 1 },
            { label: 'No interest or pleasure in doing things', score: 0 },
        ]
    },
    {
        id: 'appetite',
        text: 'Have you noticed changes in your appetite or eating patterns?',
        options: [
            { label: 'My appetite is normal and stable', score: 3 },
            { label: 'Slight changes, but nothing significant', score: 2 },
            { label: 'Noticeable increase or decrease in appetite', score: 1 },
            { label: 'Major changes — eating far too much or too little', score: 0 },
        ]
    },
    {
        id: 'social',
        text: 'How connected do you feel to the people around you?',
        options: [
            { label: 'I feel supported and enjoy socializing', score: 3 },
            { label: 'Somewhat connected, though I could reach out more', score: 2 },
            { label: 'Withdrawn — I avoid people more than usual', score: 1 },
            { label: 'Very isolated and disconnected from others', score: 0 },
        ]
    },
    {
        id: 'balance',
        text: 'How stable do your emotions feel day-to-day?',
        options: [
            { label: 'Balanced — I handle ups and downs smoothly', score: 3 },
            { label: 'Mostly even with occasional mood shifts', score: 2 },
            { label: 'Unpredictable — emotions change quickly', score: 1 },
            { label: 'Intense swings that feel hard to control', score: 0 },
        ]
    },
];

let currentIndex = 0;
let answers = new Array(questions.length).fill(null); // stores selected option index

/* ======= SECTION MANAGEMENT ======= */

function startAssessment() {
    document.getElementById('landing-section').classList.add('hidden');
    document.getElementById('assessment-section').classList.remove('hidden');
    renderQuestion();
}

/* ======= QUESTION RENDERING ======= */

function renderQuestion() {
    const q = questions[currentIndex];
    document.getElementById('question-text').textContent = q.text;

    // Progress
    const progress = Math.round(((currentIndex + 1) / questions.length) * 100);
    document.getElementById('progress-bar').style.width = `${progress}%`;
    document.getElementById('progress-percent').textContent = `${progress}%`;
    document.getElementById('question-counter').textContent = `Question ${currentIndex + 1} of ${questions.length}`;

    // Options
    const container = document.getElementById('options-container');
    container.innerHTML = '';
    q.options.forEach((opt, idx) => {
        const isSelected = answers[currentIndex] === idx;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.setAttribute('role', 'radio');
        btn.setAttribute('aria-checked', isSelected ? 'true' : 'false');
        btn.setAttribute('tabindex', '0');
        btn.className = `w-full text-left px-5 py-4 rounded-xl border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-300 ${
            isSelected
                ? 'border-primary-400 bg-primary-50 shadow-sm'
                : 'border-gray-200 bg-white hover:border-primary-200 hover:bg-primary-50/30'
        }`;
        btn.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                    isSelected ? 'border-primary-500 bg-primary-500' : 'border-gray-300'
                }">
                    ${isSelected ? '<span class="w-2 h-2 bg-white rounded-full"></span>' : ''}
                </span>
                <span class="text-sm md:text-base text-gray-700 leading-relaxed">${escapeHtml(opt.label)}</span>
            </div>
        `;
        btn.addEventListener('click', () => selectOption(idx));
        btn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                selectOption(idx);
            }
        });
        container.appendChild(btn);
    });

    // Button states
    document.getElementById('prev-btn').disabled = currentIndex === 0;
    updateNextButton();

    // Animate card
    const card = document.getElementById('question-card');
    card.classList.remove('fade-in');
    void card.offsetWidth; // trigger reflow
    card.classList.add('fade-in');
}

function selectOption(idx) {
    answers[currentIndex] = idx;
    renderQuestion();
}

function updateNextButton() {
    const nextBtn = document.getElementById('next-btn');
    const hasAnswer = answers[currentIndex] !== null;
    nextBtn.disabled = !hasAnswer;

    // Update button text for last question
    if (currentIndex === questions.length - 1) {
        nextBtn.innerHTML = `<span class="flex items-center gap-2">See Results <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg></span>`;
    } else {
        nextBtn.innerHTML = `<span class="flex items-center gap-2">Next <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg></span>`;
    }
}

/* ======= NAVIGATION ======= */

function nextQuestion() {
    if (answers[currentIndex] === null) return;

    if (currentIndex < questions.length - 1) {
        currentIndex++;
        renderQuestion();
    } else {
        showResults();
    }
}

function previousQuestion() {
    if (currentIndex > 0) {
        currentIndex--;
        renderQuestion();
    }
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    const assessmentVisible = !document.getElementById('assessment-section').classList.contains('hidden');
    if (!assessmentVisible) return;

    if (e.key === 'ArrowRight' || e.key === 'Enter') {
        if (answers[currentIndex] !== null && currentIndex < questions.length) {
            nextQuestion();
        }
    } else if (e.key === 'ArrowLeft') {
        previousQuestion();
    } else if (e.key >= '1' && e.key <= '4') {
        selectOption(parseInt(e.key) - 1);
    }
});

/* ======= RESULTS ======= */

function calculateResults() {
    let totalScore = 0;
    const concerns = [];
    const areaScores = {};

    questions.forEach((q, idx) => {
        const selectedIdx = answers[idx];
        if (selectedIdx !== null) {
            const score = q.options[selectedIdx].score;
            totalScore += score;
            areaScores[q.id] = score;

            // Flag areas with score 0 or 1 as concerns
            if (score <= 1) {
                concerns.push(q.id);
            }
        }
    });

    // Category determination (max 30)
    let category, color, icon, encouragement;
    if (totalScore >= 25) {
        category = 'Thriving';
        color = 'from-primary-400 to-primary-600';
        icon = '🌟';
        encouragement = 'You appear to be in a strong emotional place. Keep nurturing the habits and connections that support you. This conversation can help you maintain and deepen your self-awareness.';
    } else if (totalScore >= 18) {
        category = 'Doing Well';
        color = 'from-calm-400 to-calm-600';
        icon = '🌿';
        encouragement = 'You seem to be managing well overall, with some areas that could use extra attention. A thoughtful conversation can help you build on your strengths and address smaller challenges before they grow.';
    } else if (totalScore >= 10) {
        category = 'Needs Attention';
        color = 'from-amber-400 to-amber-600';
        icon = '🌤️';
        encouragement = 'Some areas of your wellbeing may benefit from more support. That takes courage to acknowledge. Speaking openly about how you feel is a meaningful step, and this companion is here to listen without judgment.';
    } else {
        category = 'High Emotional Strain';
        color = 'from-warm-400 to-red-400';
        icon = '💛';
        encouragement = 'It sounds like things have been really difficult recently. You are not alone, and reaching out — even to an AI — shows incredible strength. Please also consider speaking with a licensed professional who can offer personalized support.';
    }

    // Build emotional summary for the AI
    const concernLabels = {
        mood: 'low mood',
        sleep: 'poor sleep quality',
        energy: 'low energy levels',
        anxiety: 'frequent anxiety or nervousness',
        stress: 'difficulty coping with stress',
        concentration: 'trouble concentrating',
        motivation: 'low motivation',
        appetite: 'appetite changes',
        social: 'social withdrawal',
        balance: 'emotional instability',
    };

    const detectedConcerns = concerns.map(c => concernLabels[c] || c);
    const emotionalSummary = buildSummary(category, totalScore, detectedConcerns);

    return {
        totalScore,
        maxScore: 30,
        percentage: Math.round((totalScore / 30) * 100),
        category,
        color,
        icon,
        encouragement,
        concerns: detectedConcerns,
        areaScores,
        emotionalSummary,
    };
}

function buildSummary(category, score, concerns) {
    let summary = `User completed the emotional check-in with a score of ${score}/30 (${category}).`;
    if (concerns.length > 0) {
        summary += ` Areas of concern include: ${concerns.join(', ')}.`;
    }
    summary += ` The AI companion should acknowledge these results, avoid repeating the same introductory questions, and gently explore the flagged areas with empathy.`;
    return summary;
}

function showResults() {
    const results = calculateResults();

    // Store results globally for the continue button
    window._checkinResults = results;

    // Hide assessment, show results
    document.getElementById('assessment-section').classList.add('hidden');
    document.getElementById('results-section').classList.remove('hidden');

    // Populate results
    const iconEl = document.getElementById('result-icon');
    iconEl.className = `w-20 h-20 mx-auto rounded-full flex items-center justify-center bg-gradient-to-br ${results.color}`;
    iconEl.innerHTML = `<span class="text-3xl">${results.icon}</span>`;

    document.getElementById('result-category').textContent = results.category;
    document.getElementById('result-score-label').textContent = `Wellness Score: ${results.totalScore} out of ${results.maxScore}`;
    document.getElementById('result-score-value').textContent = `${results.percentage}%`;

    // Animate score bar
    setTimeout(() => {
        const bar = document.getElementById('result-score-bar');
        bar.style.width = `${results.percentage}%`;
        bar.className = `h-full rounded-full transition-all duration-1000 ease-out bg-gradient-to-r ${results.color}`;
    }, 100);

    // Observations
    const obsList = document.getElementById('observations-list');
    obsList.innerHTML = '';

    if (results.concerns.length > 0) {
        results.concerns.forEach(concern => {
            const li = document.createElement('li');
            li.className = 'flex items-start gap-3 text-sm text-gray-700';
            li.innerHTML = `
                <span class="w-2 h-2 rounded-full bg-amber-400 mt-1.5 flex-shrink-0"></span>
                <span class="capitalize">${escapeHtml(concern)}</span>
            `;
            obsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.className = 'text-sm text-gray-500';
        li.textContent = 'No significant concerns detected — you appear to be in good emotional balance.';
        obsList.appendChild(li);
    }

    // Encouragement
    document.querySelector('#encouraging-message p').textContent = results.encouragement;

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ======= CONTINUE TO AI COMPANION ======= */

async function continueToCompanion() {
    const results = window._checkinResults;
    if (!results) return;

    const btn = document.getElementById('continue-btn');
    btn.disabled = true;
    btn.innerHTML = `
        <span class="flex items-center gap-2">
            <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            Starting conversation...
        </span>
    `;

    try {
        // Start conversation with assessment context
        const response = await fetch('/api/conversation/start-with-checkin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                score: results.totalScore,
                max_score: results.maxScore,
                category: results.category,
                concerns: results.concerns,
                emotional_summary: results.emotionalSummary,
                area_scores: results.areaScores,
            }),
        });

        if (!response.ok) throw new Error('Failed to start conversation');
        const data = await response.json();

        // Navigate to chat with conversation context
        window.location.href = `/chat?conversation_id=${data.conversation_id}`;
    } catch (error) {
        console.error('Error starting conversation:', error);
        btn.disabled = false;
        btn.innerHTML = 'Continue with AI Companion';
        alert('Failed to start conversation. Please try again.');
    }
}

/* ======= UTILITY ======= */

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
