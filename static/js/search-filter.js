/**
 * Openfeed - Search, Filter, and Sort Functionality
 * Handles real-time filtering and sorting of feedback cards
 */

class FeedbackManager {
  constructor() {
    this.feedbacks = [];
    this.filteredFeedbacks = [];
    this.currentFilters = {
      search: '',
      sentiment: '',
      company: '',
      sort: 'recent'
    };
    
    this.init();
  }

  init() {
    // Get all feedback elements and store their data
    this.loadFeedbackData();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Initial display
    this.applyFilters();
  }

  loadFeedbackData() {
    const feedbackElements = document.querySelectorAll('.feedback-box');
    this.feedbacks = Array.from(feedbackElements).map((element, index) => {
      const companyName = element.querySelector('.feedback-company-name').textContent.trim();
      const sentiment = element.querySelector('.sentiment-badge').textContent.trim().toLowerCase();
      const comment = element.querySelector('.feedback-text').textContent.trim();
      const dateElement = element.querySelector('.feedback-date');
      
      // Extract date from element or use index as fallback for sorting
      let date = new Date();
      if (dateElement) {
        date = new Date(dateElement.textContent);
      } else {
        // Use reverse index to simulate recent first order
        date = new Date(Date.now() - (index * 60000)); // Each feedback 1 minute apart
      }

      return {
        element: element,
        company: companyName,
        sentiment: sentiment,
        comment: comment,
        date: date,
        originalIndex: index,
        helpful: Math.floor(Math.random() * 100) // Simulate helpful votes for sorting
      };
    });

    this.filteredFeedbacks = [...this.feedbacks];
  }

  setupEventListeners() {
    // Filter toggle button
    const toggleFiltersBtn = document.getElementById('toggleFilters');
    const filtersRow = document.getElementById('filtersRow');
    
    toggleFiltersBtn.addEventListener('click', () => {
      const isVisible = filtersRow.style.display !== 'none';
      
      if (isVisible) {
        // Hide filters
        filtersRow.classList.remove('show');
        toggleFiltersBtn.classList.remove('active');
        setTimeout(() => {
          filtersRow.style.display = 'none';
        }, 400); // Match CSS transition duration
      } else {
        // Show filters
        filtersRow.style.display = 'grid';
        setTimeout(() => {
          filtersRow.classList.add('show');
          toggleFiltersBtn.classList.add('active');
        }, 10); // Small delay to ensure display change takes effect
      }
    });

    // Search input
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearch');
    
    searchInput.addEventListener('input', (e) => {
      this.currentFilters.search = e.target.value.toLowerCase();
      this.toggleClearSearchButton();
      this.applyFilters();
    });

    clearSearchBtn.addEventListener('click', () => {
      searchInput.value = '';
      this.currentFilters.search = '';
      this.toggleClearSearchButton();
      this.applyFilters();
    });

    // Filter selects
    document.getElementById('sentimentFilter').addEventListener('change', (e) => {
      this.currentFilters.sentiment = e.target.value;
      this.applyFilters();
    });

    document.getElementById('companyFilter').addEventListener('change', (e) => {
      this.currentFilters.company = e.target.value;
      this.applyFilters();
    });

    document.getElementById('sortSelect').addEventListener('change', (e) => {
      this.currentFilters.sort = e.target.value;
      this.applyFilters();
    });

    // Clear all filters
    document.getElementById('clearFilters').addEventListener('click', () => {
      this.clearAllFilters();
    });
  }

  toggleClearSearchButton() {
    const clearBtn = document.getElementById('clearSearch');
    const searchInput = document.getElementById('searchInput');
    
    if (searchInput.value.length > 0) {
      clearBtn.style.display = 'block';
    } else {
      clearBtn.style.display = 'none';
    }
  }

  applyFilters() {
    // Start with all feedbacks
    let filtered = [...this.feedbacks];

    // Apply search filter
    if (this.currentFilters.search) {
      filtered = filtered.filter(feedback => 
        feedback.company.toLowerCase().includes(this.currentFilters.search) ||
        feedback.comment.toLowerCase().includes(this.currentFilters.search)
      );
    }

    // Apply sentiment filter
    if (this.currentFilters.sentiment) {
      filtered = filtered.filter(feedback => 
        feedback.sentiment === this.currentFilters.sentiment
      );
    }

    // Apply company filter
    if (this.currentFilters.company) {
      filtered = filtered.filter(feedback => 
        feedback.company === this.currentFilters.company
      );
    }

    // Apply sorting
    this.sortFeedbacks(filtered);

    // Update display
    this.updateDisplay(filtered);
    this.updateResultsCount(filtered.length);
    
    // Update filter button indicator
    this.updateFilterButtonState();
  }

  updateFilterButtonState() {
    const toggleBtn = document.getElementById('toggleFilters');
    const hasActiveFilters = 
      this.currentFilters.search || 
      this.currentFilters.sentiment || 
      this.currentFilters.company ||
      this.currentFilters.sort !== 'recent';
    
    if (hasActiveFilters) {
      toggleBtn.classList.add('has-active-filters');
    } else {
      toggleBtn.classList.remove('has-active-filters');
    }
  }

