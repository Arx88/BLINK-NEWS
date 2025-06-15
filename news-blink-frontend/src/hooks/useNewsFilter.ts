
import { useState, useEffect, useMemo, useCallback } from 'react';

export const useNewsFilter = (news: any[], initialActiveTab: string = 'tendencias') => { // Keep the signature allowing initialActiveTab
  const [activeTab, setActiveTab] = useState(initialActiveTab);

  // THIS IS THE CRUCIAL LOG - ensuring it's exactly this:
  console.log(
    '[useNewsFilter] Hook called/re-rendered. Received initialActiveTab:', initialActiveTab,
    '. Current internal activeTab state (from useState):', activeTab,
    '. Input news length:', news.length
  );
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
  console.log('[useNewsFilter] searchFilteredNews computed. Length:', searchFilteredNews.length, 'ActiveSearchTerm:', searchTerm, 'First item:', searchFilteredNews.length > 0 ? searchFilteredNews[0] : 'N/A');

  const categoryFilteredNews = useMemo(() => {
    if (selectedCategory === 'all') return searchFilteredNews;
    return searchFilteredNews.filter(item => item.category === selectedCategory);
  }, [searchFilteredNews, selectedCategory]);
  console.log('[useNewsFilter] categoryFilteredNews computed. Length:', categoryFilteredNews.length, 'SelectedCategory:', selectedCategory, 'First item:', categoryFilteredNews.length > 0 ? categoryFilteredNews[0] : 'N/A');

  const tabFilteredNews = useMemo(() => {
    let filtered = [...categoryFilteredNews];
    // console.log('[useNewsFilter] Inside tabFilteredNews memo. Start. categoryFilteredNews length:', categoryFilteredNews.length, 'activeTab:', activeTab); // Optional inner log
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
  console.log('[useNewsFilter] tabFilteredNews (variable from useMemo) computed. Length:', tabFilteredNews.length, 'ActiveTab:', activeTab, 'First item:', tabFilteredNews.length > 0 ? tabFilteredNews[0] : 'N/A');

  useEffect(() => {
    console.log('[useNewsFilter] useEffect for tabFilteredNews. tabFilteredNews length:', tabFilteredNews.length, 'First item if exists:', tabFilteredNews.length > 0 ? tabFilteredNews[0] : 'N/A');
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
