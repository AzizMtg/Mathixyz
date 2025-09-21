import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ProcessingStatus from '../components/ProcessingStatus';
import { getJobStatus } from '../services/api';
import { ArrowRightIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

interface JobStatus {
  job_id: string;
  status: string;
  created_at: string;
  ocr_done: boolean;
  llm_done: boolean;
  lesson_built: boolean;
  lesson_id?: string;
  error?: string;
}

const StatusPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setError('No job ID provided');
      setLoading(false);
      return;
    }

    const pollStatus = async () => {
      try {
        const status = await getJobStatus(jobId);
        setJobStatus(status);
        setError(null);

        // If completed and has lesson_id, we can stop polling
        if (status.status === 'completed' && status.lesson_id) {
          setLoading(false);
          return;
        }

        // If error, stop polling
        if (status.status === 'error') {
          setLoading(false);
          return;
        }

        // Continue polling if still processing
        if (status.status !== 'completed') {
          setTimeout(pollStatus, 2000); // Poll every 2 seconds
        } else {
          setLoading(false);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to get job status');
        setLoading(false);
      }
    };

    pollStatus();
  }, [jobId]);

  const handleViewLesson = () => {
    if (jobStatus?.lesson_id) {
      navigate(`/lesson/${jobStatus.lesson_id}`);
    }
  };

  const handleBackToUpload = () => {
    navigate('/');
  };

  if (!jobId) {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h1 className="text-xl font-semibold text-red-900 mb-2">Invalid Job ID</h1>
          <p className="text-red-700 mb-4">No job ID was provided in the URL.</p>
          <button
            onClick={handleBackToUpload}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700"
          >
            <ArrowLeftIcon className="h-4 w-4" />
            <span>Back to Upload</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Processing Your Math Images</h1>
        <p className="text-gray-600">Job ID: <span className="font-mono text-sm">{jobId}</span></p>
      </div>

      {/* Status Display */}
      {jobStatus && (
        <ProcessingStatus
          status={jobStatus.status}
          ocrDone={jobStatus.ocr_done}
          llmDone={jobStatus.llm_done}
          lessonBuilt={jobStatus.lesson_built}
          error={jobStatus.error}
        />
      )}

      {/* Loading State */}
      {loading && !jobStatus && (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading job status...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-900 mb-2">Error</h2>
          <p className="text-red-700 mb-4">{error}</p>
          <button
            onClick={handleBackToUpload}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700"
          >
            <ArrowLeftIcon className="h-4 w-4" />
            <span>Try Again</span>
          </button>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between">
        <button
          onClick={handleBackToUpload}
          className="inline-flex items-center space-x-2 px-4 py-2 text-gray-700 bg-gray-100 font-medium rounded-lg hover:bg-gray-200"
        >
          <ArrowLeftIcon className="h-4 w-4" />
          <span>Upload More Images</span>
        </button>

        {jobStatus?.status === 'completed' && jobStatus.lesson_id && (
          <button
            onClick={handleViewLesson}
            className="inline-flex items-center space-x-2 px-6 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700"
          >
            <span>View Lesson</span>
            <ArrowRightIcon className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Processing Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">What's happening?</h3>
        <div className="text-sm text-blue-800 space-y-1">
          <p>• <strong>OCR Processing:</strong> Extracting mathematical expressions from your images</p>
          <p>• <strong>Validation:</strong> Checking expressions with SymPy for mathematical correctness</p>
          <p>• <strong>AI Analysis:</strong> Generating step-by-step explanations and identifying key concepts</p>
          <p>• <strong>Lesson Building:</strong> Creating structured, interactive lesson content</p>
        </div>
      </div>

      {/* Time Estimate */}
      {jobStatus && jobStatus.status !== 'completed' && jobStatus.status !== 'error' && (
        <div className="text-center text-sm text-gray-500">
          <p>Processing typically takes 30-60 seconds depending on image complexity</p>
          <p className="mt-1">This page will automatically update when complete</p>
        </div>
      )}
    </div>
  );
};

export default StatusPage;