  sortFeedbacks(feedbacks) {
    switch (this.currentFilters.sort) {
      case 'recent':
        feedbacks.sort((a, b) => b.date - a.date);
        break;
      case 'oldest':
        feedbacks.sort((a, b) => a.date - b.date);
        break;
      case 'helpful':
        feedbacks.sort((a, b) => b.helpful - a.helpful);
        break;
      default:
        feedbacks.sort((a, b) => b.date - a.date);
    }
  }

  updateDisplay(filteredFeedbacks) {
    const feedbackGrid = document.getElementById('hofGrid');
    
    // Hide all feedback elements first
    this.feedbacks.forEach(feedback => {
      feedback.element.style.display = 'none';
    });

    // Show filtered feedbacks in order
    if (filteredFeedbacks.length === 0) {
      this.showNoResults();
    } else {
      this.hideNoResults();
      filteredFeedbacks.forEach((feedback, index) => {
        feedback.element.style.display = 'block';
        feedback.element.style.order = index;
        feedbackGrid.appendChild(feedback.element);
      });
    }
  }

  showNoResults() {
    let noResultsElement = document.getElementById('noResults');
    
    if (!noResultsElement) {
      noResultsElement = document.createElement('div');
      noResultsElement.id = 'noResults';
      noResultsElement.className = 'no-results';
      noResultsElement.innerHTML = `
        <i class="fas fa-search"></i>
        <h3>No feedback found</h3>
        <p>Try adjusting your search terms or filters</p>
      `;
      document.getElementById('hofGrid').appendChild(noResultsElement);
    }
    
    noResultsElement.style.display = 'block';
  }

  hideNoResults() {
    const noResultsElement = document.getElementById('noResults');
    if (noResultsElement) {
      noResultsElement.style.display = 'none';
    }
  }

  updateResultsCount(count) {
    const resultsCount = document.getElementById('resultsCount');
    const total = this.feedbacks.length;
    
    if (count === total) {
      resultsCount.textContent = `${total} feedback(s) found`;
    } else {
      resultsCount.textContent = `${count} of ${total} feedback(s) found`;
    }
  }

  clearAllFilters() {
    // Reset all filter values
    document.getElementById('searchInput').value = '';
    document.getElementById('sentimentFilter').value = '';
    document.getElementById('companyFilter').value = '';
    document.getElementById('sortSelect').value = 'recent';
    
    // Reset internal state
    this.currentFilters = {
      search: '',
      sentiment: '',
      company: '',
      sort: 'recent'
    };
    
    // Hide clear search button
    this.toggleClearSearchButton();
    
    // Hide filters panel
    const filtersRow = document.getElementById('filtersRow');
    const toggleFiltersBtn = document.getElementById('toggleFilters');
    
    filtersRow.classList.remove('show');
    toggleFiltersBtn.classList.remove('active');
    setTimeout(() => {
      filtersRow.style.display = 'none';
    }, 400);
    
    // Apply filters (which will show all)
    this.applyFilters();
  }

  // Method to add new feedback (for when new feedback is submitted)
  addNewFeedback(feedbackData) {
    const feedbackGrid = document.getElementById('hofGrid');
    
    // Create new feedback element
    const feedbackElement = this.createFeedbackElement(feedbackData);
    
    // Add to feedbacks array
    const newFeedback = {
      element: feedbackElement,
      company: feedbackData.company_name,
      sentiment: feedbackData.sentiment,
      comment: feedbackData.comment,
      date: new Date(),
      originalIndex: this.feedbacks.length,
      helpful: 0
    };
    
    this.feedbacks.unshift(newFeedback); // Add to beginning
    
    // Reapply filters to include new feedback
    this.applyFilters();
  }

  createFeedbackElement(feedback) {
    const feedbackCard = document.createElement('div');
    feedbackCard.className = 'feedback-box';
    feedbackCard.style.animation = 'modalSlideIn 0.5s ease';

    feedbackCard.innerHTML = `
      <div class="feedback-box-header">
        <div class="feedback-company">
          ${
            feedback.company_logo
              ? `<img class="feedback-company-logo" src="${feedback.company_logo}" alt="${feedback.company_name} logo">`
              : `<div class="feedback-company-logo" style="background-color: #4285f4; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                  ${feedback.company_name[0].toUpperCase()}
                </div>`
          }
          <span class="feedback-company-name">${feedback.company_name}</span>
        </div>
        <span class="sentiment-badge ${feedback.sentiment}">
          ${feedback.sentiment.charAt(0).toUpperCase() + feedback.sentiment.slice(1)}
        </span>
      </div>
      <div class="feedback-box-content">
        <p class="feedback-text">"${feedback.comment}"</p>
      </div>
    `;

    return feedbackCard;
  }
}

// Initialize the feedback manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Wait a bit to ensure all other scripts have loaded
  setTimeout(() => {
    window.feedbackManager = new FeedbackManager();
  }, 100);
});

// Export for use in other scripts
window.FeedbackManager = FeedbackManager;