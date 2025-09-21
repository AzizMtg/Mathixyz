import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import UploadPage from './pages/UploadPage';
import LessonPage from './pages/LessonPage';
import StatusPage from './pages/StatusPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/status/:jobId" element={<StatusPage />} />
            <Route path="/lesson/:lessonId" element={<LessonPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
