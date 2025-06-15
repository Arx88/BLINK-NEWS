
import { useState, useEffect, useMemo, useCallback } from 'react';

export const useNewsFilter = (news: any[]) => {
  const [filteredNews, setFilteredNews] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeTab, setActiveTab] = useState('tendencias');

  // Memoize expensive computations
  const searchFilteredNews = useMemo(() => {
    if (!searchTerm) return news;
    
    const lowercaseSearch = searchTerm.toLowerCase();
    return news.filter(item =>
      item.title.toLowerCase().includes(lowercaseSearch) ||
      item.points.some((point: string) => point.toLowerCase().includes(lowercaseSearch))
    );
  }, [news, searchTerm]);

  const categoryFilteredNews = useMemo(() => {
    if (selectedCategory === 'all') return searchFilteredNews;
    return searchFilteredNews.filter(item => item.category === selectedCategory);
  }, [searchFilteredNews, selectedCategory]);

  const tabFilteredNews = useMemo(() => {
    let filtered = [...categoryFilteredNews];

    switch (activeTab) {
      case 'tendencias':
        filtered = filtered.filter(item => item.isHot || item.aiScore > 85);
        break;
      case 'rumores':
        filtered = filtered.filter(item => item.category === 'RUMORES' || item.aiScore < 90);
        break;
      case 'ultimas':
        // Sort by date for recent news
        filtered = filtered.sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime());
        break;
      default:
        break;
    }

    // Final sort by votes (except for "ultimas" tab)
    if (activeTab !== 'ultimas') {
      filtered = filtered.sort((a, b) => {
        const aVotes = (a.votes?.likes || 0) - (a.votes?.dislikes || 0);
        const bVotes = (b.votes?.likes || 0) - (b.votes?.dislikes || 0);
        return bVotes - aVotes;
      });
    }

    return filtered;
  }, [categoryFilteredNews, activeTab]);

  useEffect(() => {
    setFilteredNews(tabFilteredNews);
  }, [tabFilteredNews]);

  const clearFilters = useCallback(() => {
    setSearchTerm('');
    setSelectedCategory('all');
  }, []);

  return {
    filteredNews,
    searchTerm,
    setSearchTerm,
    selectedCategory,
    setSelectedCategory,
    activeTab,
    setActiveTab,
    clearFilters
  };
};
