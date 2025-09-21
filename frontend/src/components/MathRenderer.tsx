import React from 'react';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

interface MathRendererProps {
  latex: string;
  inline?: boolean;
  className?: string;
}

const MathRenderer: React.FC<MathRendererProps> = ({ 
  latex, 
  inline = false, 
  className = '' 
}) => {
  // Clean up LaTeX for KaTeX
  const cleanLatex = (latex: string): string => {
    return latex
      .replace(/\\text\{([^}]+)\}/g, '\\mathrm{$1}') // Convert \text to \mathrm
      .replace(/\\displaystyle/g, '') // Remove displaystyle
      .trim();
  };

  try {
    const cleanedLatex = cleanLatex(latex);
    
    if (inline) {
      return (
        <span className={className}>
          <InlineMath math={cleanedLatex} />
        </span>
      );
    } else {
      return (
        <div className={`text-center ${className}`}>
          <BlockMath math={cleanedLatex} />
        </div>
      );
    }
  } catch (error) {
    // Fallback for invalid LaTeX
    return (
      <div className={`bg-red-50 border border-red-200 rounded p-2 ${className}`}>
        <p className="text-red-600 text-sm font-mono">
          LaTeX Error: {latex}
        </p>
        <p className="text-red-500 text-xs mt-1">
          {error instanceof Error ? error.message : 'Invalid LaTeX syntax'}
        </p>
      </div>
    );
  }
};

export default MathRenderer;
