import React, { useState } from 'react';
import { ChevronLeftIcon, ChevronRightIcon, BookOpenIcon, LightBulbIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import MathRenderer from './MathRenderer';

interface LessonStep {
  step_id: string;
  image_index: number;
  latex: string;
  step_type: string;
  explanation: {
    problem_type: string;
    steps: Array<{
      step_number: number;
      description: string;
      latex: string;
      explanation: string;
    }>;
    key_concepts: string[];
    common_mistakes: string[];
    final_answer: string;
  };
  validation: {
    valid: boolean;
    simplified?: string;
    error?: string;
  };
}

interface LessonData {
  lesson_id: string;
  title: string;
  summary?: string;
  total_steps: number;
  steps: LessonStep[];
}

interface LessonViewerProps {
  lesson: LessonData;
}

const LessonViewer: React.FC<LessonViewerProps> = ({ lesson }) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['explanation']));

  const currentStep = lesson.steps[currentStepIndex];

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const nextStep = () => {
    if (currentStepIndex < lesson.steps.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1);
    }
  };

  const prevStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Lesson Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">{lesson.title}</h1>
            {lesson.summary && (
              <p className="text-gray-600">{lesson.summary}</p>
            )}
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">
              Step {currentStepIndex + 1} of {lesson.total_steps}
            </div>
            <div className="text-xs text-gray-400 mt-1">
              {currentStep.step_type.replace('_', ' ').toUpperCase()}
            </div>
          </div>
        </div>
      </div>

      {/* Step Navigation */}
      {lesson.steps.length > 1 && (
        <div className="flex items-center justify-between bg-white rounded-lg border border-gray-200 p-4">
          <button
            onClick={prevStep}
            disabled={currentStepIndex === 0}
            className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeftIcon className="h-4 w-4" />
            <span>Previous</span>
          </button>

          <div className="flex space-x-2">
            {lesson.steps.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentStepIndex(index)}
                className={`w-3 h-3 rounded-full ${
                  index === currentStepIndex ? 'bg-primary-600' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>

          <button
            onClick={nextStep}
            disabled={currentStepIndex === lesson.steps.length - 1}
            className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>Next</span>
            <ChevronRightIcon className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Current Step Content */}
      <div className="space-y-6">
        {/* Original Expression */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Original Expression</h2>
          <div className="bg-gray-50 rounded-lg p-4">
            <MathRenderer latex={currentStep.latex} />
          </div>
          
          {/* Validation Status */}
          <div className="mt-4 flex items-center space-x-2">
            {currentStep.validation.valid ? (
              <div className="flex items-center space-x-2 text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium">Expression validated</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2 text-red-600">
                <ExclamationTriangleIcon className="h-4 w-4" />
                <span className="text-sm font-medium">Validation error: {currentStep.validation.error}</span>
              </div>
            )}
          </div>
        </div>

        {/* Step-by-Step Explanation */}
        <div className="bg-white rounded-lg border border-gray-200">
          <button
            onClick={() => toggleSection('explanation')}
            className="w-full flex items-center justify-between p-6 text-left"
          >
            <div className="flex items-center space-x-3">
              <BookOpenIcon className="h-5 w-5 text-primary-600" />
              <h2 className="text-lg font-semibold text-gray-900">Step-by-Step Solution</h2>
            </div>
            <ChevronRightIcon 
              className={`h-5 w-5 text-gray-400 transform transition-transform ${
                expandedSections.has('explanation') ? 'rotate-90' : ''
              }`}
            />
          </button>
          
          {expandedSections.has('explanation') && (
            <div className="px-6 pb-6 space-y-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <h3 className="font-medium text-blue-900 mb-2">Problem Type</h3>
                <p className="text-blue-800">{currentStep.explanation.problem_type}</p>
              </div>
              
              <div className="space-y-4">
                {currentStep.explanation.steps.map((step, index) => (
                  <div key={index} className="border-l-4 border-primary-200 pl-4">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                        {step.step_number}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-2">{step.description}</h4>
                        <div className="bg-gray-50 rounded p-3 mb-2">
                          <MathRenderer latex={step.latex} />
                        </div>
                        <p className="text-gray-600 text-sm">{step.explanation}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Final Answer */}
              <div className="bg-green-50 rounded-lg p-4">
                <h3 className="font-medium text-green-900 mb-2">Final Answer</h3>
                <MathRenderer latex={currentStep.explanation.final_answer} />
              </div>
            </div>
          )}
        </div>

        {/* Key Concepts */}
        <div className="bg-white rounded-lg border border-gray-200">
          <button
            onClick={() => toggleSection('concepts')}
            className="w-full flex items-center justify-between p-6 text-left"
          >
            <div className="flex items-center space-x-3">
              <LightBulbIcon className="h-5 w-5 text-yellow-600" />
              <h2 className="text-lg font-semibold text-gray-900">Key Concepts</h2>
            </div>
            <ChevronRightIcon 
              className={`h-5 w-5 text-gray-400 transform transition-transform ${
                expandedSections.has('concepts') ? 'rotate-90' : ''
              }`}
            />
          </button>
          
          {expandedSections.has('concepts') && (
            <div className="px-6 pb-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-medium text-gray-900 mb-3">Important Concepts</h3>
                  <ul className="space-y-2">
                    {currentStep.explanation.key_concepts.map((concept, index) => (
                      <li key={index} className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                        <span className="text-gray-700">{concept}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h3 className="font-medium text-gray-900 mb-3">Common Mistakes</h3>
                  <ul className="space-y-2">
                    {currentStep.explanation.common_mistakes.map((mistake, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <ExclamationTriangleIcon className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700 text-sm">{mistake}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LessonViewer;
