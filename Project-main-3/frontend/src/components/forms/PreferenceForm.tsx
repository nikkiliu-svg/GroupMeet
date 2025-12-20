/**
 * Preference form component for student submissions.
 */
import React, { useState } from 'react';
import { submissionsAPI } from '../../services/api';
import { SubmissionData } from '../../services/types';
import { STUDY_STYLES, GOALS, AVAILABILITY_SLOTS, GROUP_SIZE_OPTIONS } from '../../utils/constants';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { ErrorMessage } from '../common/ErrorMessage';

export const PreferenceForm: React.FC = () => {
  const [formData, setFormData] = useState<SubmissionData>({
    course: '',
    availability: [],
    study_style: '',
    goal: '',
    preferred_group_size: 4,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await submissionsAPI.create(formData);
      setSuccess(true);
      // Reset form
      setFormData({
        course: '',
        availability: [],
        study_style: '',
        goal: '',
        preferred_group_size: 4,
      });
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to submit preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleAvailabilityChange = (slot: string) => {
    setFormData((prev) => ({
      ...prev,
      availability: prev.availability.includes(slot)
        ? prev.availability.filter((s) => s !== slot)
        : [...prev.availability, slot],
    }));
  };

  if (success) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h2 style={{ color: '#01256E' }}>Submission Successful!</h2>
        <p>Your preferences have been saved. We'll match you with a study group soon.</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h2 style={{ color: '#01256E', marginBottom: '30px' }}>Study Group Preferences</h2>

      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Course Code *
          </label>
          <input
            type="text"
            value={formData.course}
            onChange={(e) => setFormData({ ...formData, course: e.target.value.toUpperCase() })}
            required
            placeholder="e.g., CIS1200"
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px',
            }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Availability * (Select all that apply)
          </label>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '10px',
            }}
          >
            {AVAILABILITY_SLOTS.map((slot) => (
              <label
                key={slot.value}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                <input
                  type="checkbox"
                  checked={formData.availability.includes(slot.value)}
                  onChange={() => handleAvailabilityChange(slot.value)}
                  style={{ marginRight: '8px' }}
                />
                {slot.label}
              </label>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Study Style *
          </label>
          {STUDY_STYLES.map((style) => (
            <label
              key={style.value}
              style={{
                display: 'block',
                padding: '10px',
                marginBottom: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              <input
                type="radio"
                name="study_style"
                value={style.value}
                checked={formData.study_style === style.value}
                onChange={(e) => setFormData({ ...formData, study_style: e.target.value })}
                required
                style={{ marginRight: '8px' }}
              />
              {style.label}
            </label>
          ))}
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Primary Goal *
          </label>
          {GOALS.map((goal) => (
            <label
              key={goal.value}
              style={{
                display: 'block',
                padding: '10px',
                marginBottom: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              <input
                type="radio"
                name="goal"
                value={goal.value}
                checked={formData.goal === goal.value}
                onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
                required
                style={{ marginRight: '8px' }}
              />
              {goal.label}
            </label>
          ))}
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Preferred Group Size
          </label>
          <select
            value={formData.preferred_group_size}
            onChange={(e) =>
              setFormData({ ...formData, preferred_group_size: parseInt(e.target.value) })
            }
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px',
            }}
          >
            {GROUP_SIZE_OPTIONS.map((size) => (
              <option key={size} value={size}>
                {size} students
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={loading || formData.availability.length === 0}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: loading ? '#ccc' : '#01256E',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
          }}
        >
          {loading ? 'Submitting...' : 'Submit Preferences'}
        </button>
      </form>
    </div>
  );
};

