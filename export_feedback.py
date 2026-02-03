"""Export Feedback Module

This module provides functionality to export feedback data to CSV format.
Supports filtering by date range, sentiment, and company.
"""

import csv
import os
from datetime import datetime
from io import StringIO


class FeedbackExporter:
    """Utility class for exporting feedback data to CSV format."""

    def __init__(self, feedback_list=None):
        """Initialize the FeedbackExporter.
        
        Args:
            feedback_list: List of feedback dictionaries with keys:
                - company (str): Company name
                - sentiment (str): Sentiment (positive, neutral, negative)
                - message (str): Feedback message
                - rating (int): Rating 1-5
                - created_at (datetime): Creation timestamp
        """
        self.feedback_list = feedback_list or []

    def add_feedback(self, feedback_dict):
        """Add feedback to the export list.
        
        Args:
            feedback_dict: Dictionary containing feedback data
        """
        self.feedback_list.append(feedback_dict)

    def export_to_csv(self, filename=None, include_headers=True):
        """Export feedback data to CSV format.
        
        Args:
            filename (str, optional): Output filename. If None, returns CSV string
            include_headers (bool): Whether to include column headers
            
        Returns:
            str: CSV content if filename is None, otherwise None
        """
        output = StringIO()
        
        if not self.feedback_list:
            return "" if filename else ""
        
        fieldnames = ['Company', 'Sentiment', 'Rating', 'Message', 'Created At']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        if include_headers:
            writer.writeheader()
        
        for feedback in self.feedback_list:
            row = {
                'Company': feedback.get('company', ''),
                'Sentiment': feedback.get('sentiment', ''),
                'Rating': feedback.get('rating', ''),
                'Message': feedback.get('message', ''),
                'Created At': feedback.get('created_at', '')
            }
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_content)
            return None
        
        return csv_content

    def filter_by_sentiment(self, sentiment):
        """Filter feedback by sentiment.
        
        Args:
            sentiment (str): Sentiment type (positive, neutral, negative)
            
        Returns:
            FeedbackExporter: New exporter with filtered data
        """
        filtered = FeedbackExporter([
            f for f in self.feedback_list
            if f.get('sentiment', '').lower() == sentiment.lower()
        ])
        return filtered

    def filter_by_company(self, company):
        """Filter feedback by company name.
        
        Args:
            company (str): Company name
            
        Returns:
            FeedbackExporter: New exporter with filtered data
        """
        filtered = FeedbackExporter([
            f for f in self.feedback_list
            if f.get('company', '').lower() == company.lower()
        ])
        return filtered

    def get_statistics(self):
        """Get feedback statistics.
        
        Returns:
            dict: Statistics including total count and sentiment breakdown
        """
        if not self.feedback_list:
            return {
                'total': 0,
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'average_rating': 0
            }
        
        positive = sum(1 for f in self.feedback_list if f.get('sentiment') == 'positive')
        neutral = sum(1 for f in self.feedback_list if f.get('sentiment') == 'neutral')
        negative = sum(1 for f in self.feedback_list if f.get('sentiment') == 'negative')
        
        total_rating = sum(f.get('rating', 0) for f in self.feedback_list)
        avg_rating = total_rating / len(self.feedback_list) if self.feedback_list else 0
        
        return {
            'total': len(self.feedback_list),
            'positive': positive,
            'neutral': neutral,
            'negative': negative,
            'average_rating': round(avg_rating, 2)
        }


if __name__ == '__main__':
    # Example usage
    sample_feedback = [
        {
            'company': 'TechCorp',
            'sentiment': 'positive',
            'rating': 5,
            'message': 'Great product and excellent customer service!',
            'created_at': datetime.now().isoformat()
        },
        {
            'company': 'DataFlow',
            'sentiment': 'neutral',
            'rating': 3,
            'message': 'Good but could be improved',
            'created_at': datetime.now().isoformat()
        },
        {
            'company': 'TechCorp',
            'sentiment': 'negative',
            'rating': 2,
            'message': 'Experienced technical issues',
            'created_at': datetime.now().isoformat()
        }
    ]
    
    exporter = FeedbackExporter(sample_feedback)
    
    # Print statistics
    print('Feedback Statistics:')
    print(exporter.get_statistics())
    
    # Export all feedback
    print('\nAll Feedback (CSV):')
    print(exporter.export_to_csv())
    
    # Export positive feedback only
    print('\nPositive Feedback Only:')
    positive_exporter = exporter.filter_by_sentiment('positive')
    print(positive_exporter.export_to_csv())
