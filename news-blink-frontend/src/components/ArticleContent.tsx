import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import ReactMarkdown from 'react-markdown'; // Import the library

interface ArticleContentProps {
  articleContent?: string;
}

export function ArticleContent({ articleContent }: ArticleContentProps) {
  const { isDarkMode } = useTheme();

  if (!articleContent || articleContent.trim() === "") {
    return (
      <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
        Contenido no disponible.
      </p>
    );
  }

  // Apply Tailwind prose classes to a wrapper div.
  // ReactMarkdown will generate HTML elements that prose can style.
  // Using dark:prose-invert for Tailwind CSS dark mode compatibility with typography.
  return (
    <div className={`prose prose-lg max-w-none ${isDarkMode ? 'dark:prose-invert' : ''}`}>
      <ReactMarkdown>
        {articleContent}
      </ReactMarkdown>
    </div>
  );
}
