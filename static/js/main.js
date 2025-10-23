document.addEventListener('DOMContentLoaded', function() {
    const feedbackBtn = document.getElementById('feedbackBtn');
    const feedbackOverlay = document.getElementById('feedbackOverlay');
    const closeFeedback = document.getElementById('closeFeedback');
    const feedbackForm = document.getElementById('feedbackForm');
    const hofGrid = document.getElementById('hofGrid');

    // Toggle feedback overlay
    feedbackBtn.addEventListener('click', () => {
        feedbackOverlay.style.display = 'flex';
    });

    closeFeedback.addEventListener('click', () => {
        feedbackOverlay.style.display = 'none';
    });

    feedbackOverlay.addEventListener('click', (e) => {
        if (e.target === feedbackOverlay) {
            feedbackOverlay.style.display = 'none';
        }
    });

    // Submit feedback
    feedbackForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(feedbackForm);
        const data = {
            company: formData.get('company'),
            comment: formData.get('comment')
        };

        try {
            const response = await fetch('/submit_feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.success) {
                // Add new feedback card to top
                const newCard = createFeedbackCard(result.feedback);
                hofGrid.insertBefore(newCard, hofGrid.firstChild);
                
                // Reset form and close overlay
                feedbackForm.reset();
                feedbackOverlay.style.display = 'none';
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
            alert('Error submitting feedback. Please try again.');
        }
    });

    function createFeedbackCard(feedback) {
        const card = document.createElement('div');
        card.className = 'feedback-card';
        card.innerHTML = `
            <div class="card-header">
                <div class="company-info">
                    <img src="${feedback.company_logo}" alt="${feedback.company_name}" class="company-logo">
                    <span>${feedback.company_name}</span>
                </div>
                <div class="sentiment-info">
                    <span class="sentiment-tag ${feedback.sentiment}">${feedback.sentiment.charAt(0).toUpperCase() + feedback.sentiment.slice(1)}</span>
                </div>
            </div>
            <div class="card-content">
                <p>"${feedback.comment}"</p>
            </div>
        `;
        return card;
    }
});