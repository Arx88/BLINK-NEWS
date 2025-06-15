
import React from 'react';
import { Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useTheme } from '@/contexts/ThemeContext';
import { ShareSection } from '@/components/ShareSection';
import { NewsItem } from '@/utils/api';

interface ArticleHeaderProps {
  article: NewsItem;
}

export function ArticleHeader({ article }: ArticleHeaderProps) {
  const { isDarkMode } = useTheme();

  return (
    <header className="space-y-6">
      <div className="flex items-center space-x-4 mb-4">
        <Badge className={`${isDarkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-800'}`}>
          {article.category || 'TECNOLOGÍA'}
        </Badge>
        <div className={`flex items-center space-x-2 text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
          <Clock className="w-4 h-4" fill="currentColor" strokeWidth={0} />
          <span>{article.readTime || '5 min'}</span>
        </div>
      </div>
      
      <h1 className={`text-4xl lg:text-5xl font-bold leading-tight ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
        {article.title}
      </h1>
      
      <ShareSection articleTitle={article.title} />
    </header>
  );
}
