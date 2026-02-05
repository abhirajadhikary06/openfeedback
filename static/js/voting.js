/**
 * Openfeed - Voting System JavaScript
 * Handles upvote/downvote functionality for feedback
 */

class VotingSystem {
  constructor() {
    this.init();
  }

  init() {
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Add event listeners to all vote buttons
    document.addEventListener('click', (e) => {
      if (e.target.closest('.vote-btn:not(.disabled)')) {
        const button = e.target.closest('.vote-btn');
        this.handleVote(button);
      }
    });
  }

  async handleVote(button) {
    const feedbackId = button.dataset.feedbackId;
    const voteType = parseInt(button.dataset.voteType);
    
    if (!feedbackId || !voteType) {
      console.error('Invalid vote data');
      return;
    }

    // Disable button during request
    button.disabled = true;
    
    try {
      const response = await fetch('/api/vote', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          feedback_id: feedbackId,
          vote_type: voteType
        })
      });

      const data = await response.json();

      if (data.success) {
        this.updateVoteUI(feedbackId, data, voteType);
        
        // Update search/filter results if they exist
        if (window.feedbackManager) {
          window.feedbackManager.updateFeedbackVotes(feedbackId, data);
        }
      } else {
        alert('Error: ' + data.message);
      }
    } catch (error) {
      console.error('Vote error:', error);
      alert('An error occurred while voting. Please try again.');
    } finally {
      button.disabled = false;
    }
  }

  updateVoteUI(feedbackId, voteData, clickedVoteType) {
    const feedbackBox = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
    if (!feedbackBox) return;

    const upvoteBtn = feedbackBox.querySelector('.upvote-btn');
    const downvoteBtn = feedbackBox.querySelector('.downvote-btn');
    const scoreValue = feedbackBox.querySelector('.score-value');

    // Update vote counts
    upvoteBtn.querySelector('.vote-count').textContent = voteData.upvote_count;
    downvoteBtn.querySelector('.vote-count').textContent = voteData.downvote_count;

    // Update score
    scoreValue.textContent = voteData.vote_score;
    
    // Update score styling
    scoreValue.className = 'score-value';
    if (voteData.vote_score > 0) {
      scoreValue.classList.add('positive');
    } else if (voteData.vote_score < 0) {
      scoreValue.classList.add('negative');
    }

    // Update button states based on action
    upvoteBtn.classList.remove('active');
    downvoteBtn.classList.remove('active');

    if (voteData.action === 'added') {
      // New vote - activate the clicked button
      if (clickedVoteType === 1) {
        upvoteBtn.classList.add('active');
      } else {
        downvoteBtn.classList.add('active');
      }
    } else if (voteData.action === 'updated') {
      // Changed vote - activate the clicked button
      if (clickedVoteType === 1) {
        upvoteBtn.classList.add('active');
      } else {
        downvoteBtn.classList.add('active');
      }
    }
    // If action is 'removed', both buttons remain inactive
  }

  // Method to update vote data when new feedback is added
  updateNewFeedbackVotes(feedbackElement, voteData) {
    if (!voteData) return;

    const upvoteBtn = feedbackElement.querySelector('.upvote-btn');
    const downvoteBtn = feedbackElement.querySelector('.downvote-btn');
    const scoreValue = feedbackElement.querySelector('.score-value');

    if (upvoteBtn) upvoteBtn.querySelector('.vote-count').textContent = voteData.upvote_count || 0;
    if (downvoteBtn) downvoteBtn.querySelector('.vote-count').textContent = voteData.downvote_count || 0;
    if (scoreValue) {
      scoreValue.textContent = voteData.vote_score || 0;
      scoreValue.className = 'score-value';
      if (voteData.vote_score > 0) {
        scoreValue.classList.add('positive');
      } else if (voteData.vote_score < 0) {
        scoreValue.classList.add('negative');
      }
    }
  }
}

// Initialize voting system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  window.votingSystem = new VotingSystem();
});

// Export for use in other scripts
window.VotingSystem = VotingSystem;