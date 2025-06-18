import { useState, useEffect, useMemo, useCallback } from 'react';
import { NewsItem } from '../utils/api'; // Import NewsItem

const CONFIDENCE_FACTOR = 5;

const calculateInterest = (newsItem: NewsItem): number => {
  const likes = newsItem.votes?.likes ?? 0;
  const dislikes = newsItem.votes?.dislikes ?? 0;
  const totalVotes = likes + dislikes;
  const netVotes = likes - dislikes;

  if (totalVotes === 0) {
    return 0;
  }
  // Using the formula: (net_vote_difference / (total_votes + confidence_factor_c)) * 100.0
  return (netVotes / (totalVotes + CONFIDENCE_FACTOR)) * 100;
};

export const useNewsFilter = (news: NewsItem[], initialActiveTab: string = 'tendencias') => {
  console.log(`[useNewsFilter] Hook execution. Input 'news' array length: ${news.length}`);
  if (news.length > 0 && typeof news.slice === 'function') {
    console.log(`[useNewsFilter] Input 'news' (first 3 items with votes):`, news.slice(0, 3).map(item => ({id: item.id, votes: item.votes, publishedAt: item.publishedAt })));
  }
  const [activeTab, setActiveTab] = useState(initialActiveTab);

  const [filteredNews, setFilteredNews] = useState<NewsItem[]>([]); // Use NewsItem[]
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Memoize expensive computations
  const searchFilteredNews = useMemo(() => {
    console.log(`[useNewsFilter] Recalculating searchFilteredNews. searchTerm: "${searchTerm}", input 'news' length: ${news.length}`);
    if (!searchTerm) {
      // console.log(`[useNewsFilter] searchFilteredNews - no searchTerm, returning original 'news' (length: ${news.length})`);
      // To see if 'news' itself has the updated item:
      if (news.length > 0 && typeof news.slice === 'function') {
        console.log(`[useNewsFilter] searchFilteredNews - no searchTerm. Input 'news' (first 3 with votes):`, news.slice(0,3).map(item => ({id: item.id, votes: item.votes })));
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
        console.log(`[useNewsFilter] searchFilteredNews - result (first 3 with votes):`, result.slice(0,3).map(item => ({id: item.id, votes: item.votes })));
    }
    return result;
  }, [news, searchTerm]);

  const categoryFilteredNews = useMemo(() => {
    console.log(`[useNewsFilter] Recalculating categoryFilteredNews. selectedCategory: "${selectedCategory}", input 'searchFilteredNews' length: ${searchFilteredNews.length}`);
    if (selectedCategory === 'all') {
      // console.log(`[useNewsFilter] categoryFilteredNews - category 'all', returning 'searchFilteredNews' (length: ${searchFilteredNews.length})`);
      if (searchFilteredNews.length > 0 && typeof searchFilteredNews.slice === 'function') {
        console.log(`[useNewsFilter] categoryFilteredNews - category 'all'. Input 'searchFilteredNews' (first 3 with votes):`, searchFilteredNews.slice(0,3).map(item => ({id: item.id, votes: item.votes })));
      }
      return searchFilteredNews;
    }
    const result = searchFilteredNews.filter(item => item.category?.toUpperCase() === selectedCategory);
    console.log(`[useNewsFilter] categoryFilteredNews - after filter, result length: ${result.length}`);
    if (result.length > 0 && typeof result.slice === 'function') {
        console.log(`[useNewsFilter] categoryFilteredNews - result (first 3 with votes):`, result.slice(0,3).map(item => ({id: item.id, votes: item.votes })));
    }
    return result;
  }, [searchFilteredNews, selectedCategory]);

  const tabFilteredNews = useMemo(() => {
    console.log(`[useNewsFilter] Recalculating tabFilteredNews. activeTab: "${activeTab}", input 'categoryFilteredNews' length: ${categoryFilteredNews.length}`);
    if (categoryFilteredNews.length > 0 && typeof categoryFilteredNews.slice === 'function') {
        console.log(`[useNewsFilter] tabFilteredNews - input 'categoryFilteredNews' (first 3 with votes, aiScore, publishedAt):`, categoryFilteredNews.slice(0,3).map(item => ({id: item.id, votes: item.votes, aiScore: item.aiScore, publishedAt: item.publishedAt })));
    }
    let sortedNews = [...categoryFilteredNews]; // Use a new variable for clarity if preferred, or just 'filtered'

    console.log(`[useNewsFilter] tabFilteredNews processing for tab: ${activeTab}`);

    if (activeTab === 'tendencias') {
      sortedNews = [...categoryFilteredNews].sort((a, b) => {
        const interestA = calculateInterest(a); // Use new function
        const interestB = calculateInterest(b); // Use new function

        if (interestA !== interestB) {
          return interestB - interestA; // Sort by interest DESC
        }

        // Tie-breaker: Sort by publication date DESC
        const dateA = new Date(a.publishedAt).getTime();
        const dateB = new Date(b.publishedAt).getTime();
        return dateB - dateA;
      });
    } else if (activeTab === 'recientes') { // Changed 'ultimas' to 'recientes'
      sortedNews = [...categoryFilteredNews].sort(
        (a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
      );
    } else if (activeTab === 'rumores') { // Kept 'rumores' logic if it exists, adjust as needed
      // Assuming 'rumores' might have specific filtering, then default sort or its own.
      // For this example, let's assume it might filter and then use default (filesystem) order or date.
      // If 'rumores' also needs interest sort, that would be specified.
      // The original code filtered by category RUMORES OR aiScore < 90 for 'rumores'.
      // This seems like a filter, not a sort. Sorting for 'rumores' is not specified beyond this.
      // Let's assume after filtering, it falls back to date sort like 'recientes' for consistency if no other sort is specified.
      sortedNews = categoryFilteredNews.filter(item => item.category?.toUpperCase() === 'RUMORES' || (item.aiScore ?? 100) < 90)
        .sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()); // Example: sort rumors by date too
    }
    // Add other tab conditions if they exist. If no specific sort for a tab, it uses categoryFilteredNews as is.

    console.log(`[useNewsFilter] tabFilteredNews - after tab logic for '${activeTab}', result length: ${sortedNews.length}`);
    if (sortedNews.length > 0 && typeof sortedNews.slice === 'function') {
        console.log(`[useNewsFilter] tabFilteredNews - result (first 3 with votes, publishedAt):`, sortedNews.slice(0,3).map(item => ({id: item.id, votes: item.votes, interest: calculateInterest(item) , publishedAt: item.publishedAt })));
    }
    return sortedNews;
  }, [categoryFilteredNews, activeTab]);

  useEffect(() => {
    console.log(`[useNewsFilter] useEffect to setFilteredNews. 'tabFilteredNews' length: ${tabFilteredNews.length}`);
    if (tabFilteredNews.length > 0 && typeof tabFilteredNews.slice === 'function') {
        console.log(`[useNewsFilter] useEffect - 'tabFilteredNews' being set (first 3 with votes):`, tabFilteredNews.slice(0,3).map(item => ({id: item.id, votes: item.votes })));
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
