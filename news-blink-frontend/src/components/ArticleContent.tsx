import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';

interface ArticleContentProps {
  articleContent?: string; // Prop to accept article content
}

export function ArticleContent({ articleContent }: ArticleContentProps) {
  const { isDarkMode } = useTheme();

  if (!articleContent) {
    return (
      <p className={isDarkMode ? 'text-gray-400' : 'text-gray-600'}>
        Contenido no disponible.
      </p>
    );
  }

  // Render the content, preserving newlines and wrapping text.
  // The 'prose' classes might provide some default styling for HTML-like content,
  // but for plain text with newlines, 'white-space: pre-line' is key.
  // Adjust className as needed if 'prose' conflicts or is not desired.
  return (
    <div
      className={`prose prose-lg max-w-none ${isDarkMode ? 'text-gray-300 prose-invert' : 'text-gray-700'}`}
      style={{ whiteSpace: 'pre-line' }}
    >
      {articleContent}
    </div>
  );
}
