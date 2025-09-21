import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LessonViewer from '../components/LessonViewer';
import { getLesson } from '../services/api';
import { ArrowLeftIcon, ShareIcon } from '@heroicons/react/24/outline';

interface LessonData {
  lesson_id: string;
  title: string;
  summary?: string;
  total_steps: number;
  steps: any[];
  created_at: string;
  job_id: string;
}

const LessonPage: React.FC = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState<LessonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLesson = async () => {
      if (!lessonId) {
        setError('No lesson ID provided');
        setLoading(false);
        return;
      }

      try {
        const lessonData = await getLesson(lessonId);
        setLesson(lessonData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load lesson');
      } finally {
        setLoading(false);
      }
    };

    fetchLesson();
  }, [lessonId]);

  const handleBackToUpload = () => {
    navigate('/');
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: lesson?.title || 'Math Lesson',
          text: lesson?.summary || 'Check out this math lesson',
          url: window.location.href,
        });
      } catch (err) {
        // User cancelled sharing
      }
    } else {
      // Fallback: copy to clipboard
      try {
        await navigator.clipboard.writeText(window.location.href);
        alert('Lesson URL copied to clipboard!');
      } catch (err) {
        console.error('Failed to copy URL:', err);
      }
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading lesson...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h1 className="text-xl font-semibold text-red-900 mb-2">Error Loading Lesson</h1>
          <p className="text-red-700 mb-4">{error}</p>
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

  if (!lesson) {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h1 className="text-xl font-semibold text-gray-900 mb-2">Lesson Not Found</h1>
          <p className="text-gray-700 mb-4">The requested lesson could not be found.</p>
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
    <div className="space-y-6">
      {/* Action Bar */}
      <div className="flex justify-between items-center">
        <button
          onClick={handleBackToUpload}
          className="inline-flex items-center space-x-2 px-4 py-2 text-gray-700 bg-gray-100 font-medium rounded-lg hover:bg-gray-200"
        >
          <ArrowLeftIcon className="h-4 w-4" />
          <span>New Upload</span>
        </button>

        <div className="flex items-center space-x-3">
          <div className="text-right text-sm text-gray-500">
            <p>Created: {new Date(lesson.created_at).toLocaleDateString()}</p>
            <p>Lesson ID: <span className="font-mono">{lesson.lesson_id}</span></p>
          </div>
          
          <button
            onClick={handleShare}
            className="inline-flex items-center space-x-2 px-4 py-2 text-gray-700 bg-gray-100 font-medium rounded-lg hover:bg-gray-200"
          >
            <ShareIcon className="h-4 w-4" />
            <span>Share</span>
          </button>
        </div>
      </div>

      {/* Lesson Content */}
      <LessonViewer lesson={lesson} />
    </div>
  );
};

export default LessonPage;
