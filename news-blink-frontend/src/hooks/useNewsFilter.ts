
import { useState, useEffect, useMemo, useCallback } from 'react';

export const useNewsFilter = (news: any[], initialActiveTab: string = 'tendencias') => { // Keep the signature allowing initialActiveTab
  console.log(`[useNewsFilter] Hook execution. Input 'news' array length: ${news.length}`);
  if (news.length > 0 && typeof news.slice === 'function') {
    console.log(`[useNewsFilter] Input 'news' (first 3 items with votes):`, news.slice(0, 3).map(item => ({id: item.id, votes: item.votes, aiScore: item.aiScore, publishedAt: item.publishedAt })));
  }
  const [activeTab, setActiveTab] = useState(initialActiveTab);

  const [filteredNews, setFilteredNews] = useState<any[]>([]);
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
    console.log(`[useNewsFilter] tabFilteredNews - after tab logic, result length: ${filtered.length}`);
    if (filtered.length > 0 && typeof filtered.slice === 'function') {
        console.log(`[useNewsFilter] tabFilteredNews - result (first 3 with votes, aiScore, publishedAt):`, filtered.slice(0,3).map(item => ({id: item.id, votes: item.votes, aiScore: item.aiScore, publishedAt: item.publishedAt })));
    }
    return filtered;
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
