import { useCallback } from 'react'; // Import useCallback, useState is no longer needed directly
// No longer importing transformBlinkToNewsItem as the store handles transformation
// Importing NewsItem from utils/api for type consistency, assuming store uses the same.
import { NewsItem } from '../utils/api';
import { useNewsStore } from '../store/newsStore'; // Import the Zustand store

// NewsItem interface definition is removed from here, will use the one from utils/api via store or direct import.

export const useRealNews = () => {
  // Get state and actions from the Zustand store
  const {
    news,
    loading,
    error,
    fetchNews: storeFetchNews
  } = useNewsStore(state => ({
    news: state.news,
    loading: state.loading,
    error: state.error,
    fetchNews: state.fetchNews,
  }));

  // The loadNews function provided by the hook.
  // It now calls the fetchNews action from the store.
  // The 'tab' parameter is kept for compatibility with existing components (e.g., Index.tsx useEffect)
  // but it's not used by storeFetchNews.
  const loadNews = useCallback(async (_tab?: string) => { // tab parameter is unused
    await storeFetchNews();
  }, [storeFetchNews]);

  // The refreshNews function provided by the hook.
  // It also calls the fetchNews action from the store via the local loadNews.
  const refreshNews = useCallback((tab?: string) => { // tab parameter is unused
    loadNews(tab); // Calls the refactored loadNews which calls storeFetchNews
  }, [loadNews]);

  return {
    news,
    loading,
    error,
    loadNews,
    refreshNews,
    updateSingleNewsItem
  };
};
