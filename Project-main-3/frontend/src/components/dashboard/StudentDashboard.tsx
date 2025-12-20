/**
 * Student dashboard component.
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { submissionsAPI, matchesAPI } from '../../services/api';
import { Submission, Match } from '../../services/types';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { PreferenceForm } from '../forms/PreferenceForm';
import { useAuth as useAuthContext } from '../../hooks/useAuth';

export const StudentDashboard: React.FC = () => {
  const { authStatus } = useAuthContext();
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [match, setMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'submit' | 'status'>('submit');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Try to get user's submission
      // Note: API needs to be updated to return user's submission
      // For now, we'll show the form
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

  const loadMatch = async (course: string) => {
    try {
      const matchData = await matchesAPI.get(course);
      setMatch(matchData);
    } catch (error) {
      // No match found
      setMatch(null);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{ color: '#01256E' }}>GroupMeet Dashboard</h1>
        <p>Welcome, {authStatus.pennkey}!</p>
      </div>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '30px', borderBottom: '1px solid #ddd' }}>
        <button
          onClick={() => setActiveTab('submit')}
          style={{
            padding: '10px 20px',
            background: activeTab === 'submit' ? '#01256E' : 'transparent',
            color: activeTab === 'submit' ? 'white' : '#01256E',
            border: 'none',
            borderBottom: activeTab === 'submit' ? '3px solid #01256E' : '3px solid transparent',
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
        >
          Submit Preferences
        </button>
        <button
          onClick={() => setActiveTab('status')}
          style={{
            padding: '10px 20px',
            background: activeTab === 'status' ? '#01256E' : 'transparent',
            color: activeTab === 'status' ? 'white' : '#01256E',
            border: 'none',
            borderBottom: activeTab === 'status' ? '3px solid #01256E' : '3px solid transparent',
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
        >
          My Status
        </button>
      </div>

      {activeTab === 'submit' && <PreferenceForm />}

      {activeTab === 'status' && (
        <div>
          <h2 style={{ color: '#01256E', marginBottom: '20px' }}>My Submissions & Matches</h2>
          {submission ? (
            <div style={{ padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '4px', marginBottom: '20px' }}>
              <h3>Course: {submission.course}</h3>
              <p>Status: {submission.status}</p>
              <p>Submitted: {submission.created_at ? new Date(submission.created_at).toLocaleDateString() : 'N/A'}</p>
              <button
                onClick={() => loadMatch(submission.course)}
                style={{
                  marginTop: '10px',
                  padding: '8px 16px',
                  backgroundColor: '#01256E',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Check for Match
              </button>
            </div>
          ) : (
            <p>No submissions yet. Go to the "Submit Preferences" tab to get started.</p>
          )}

          {match && (
            <div style={{ padding: '20px', backgroundColor: '#e8f5e9', borderRadius: '4px', marginTop: '20px' }}>
              <h3 style={{ color: '#01256E' }}>Your Study Group</h3>
              <p><strong>Course:</strong> {match.course}</p>
              <p><strong>Group ID:</strong> {match.group_id}</p>
              <p><strong>Suggested Time:</strong> {match.suggested_meeting_time.replace('_', ' ')}</p>
              <p><strong>Compatibility Score:</strong> {(match.compatibility_score * 100).toFixed(1)}%</p>
              <h4 style={{ marginTop: '15px' }}>Group Members:</h4>
              <ul>
                {match.members.map((member, idx) => (
                  <li key={idx}>
                    {member.name || member.pennkey} - {member.email}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

