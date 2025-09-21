import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { CloudArrowUpIcon, XMarkIcon, PhotoIcon } from '@heroicons/react/24/outline';

interface ImageFile {
  file: File;
  preview: string;
  tag?: string;
}

interface ImageUploadProps {
  onFilesChange: (files: ImageFile[]) => void;
  maxFiles?: number;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onFilesChange, maxFiles = 5 }) => {
  const [files, setFiles] = useState<ImageFile[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      preview: URL.createObjectURL(file),
      tag: ''
    }));
    
    const updatedFiles = [...files, ...newFiles].slice(0, maxFiles);
    setFiles(updatedFiles);
    onFilesChange(updatedFiles);
  }, [files, maxFiles, onFilesChange]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
    },
    maxFiles: maxFiles - files.length,
    disabled: files.length >= maxFiles
  });

  const removeFile = (index: number) => {
    const updatedFiles = files.filter((_, i) => i !== index);
    setFiles(updatedFiles);
    onFilesChange(updatedFiles);
  };

  const updateTag = (index: number, tag: string) => {
    const updatedFiles = files.map((file, i) => 
      i === index ? { ...file, tag } : file
    );
    setFiles(updatedFiles);
    onFilesChange(updatedFiles);
  };

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-primary-400 bg-primary-50' 
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }
          ${files.length >= maxFiles ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        
        {isDragActive ? (
          <p className="text-primary-600 font-medium">Drop the images here...</p>
        ) : (
          <div>
            <p className="text-gray-600 font-medium mb-2">
              {files.length >= maxFiles 
                ? `Maximum ${maxFiles} files reached`
                : 'Drag & drop math images here, or click to select'
              }
            </p>
            <p className="text-sm text-gray-500">
              Supports: JPEG, PNG, GIF, BMP, WebP (max {maxFiles} files)
            </p>
          </div>
        )}
      </div>

      {/* File Preview */}
      {files.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-medium text-gray-900">
            Uploaded Images ({files.length}/{maxFiles})
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {files.map((fileObj, index) => (
              <div key={index} className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-start space-x-3">
                  {/* Image Preview */}
                  <div className="flex-shrink-0">
                    <img
                      src={fileObj.preview}
                      alt={`Preview ${index + 1}`}
                      className="w-16 h-16 object-cover rounded-md border border-gray-200"
                    />
                  </div>
                  
                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {fileObj.file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(fileObj.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    
                    {/* Tag Input */}
                    <div className="mt-2">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Tag (optional)
                      </label>
                      <input
                        type="text"
                        value={fileObj.tag || ''}
                        onChange={(e) => updateTag(index, e.target.value)}
                        placeholder={`pic${index + 1}`}
                        className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
                      />
                    </div>
                  </div>
                  
                  {/* Remove Button */}
                  <button
                    onClick={() => removeFile(index)}
                    className="flex-shrink-0 p-1 text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
