// Quiz Mode JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const startScreen = document.getElementById('startScreen');
    const quizScreen = document.getElementById('quizScreen');
    const resultsScreen = document.getElementById('resultsScreen');
    const startQuizBtn = document.getElementById('startQuizBtn');
    const retakeQuizBtn = document.getElementById('retakeQuizBtn');
    const numQuestionsSelect = document.getElementById('numQuestions');
    const quizSourceSelect = document.getElementById('quizSource');

    let currentQuiz = null;
    let currentQuestionIndex = 0;
    let score = 0;
    let totalQuestions = 0;

    // Start Quiz
    startQuizBtn.addEventListener('click', async function() {
        const numQuestions = parseInt(numQuestionsSelect.value);
        const sourceType = quizSourceSelect.value;

        try {
            startQuizBtn.disabled = true;
            startQuizBtn.innerHTML = '<span class="spinner"></span> იტვირთება...';

            const response = await fetch('/api/quiz/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    num_questions: numQuestions,
                    source_type: sourceType
                })
            });

            const data = await response.json();

            if (data.error) {
                alert(data.message);
                startQuizBtn.disabled = false;
                startQuizBtn.innerHTML = '🎯 ტესტის დაწყება';
                return;
            }

            // Start quiz
            currentQuiz = data;
            totalQuestions = data.total_questions;
            currentQuestionIndex = 0;
            score = 0;

            showQuestion(data.first_question);
            startScreen.style.display = 'none';
            quizScreen.style.display = 'block';

        } catch (error) {
            alert('შეცდომა: ' + error.message);
            startQuizBtn.disabled = false;
            startQuizBtn.innerHTML = '🎯 ტესტის დაწყება';
        }
    });

    // Show Question
    function showQuestion(question) {
        currentQuestionIndex++;

        console.log('[DEBUG] Question object:', question);
        console.log('[DEBUG] Question ID:', question.id);

        // Update progress
        const progressPercent = ((currentQuestionIndex - 1) / totalQuestions) * 100;
        document.getElementById('progressFill').style.width = progressPercent + '%';
        document.getElementById('progressText').textContent = `კითხვა ${currentQuestionIndex} / ${totalQuestions}`;

        // Update question
        document.getElementById('questionDifficulty').textContent = getDifficultyBadge(question.difficulty);
        document.getElementById('questionText').textContent = question.question;

        // Clear previous feedback and hide next button
        document.getElementById('quizFeedback').style.display = 'none';
        document.getElementById('nextButtonContainer').style.display = 'none';

        // Create option buttons
        const optionsContainer = document.getElementById('questionOptions');
        optionsContainer.innerHTML = '';

        question.options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'option-btn';
            button.textContent = option;
            button.onclick = () => submitAnswer(question.id, option);
            optionsContainer.appendChild(button);
        });
    }

    // Submit Answer
    async function submitAnswer(questionId, answer) {
        console.log('[DEBUG] submitAnswer called with questionId:', questionId, 'type:', typeof questionId);

        // Disable all option buttons
        const optionBtns = document.querySelectorAll('.option-btn');
        optionBtns.forEach(btn => btn.disabled = true);

        try {
            const payload = {
                question_id: questionId,
                answer: answer
            };
            console.log('[DEBUG] Sending payload:', payload);

            const response = await fetch('/api/quiz/answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.error) {
                alert(data.message);
                return;
            }

            // Update score
            if (data.is_correct) {
                score++;
            }

            // Show feedback with next button
            showFeedback(data);

        } catch (error) {
            alert('შეცდომა: ' + error.message);
        }
    }

    // Show Feedback
    function showFeedback(data) {
        const feedback = document.getElementById('quizFeedback');
        const isCorrect = data.is_correct;

        // Build feedback HTML - always show explanation for learning
        // Only show correct_answer if user got it wrong (to prevent cheating)
        let feedbackHTML = `
            <div class="feedback-${isCorrect ? 'correct' : 'wrong'}">
                <div class="feedback-icon">${isCorrect ? '✅' : '❌'}</div>
                <div class="feedback-title">${isCorrect ? 'სწორია!' : 'არასწორია'}</div>
                ${!isCorrect && data.correct_answer ? `<div class="feedback-answer">სწორი პასუხი: <strong>${data.correct_answer}</strong></div>` : ''}
        `;

        // Always show explanation and law reference for learning (whether correct or wrong)
        if (data.law_reference || data.explanation) {
            feedbackHTML += `
                <div class="feedback-explanation">
                    ${data.law_reference ? `<strong>${data.law_reference}</strong><br>` : ''}
                    ${data.explanation || ''}
                </div>
            `;
        }

        feedbackHTML += `</div>`;
        feedback.innerHTML = feedbackHTML;
        feedback.style.display = 'block';

        // Show next button at top with appropriate text
        const nextButtonText = data.is_complete ? '📊 შედეგების ნახვა' : '➡️ შემდეგი კითხვა';
        const nextBtn = document.getElementById('nextQuestionBtn');
        nextBtn.textContent = nextButtonText;
        document.getElementById('nextButtonContainer').style.display = 'block';

        // Highlight correct/wrong option (only highlight wrong answer since we don't know correct one)
        const optionBtns = document.querySelectorAll('.option-btn');
        optionBtns.forEach(btn => {
            // Only highlight correct answer if we have it (when answer was wrong)
            if (data.correct_answer && btn.textContent === data.correct_answer) {
                btn.classList.add('option-correct');
            }
            // Always highlight wrong answer if answer was incorrect
            if (btn.textContent === data.user_answer && !isCorrect) {
                btn.classList.add('option-wrong');
            }
        });

        // Add click handler for next button (remove old listener first)
        const newNextBtn = nextBtn.cloneNode(true);
        nextBtn.parentNode.replaceChild(newNextBtn, nextBtn);

        newNextBtn.addEventListener('click', function() {
            if (data.is_complete) {
                showResults();
            } else {
                showQuestion(data.next_question);
            }
        });
    }

    // Show Results
    function showResults() {
        quizScreen.style.display = 'none';
        resultsScreen.style.display = 'block';

        const percentage = ((score / totalQuestions) * 100).toFixed(1);

        let grade, message;
        if (percentage >= 90) {
            grade = 'A';
            message = 'შესანიშნავი! თქვენ ძალიან კარგად იცით კანონები!';
        } else if (percentage >= 80) {
            grade = 'B';
            message = 'კარგია! გააგრძელეთ სწავლა.';
        } else if (percentage >= 70) {
            grade = 'C';
            message = 'საშუალო შედეგი. კიდევ ივარჯიშეთ.';
        } else if (percentage >= 60) {
            grade = 'D';
            message = 'საჭიროა მეტი პრაქტიკა.';
        } else {
            grade = 'F';
            message = 'გადახედეთ კანონებს და სცადეთ თავიდან.';
        }

        document.getElementById('resultsScore').innerHTML = `
            <div class="results-grade">${grade}</div>
            <div class="results-percentage">${percentage}%</div>
            <div class="results-fraction">${score} / ${totalQuestions} სწორი</div>
        `;

        document.getElementById('resultsDetails').innerHTML = `
            <p class="results-message">${message}</p>
        `;
    }

    // Retake Quiz
    retakeQuizBtn.addEventListener('click', function() {
        // Reload page to refresh stats
        window.location.reload();
    });

    // Helper function
    function getDifficultyBadge(difficulty) {
        const badges = {
            'easy': '🟢 მარტივი',
            'medium': '🟡 საშუალო',
            'hard': '🔴 რთული'
        };
        return badges[difficulty] || difficulty;
    }
});
