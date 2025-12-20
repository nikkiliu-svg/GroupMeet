/**
 * Feedback form component.
 */
import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { feedbackAPI, matchesAPI } from '../../services/api';
import { Match, FeedbackData } from '../../services/types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorMessage } from '../common/ErrorMessage';

export const FeedbackForm: React.FC = () => {
  const [searchParams] = useSearchParams();
  const matchId = searchParams.get('match_id') || '';

  const [match, setMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState<FeedbackData>({
    match_id: matchId,
    rating: 0,
    comments: '',
    met_with_group: false,
    would_meet_again: false,
  });

  useEffect(() => {
    if (matchId) {
      loadMatch();
    } else {
      setError('No match ID provided');
      setLoading(false);
    }
  }, [matchId]);

  const loadMatch = async () => {
    try {
      const matchData = await matchesAPI.getById(matchId);
      setMatch(matchData);
      setFormData((prev) => ({ ...prev, match_id: matchId }));
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load match');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await feedbackAPI.create(formData);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading match information..." />;
  }

  if (success) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h2 style={{ color: '#01256E' }}>Thank You!</h2>
        <p>Your feedback has been submitted successfully.</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h2 style={{ color: '#01256E', marginBottom: '30px' }}>Rate Your Study Group</h2>

      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}

      {match && (
        <div style={{ marginBottom: '30px', padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
          <h3>Course: {match.course}</h3>
          <p>Group #{match.group_id}</p>
          <p>Suggested Time: {match.suggested_meeting_time.replace('_', ' ')}</p>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Rating * (1-5 stars)
          </label>
          <div style={{ display: 'flex', gap: '10px', fontSize: '24px' }}>
            {[1, 2, 3, 4, 5].map((rating) => (
              <button
                key={rating}
                type="button"
                onClick={() => setFormData({ ...formData, rating })}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '32px',
                  color: formData.rating >= rating ? '#ffd700' : '#ddd',
                }}
              >
                ★
              </button>
            ))}
          </div>
          {formData.rating > 0 && <p>Selected: {formData.rating} stars</p>}
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Did you meet with your group?
          </label>
          <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
            <input
              type="checkbox"
              checked={formData.met_with_group}
              onChange={(e) => setFormData({ ...formData, met_with_group: e.target.checked })}
              style={{ marginRight: '8px' }}
            />
            Yes, I met with my group
          </label>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Would you meet with this group again?
          </label>
          <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
            <input
              type="checkbox"
              checked={formData.would_meet_again}
              onChange={(e) => setFormData({ ...formData, would_meet_again: e.target.checked })}
              style={{ marginRight: '8px' }}
            />
            Yes, I would meet with them again
          </label>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Comments (optional)
          </label>
          <textarea
            value={formData.comments}
            onChange={(e) => setFormData({ ...formData, comments: e.target.value })}
            rows={5}
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px',
            }}
            placeholder="Share your experience..."
          />
        </div>

        <button
          type="submit"
          disabled={submitting || formData.rating === 0}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: submitting || formData.rating === 0 ? '#ccc' : '#01256E',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: submitting || formData.rating === 0 ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
          }}
        >
          {submitting ? 'Submitting...' : 'Submit Feedback'}
        </button>
      </form>
    </div>
  );
};

