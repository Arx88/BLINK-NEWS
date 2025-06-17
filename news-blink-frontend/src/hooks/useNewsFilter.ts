
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
        filtered.sort((a, b) => {
          const votesA = a.votes || { likes: 0, dislikes: 0 };
          const likesA = Number(votesA.likes || 0);
          const dislikesA = Number(votesA.dislikes || 0);
          const totalVotesA = likesA + dislikesA;
          const scoreA = totalVotesA > 0 ? likesA / totalVotesA : 0.0;

          const votesB = b.votes || { likes: 0, dislikes: 0 };
          const likesB = Number(votesB.likes || 0);
          const dislikesB = Number(votesB.dislikes || 0);
          const totalVotesB = likesB + dislikesB;
          const scoreB = totalVotesB > 0 ? likesB / totalVotesB : 0.0;

          if (scoreB !== scoreA) {
            return scoreB - scoreA; // Primary: interest score descending
          }

          if (likesB !== likesA) {
            return likesB - likesA; // Secondary: absolute likes descending
          }

          // Tertiary: publishedAt (timestamp) descending
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
