import React from 'react';
import { CheckCircleIcon, ClockIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface ProcessingStatusProps {
  status: string;
  ocrDone: boolean;
  llmDone: boolean;
  lessonBuilt: boolean;
  error?: string;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  status,
  ocrDone,
  llmDone,
  lessonBuilt,
  error
}) => {
  const steps = [
    {
      name: 'Image Processing & OCR',
      description: 'Extracting mathematical content from images',
      completed: ocrDone,
      current: status === 'processing' && !ocrDone
    },
    {
      name: 'Mathematical Analysis',
      description: 'Validating expressions and generating explanations',
      completed: llmDone,
      current: ocrDone && !llmDone
    },
    {
      name: 'Lesson Building',
      description: 'Creating structured lesson content',
      completed: lessonBuilt,
      current: llmDone && !lessonBuilt
    }
  ];

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-3">
          <ExclamationTriangleIcon className="h-6 w-6 text-red-500" />
          <div>
            <h3 className="text-lg font-medium text-red-900">Processing Error</h3>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-6">Processing Status</h3>
      
      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={index} className="flex items-start space-x-4">
            {/* Status Icon */}
            <div className="flex-shrink-0 mt-0.5">
              {step.completed ? (
                <CheckCircleIcon className="h-6 w-6 text-green-500" />
              ) : step.current ? (
                <div className="h-6 w-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
              ) : (
                <ClockIcon className="h-6 w-6 text-gray-300" />
              )}
            </div>
            
            {/* Step Content */}
            <div className="flex-1">
              <h4 className={`font-medium ${
                step.completed ? 'text-green-900' : 
                step.current ? 'text-primary-900' : 
                'text-gray-500'
              }`}>
                {step.name}
              </h4>
              <p className={`text-sm mt-1 ${
                step.completed ? 'text-green-700' : 
                step.current ? 'text-primary-700' : 
                'text-gray-400'
              }`}>
                {step.description}
              </p>
            </div>
          </div>
        ))}
      </div>
      
      {/* Progress Bar */}
      <div className="mt-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{Math.round((steps.filter(s => s.completed).length / steps.length) * 100)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(steps.filter(s => s.completed).length / steps.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default ProcessingStatus;
