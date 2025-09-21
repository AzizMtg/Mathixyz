import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">∫</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Math Scrap</h1>
              <p className="text-sm text-gray-500">Convert math images to lessons</p>
            </div>
          </Link>
          
          <nav className="flex items-center space-x-6">
            <Link 
              to="/" 
              className="text-gray-600 hover:text-primary-600 transition-colors font-medium"
            >
              Upload
            </Link>
            <a 
              href="http://localhost:8000/docs" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-primary-600 transition-colors font-medium"
            >
              API Docs
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
