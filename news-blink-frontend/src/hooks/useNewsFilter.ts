
import { useState, useEffect, useMemo, useCallback } from 'react';

export const useNewsFilter = (news: any[], initialActiveTab: string = 'tendencias') => { // Keep the signature allowing initialActiveTab
  const [activeTab, setActiveTab] = useState(initialActiveTab);

  const [filteredNews, setFilteredNews] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Memoize expensive computations
  const searchFilteredNews = useMemo(() => {
    if (!searchTerm) return news;
    
    const lowercaseSearch = searchTerm.toLowerCase();
    return news.filter(item =>
      item.title.toLowerCase().includes(lowercaseSearch) ||
      (item.points && item.points.some((point: string) => point.toLowerCase().includes(lowercaseSearch)))
    );
  }, [news, searchTerm]);

  const categoryFilteredNews = useMemo(() => {
    if (selectedCategory === 'all') return searchFilteredNews;
    return searchFilteredNews.filter(item => item.category?.toUpperCase() === selectedCategory);
  }, [searchFilteredNews, selectedCategory]);

  const tabFilteredNews = useMemo(() => {
    let filtered = [...categoryFilteredNews];
    // console.log('[useNewsFilter] Inside tabFilteredNews memo. Start. categoryFilteredNews length:', categoryFilteredNews.length, 'activeTab:', activeTab); // Optional inner log
    switch (activeTab) {
      case 'tendencias':
        // Sort by likes (descending), then by timestamp (descending) if likes are equal.
        // This ensures that if a vote changes, the client-side sorting reflects it immediately
        // and maintains a consistent order similar to the backend's default.
        filtered.sort((a, b) => {
          const likesA = a.votes?.likes || 0;
          const likesB = b.votes?.likes || 0;

          if (likesB !== likesA) {
            return likesB - likesA; // Primary sort: likes descending
          }

          // Secondary sort: publishedAt (timestamp) descending
          const timestampA = new Date(a.publishedAt || 0).getTime();
          const timestampB = new Date(b.publishedAt || 0).getTime();
          return timestampB - timestampA;
        });
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

    // The final sort by votes (likes - dislikes) that was here has been removed.
    // The news items are now expected to be pre-sorted by likes (primary) and timestamp (secondary)
    // from the backend when fetched via /api/blinks.
    // The 'ultimas' tab still applies its own date-based sort.
    // Other tabs ('tendencias', 'rumores') will rely on the backend's default sort order
    // after their specific filtering logic is applied.

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
