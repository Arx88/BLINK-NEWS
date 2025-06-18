import { useState, useEffect, useMemo, useCallback } from 'react';
import { NewsItem } from '../utils/api'; // Import NewsItem

export const useNewsFilter = (news: NewsItem[], initialActiveTab: string = 'tendencias') => {
  console.log(`[useNewsFilter] Hook execution. Input 'news' array length: ${news.length}. Backend now handles sorting.`);
  if (news.length > 0 && typeof news.slice === 'function') {
    console.log(`[useNewsFilter] Input 'news' (first 3 items with id, votes, interestPercentage, publishedAt):`, news.slice(0, 3).map(item => ({id: item.id, votes: item.votes, interestPercentage: item.interestPercentage, publishedAt: item.publishedAt })));
  }
  const [activeTab, setActiveTab] = useState(initialActiveTab);

  const [filteredNews, setFilteredNews] = useState<NewsItem[]>([]); // Use NewsItem[]
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Memoize expensive computations
  const searchFilteredNews = useMemo(() => {
    console.log(`[useNewsFilter] Recalculating searchFilteredNews. searchTerm: "${searchTerm}", input 'news' length: ${news.length}`);
    if (!searchTerm) {
      if (news.length > 0 && typeof news.slice === 'function') {
        console.log(`[useNewsFilter] searchFilteredNews - no searchTerm. Input 'news' (first 3 with id, votes, interestPercentage):`, news.slice(0,3).map(item => ({id: item.id, votes: item.votes, interestPercentage: item.interestPercentage })));
      }
      return news;
    }
    
    const lowercaseSearch = searchTerm.toLowerCase();
    const result = news.filter(item =>
      item.title.toLowerCase().includes(lowercaseSearch) ||
      (item.points && item.points.some((point: string) => point.toLowerCase().includes(lowercaseSearch)))
    );
    console.log(`[useNewsFilter] searchFilteredNews - after filter, result length: ${result.length}`);
    if (result.length > 0 && typeof result.slice === 'function') {
        console.log(`[useNewsFilter] searchFilteredNews - result (first 3 with id, votes, interestPercentage):`, result.slice(0,3).map(item => ({id: item.id, votes: item.votes, interestPercentage: item.interestPercentage })));
    }
    return result;
  }, [news, searchTerm]);

  const categoryFilteredNews = useMemo(() => {
    console.log(`[useNewsFilter] Recalculating categoryFilteredNews. selectedCategory: "${selectedCategory}", input 'searchFilteredNews' length: ${searchFilteredNews.length}`);
    if (selectedCategory === 'all') {
      if (searchFilteredNews.length > 0 && typeof searchFilteredNews.slice === 'function') {
        console.log(`[useNewsFilter] categoryFilteredNews - category 'all'. Input 'searchFilteredNews' (first 3 with id, votes, interestPercentage):`, searchFilteredNews.slice(0,3).map(item => ({id: item.id, votes: item.votes, interestPercentage: item.interestPercentage })));
      }
      return searchFilteredNews;
    }
    const result = searchFilteredNews.filter(item => item.category?.toUpperCase() === selectedCategory);
    console.log(`[useNewsFilter] categoryFilteredNews - after filter, result length: ${result.length}`);
    if (result.length > 0 && typeof result.slice === 'function') {
        console.log(`[useNewsFilter] categoryFilteredNews - result (first 3 with id, votes, interestPercentage):`, result.slice(0,3).map(item => ({id: item.id, votes: item.votes, interestPercentage: item.interestPercentage })));
    }
    return result;
  }, [searchFilteredNews, selectedCategory]);

  const tabFilteredNews = useMemo(() => {
    console.log(`[useNewsFilter] Recalculating tabFilteredNews. activeTab: "${activeTab}", input 'categoryFilteredNews' length: ${categoryFilteredNews.length}. Backend sorting is preserved.`);
    if (categoryFilteredNews.length > 0 && typeof categoryFilteredNews.slice === 'function') {
        console.log(`[useNewsFilter] tabFilteredNews - input 'categoryFilteredNews' (first 3 with id, votes, interestPercentage, aiScore, publishedAt):`, categoryFilteredNews.slice(0,3).map(item => ({id: item.id, votes: item.votes, interestPercentage: item.interestPercentage, aiScore: item.aiScore, publishedAt: item.publishedAt })));
    }

    if (activeTab === 'rumores') {
      // Apply filtering for 'rumores'. The data from categoryFilteredNews is already sorted by the backend.
      const filteredForRumores = categoryFilteredNews.filter(item => item.category?.toUpperCase() === 'RUMORES' || (item.aiScore ?? 100) < 90);
      console.log(`[useNewsFilter] tabFilteredNews - 'rumores' tab filtered. Result length: ${filteredForRumores.length}`);
      if (filteredForRumores.length > 0 && typeof filteredForRumores.slice === 'function') {
        console.log(`[useNewsFilter] tabFilteredNews - 'rumores' result (first 3 with id, votes, interestPercentage, publishedAt):`, filteredForRumores.slice(0,3).map(item => ({id: item.id, votes: item.votes, interestPercentage: item.interestPercentage, publishedAt: item.publishedAt })));
      }
      return filteredForRumores;
    }

    // For 'tendencias', 'recientes', or any other tabs that don't have specific *filters*,
    // they just use the already sorted data from categoryFilteredNews.
    console.log(`[useNewsFilter] tabFilteredNews - tab '${activeTab}' uses pre-sorted data from categoryFilteredNews. Length: ${categoryFilteredNews.length}`);
    if (categoryFilteredNews.length > 0 && typeof categoryFilteredNews.slice === 'function') {
        console.log(`[useNewsFilter] tabFilteredNews - '${activeTab}' result (first 3 with id, votes, interestPercentage, publishedAt):`, categoryFilteredNews.slice(0,3).map(item => ({id: item.id, votes: item.votes, interestPercentage: item.interestPercentage, publishedAt: item.publishedAt })));
    }
    return categoryFilteredNews;
  }, [categoryFilteredNews, activeTab]);

  useEffect(() => {
    console.log(`[useNewsFilter] useEffect to setFilteredNews. 'tabFilteredNews' length: ${tabFilteredNews.length}`);
    if (tabFilteredNews.length > 0 && typeof tabFilteredNews.slice === 'function') {
        console.log(`[useNewsFilter] useEffect - 'tabFilteredNews' being set (first 3 with id, votes, interestPercentage):`, tabFilteredNews.slice(0,3).map(item => ({id: item.id, votes: item.votes, interestPercentage: item.interestPercentage })));
    }
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
