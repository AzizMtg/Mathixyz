import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ImageUpload from '../components/ImageUpload';
import { uploadImages } from '../services/api';
import { ArrowRightIcon } from '@heroicons/react/24/outline';

interface ImageFile {
  file: File;
  preview: string;
  tag?: string;
}

const UploadPage: React.FC = () => {
  const [files, setFiles] = useState<ImageFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Please select at least one image to upload');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      const tags: string[] = [];

      files.forEach((fileObj, index) => {
        formData.append('files', fileObj.file);
        tags.push(fileObj.tag || `pic${index + 1}`);
      });

      if (tags.length > 0) {
        formData.append('tags', tags.join(','));
      }

      const response = await uploadImages(formData);
      
      // Navigate to status page
      navigate(`/status/${response.job_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Convert Math Images to Lessons
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Upload images of handwritten math problems and get step-by-step explanations 
          with interactive lessons powered by OCR and AI.
        </p>
      </div>

      {/* Upload Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Upload Math Images</h2>
        
        <ImageUpload 
          onFilesChange={setFiles}
          maxFiles={5}
        />

        {/* Error Display */}
        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600 font-medium">{error}</p>
          </div>
        )}

        {/* Upload Button */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={handleUpload}
            disabled={files.length === 0 || isUploading}
            className="flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isUploading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>Generate Lesson</span>
                <ArrowRightIcon className="h-4 w-4" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <span className="text-blue-600 text-xl font-bold">OCR</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Recognition</h3>
          <p className="text-gray-600">
            Advanced OCR technology extracts mathematical expressions from handwritten images
            with high accuracy.
          </p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
            <span className="text-green-600 text-xl font-bold">∫</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Validation</h3>
          <p className="text-gray-600">
            SymPy validates mathematical expressions and provides simplified forms
            to ensure accuracy.
          </p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
            <span className="text-purple-600 text-xl font-bold">AI</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Explanations</h3>
          <p className="text-gray-600">
            AI-powered step-by-step explanations help you understand the solution process
            and key concepts.
          </p>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">Tips for Best Results</h3>
        <ul className="space-y-2 text-blue-800">
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 mt-1">•</span>
            <span>Ensure images are clear and well-lit with minimal shadows</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 mt-1">•</span>
            <span>Write math expressions clearly with good spacing between symbols</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 mt-1">•</span>
            <span>Use tags like "pic1", "pic2" to organize multiple related problems</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 mt-1">•</span>
            <span>Supported formats: JPEG, PNG, GIF, BMP, WebP (max 10MB each)</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default UploadPage;
