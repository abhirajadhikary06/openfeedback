/**
 * VoteManager - Handles feedback voting functionality
 * Manages vote submission, removal, and display updates
 */

class VoteManager {
  constructor() {
    this.votes = {}; // Cache of vote states by feedback_id
    this.currentUserId = null; // Will be set from session
    this.isAuthenticated = false;
  }

  /**
   * Initialize the vote manager
   */
  async init() {
    // Check if user is authenticated
    this.checkAuthentication();
    
    // Load all vote data
    await this.loadVotes();
    
    // Render vote controls on all feedback cards
    this.renderVoteControls();
    
    // Attach event listeners
    this.attachEventListeners();
  }

  /**
   * Check if user is authenticated by looking for session data
   */
  checkAuthentication() {
    // Check if there's a logged-in user indicator in the page
    const authState = document.getElementById('auth-state');
    if (authState) {
      this.isAuthenticated = authState.dataset.loggedIn === 'true';
      this.currentUserId = authState.dataset.userId ? parseInt(authState.dataset.userId) : null;
    }
  }

  /**
   * Load vote data for all feedback items
   */
  async loadVotes() {
    try {
      const response = await fetch('/api/feedback/votes');
      const data = await response.json();
      
      if (data.success) {
        this.votes = data.votes;
      } else {
        console.error('Failed to load votes:', data.error);
      }
    } catch (error) {
      console.error('Error loading votes:', error);
    }
  }

  /**
   * Render vote controls on all feedback cards
   */
  renderVoteControls() {
    const feedbackCards = document.querySelectorAll('.feedback-box');
    
    feedbackCards.forEach(card => {
      const feedbackId = card.dataset.feedbackId;
      const feedbackUserId = card.dataset.userId ? parseInt(card.dataset.userId) : null;
      
      // Get vote data for this feedback
      const voteData = this.votes[feedbackId] || {
        vote_score: 0,
        upvotes: 0,
        downvotes: 0,
        user_vote: null
      };
      
      // Create vote controls
      const controls = this.createVoteControls(feedbackId, voteData, feedbackUserId);
      
      // Insert controls into feedback card
      const contentDiv = card.querySelector('.feedback-box-content');
      if (contentDiv && !contentDiv.querySelector('.vote-controls')) {
        contentDiv.appendChild(controls);
      }
    });
  }

  /**
   * Create vote controls HTML for a feedback item
   */
  createVoteControls(feedbackId, voteData, feedbackUserId) {
    const container = document.createElement('div');
    container.className = 'vote-controls';
    container.dataset.feedbackId = feedbackId;
    
    // Determine if controls should be disabled
    const isOwnFeedback = this.currentUserId && this.currentUserId === feedbackUserId;
    const shouldDisable = !this.isAuthenticated || isOwnFeedback;
    
    // Upvote button
    const upvoteBtn = document.createElement('button');
    upvoteBtn.className = 'vote-btn upvote-btn';
    upvoteBtn.dataset.voteType = 'upvote';
    upvoteBtn.disabled = shouldDisable;
    if (voteData.user_vote === 'upvote') {
      upvoteBtn.classList.add('active');
    }
    upvoteBtn.innerHTML = `
      <i class="fas fa-thumbs-up"></i>
      <span class="vote-count">${voteData.upvotes}</span>
    `;
    
    // Downvote button
    const downvoteBtn = document.createElement('button');
    downvoteBtn.className = 'vote-btn downvote-btn';
    downvoteBtn.dataset.voteType = 'downvote';
    downvoteBtn.disabled = shouldDisable;
    if (voteData.user_vote === 'downvote') {
      downvoteBtn.classList.add('active');
    }
    downvoteBtn.innerHTML = `
      <i class="fas fa-thumbs-down"></i>
      <span class="vote-count">${voteData.downvotes}</span>
    `;
    
    // Score label
    const scoreLabel = document.createElement('div');
    scoreLabel.className = 'vote-score-label';
    scoreLabel.innerHTML = '<i class="fas fa-chart-line"></i> Score:';
    
    // Vote score (just the number)
    const scoreDiv = document.createElement('div');
    scoreDiv.className = 'vote-score';
    if (voteData.vote_score > 0) {
      scoreDiv.classList.add('positive');
      scoreDiv.textContent = `+${voteData.vote_score}`;
    } else if (voteData.vote_score < 0) {
      scoreDiv.classList.add('negative');
      scoreDiv.textContent = `${voteData.vote_score}`;
    } else {
      scoreDiv.textContent = '0';
    }
    
    // Assemble controls in horizontal layout
    container.appendChild(upvoteBtn);
    container.appendChild(downvoteBtn);
    container.appendChild(scoreLabel);
    container.appendChild(scoreDiv);
    
    return container;
  }

  /**
   * Attach event listeners for vote buttons
   */
  attachEventListeners() {
    // Use event delegation for vote button clicks
    document.addEventListener('click', (e) => {
      const voteBtn = e.target.closest('.vote-btn');
      if (voteBtn && !voteBtn.disabled) {
        this.handleVote(voteBtn);
      }
    });
  }

  /**
   * Handle vote button click
   */
  async handleVote(button) {
    const controls = button.closest('.vote-controls');
    const feedbackId = controls.dataset.feedbackId;
    const voteType = button.dataset.voteType;
    const currentVote = this.votes[feedbackId]?.user_vote;
    
    // Disable buttons during request
    this.setButtonsLoading(controls, true);
    
    try {
      if (currentVote === voteType) {
        // Remove vote (toggle off)
        await this.removeVote(feedbackId);
      } else {
        // Create or update vote
        await this.submitVote(feedbackId, voteType);
      }
    } catch (error) {
      this.showError('Failed to process vote. Please try again.');
    } finally {
      // Re-enable buttons
      this.setButtonsLoading(controls, false);
    }
  }

  /**
   * Submit a vote (create or update)
   */
  async submitVote(feedbackId, voteType) {
    const response = await fetch('/api/vote', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        feedback_id: parseInt(feedbackId),
        vote_type: voteType
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Update vote data
      await this.updateVoteData(feedbackId, voteType, data.vote.vote_score);
      
      // Update display
      this.updateVoteDisplay(feedbackId);
    } else {
      throw new Error(data.error || 'Failed to submit vote');
    }
  }

  /**
   * Remove a vote
   */
  async removeVote(feedbackId) {
    const response = await fetch(`/api/vote/${feedbackId}`, {
      method: 'DELETE'
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Update vote data
      await this.updateVoteData(feedbackId, null, data.vote_score);
      
      // Update display
      this.updateVoteDisplay(feedbackId);
    } else {
      throw new Error(data.error || 'Failed to remove vote');
    }
  }

  /**
   * Update cached vote data after a vote operation
   */
  async updateVoteData(feedbackId, newVoteType, newScore) {
    // Fetch fresh vote data for this feedback
    try {
      const response = await fetch(`/api/feedback/${feedbackId}/votes`);
      const data = await response.json();
      
      if (data.success) {
        this.votes[feedbackId] = {
          vote_score: data.vote_score,
          upvotes: data.upvotes,
          downvotes: data.downvotes,
          user_vote: data.user_vote
        };
      }
    } catch (error) {
      console.error('Error updating vote data:', error);
    }
  }

  /**
   * Update vote display in the DOM
   */
  updateVoteDisplay(feedbackId) {
    const controls = document.querySelector(`.vote-controls[data-feedback-id="${feedbackId}"]`);
    if (!controls) return;
    
    const voteData = this.votes[feedbackId];
    if (!voteData) return;
    
    // Update upvote button
    const upvoteBtn = controls.querySelector('.upvote-btn');
    const upvoteCount = upvoteBtn.querySelector('.vote-count');
    upvoteCount.textContent = voteData.upvotes;
    
    if (voteData.user_vote === 'upvote') {
      upvoteBtn.classList.add('active');
    } else {
      upvoteBtn.classList.remove('active');
    }
    
    // Update downvote button
    const downvoteBtn = controls.querySelector('.downvote-btn');
    const downvoteCount = downvoteBtn.querySelector('.vote-count');
    downvoteCount.textContent = voteData.downvotes;
    
    if (voteData.user_vote === 'downvote') {
      downvoteBtn.classList.add('active');
    } else {
      downvoteBtn.classList.remove('active');
    }
    
    // Update score (just the number)
    const scoreDiv = controls.querySelector('.vote-score');
    scoreDiv.className = 'vote-score'; // Reset classes
    
    if (voteData.vote_score > 0) {
      scoreDiv.classList.add('positive');
      scoreDiv.textContent = `+${voteData.vote_score}`;
    } else if (voteData.vote_score < 0) {
      scoreDiv.classList.add('negative');
      scoreDiv.textContent = `${voteData.vote_score}`;
    } else {
      scoreDiv.textContent = '0';
    }
  }

  /**
   * Set loading state on vote buttons
   */
  setButtonsLoading(controls, isLoading) {
    const buttons = controls.querySelectorAll('.vote-btn');
    buttons.forEach(btn => {
      if (isLoading) {
        btn.classList.add('loading');
        btn.disabled = true;
      } else {
        btn.classList.remove('loading');
        // Only re-enable if not permanently disabled
        const feedbackCard = controls.closest('.feedback-box');
        const feedbackUserId = feedbackCard.dataset.userId ? parseInt(feedbackCard.dataset.userId) : null;
        const isOwnFeedback = this.currentUserId && this.currentUserId === feedbackUserId;
        btn.disabled = !this.isAuthenticated || isOwnFeedback;
      }
    });
  }

  /**
   * Show error message to user
   */
  showError(message) {
    // Simple alert for now - can be enhanced with a toast notification
    alert(message);
  }

  /**
   * Refresh vote controls after filtering/sorting
   * Called by FeedbackManager when feedback list is updated
   */
  refreshVoteControls() {
    // Re-render vote controls for all visible feedback cards
    const feedbackCards = document.querySelectorAll('.feedback-box[style*="display: block"], .feedback-box:not([style*="display: none"])');
    
    feedbackCards.forEach(card => {
      const feedbackId = card.dataset.feedbackId;
      const existingControls = card.querySelector('.vote-controls');
      
      // Only refresh if controls already exist
      if (existingControls && this.votes[feedbackId]) {
        this.updateVoteDisplay(feedbackId);
      }
    });
  }
}

// Initialize VoteManager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.voteManager = new VoteManager();
  window.voteManager.init();
});
