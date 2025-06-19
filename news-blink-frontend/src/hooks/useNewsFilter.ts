// news-blink-frontend/src/hooks/useNewsFilter.ts
import { useState, useEffect, useMemo, useCallback } from 'react';
import { NewsItem as Blink } from '../store/newsStore'; // Import NewsItem as Blink

// El hook ahora usa el tipo 'Blink' (que es NewsItem) y establece un valor por defecto para 'news'
export const useNewsFilter = (news: Blink[] = [], initialActiveTab: string = 'tendencias') => {
  const [activeTab, setActiveTab] = useState(initialActiveTab);
  const [filteredNews, setFilteredNews] = useState<Blink[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Filtrado por término de búsqueda (título y resumen)
  const searchFilteredNews = useMemo(() => {
    if (!searchTerm) {
      return news;
    }
    const lowercaseSearch = searchTerm.toLowerCase();
    return news.filter(item =>
      item.title.toLowerCase().includes(lowercaseSearch) ||
      item.summary.toLowerCase().includes(lowercaseSearch)
    );
  }, [news, searchTerm]);

  // Filtrado por categoría
  const categoryFilteredNews = useMemo(() => {
    if (selectedCategory === 'all') {
      return searchFilteredNews;
    }
    return searchFilteredNews.filter(item => item.category?.toUpperCase() === selectedCategory.toUpperCase());
  }, [searchFilteredNews, selectedCategory]);

  // La lógica de filtrado por pestaña se mantiene, pero ya no necesita ordenar.
  // El ordenamiento principal ya viene del backend.
  const tabFilteredNews = useMemo(() => {
    console.log(`[useNewsFilter] Sorting triggered. Active Tab: '${activeTab}'`);
    console.log(`[useNewsFilter] Items to sort (first 3):`, categoryFilteredNews.slice(0, 3).map(item => ({ id: item.id, title: item.title, publishedAt: item.publishedAt, likes: item.votes?.likes })));
    const newsToSort = [...categoryFilteredNews]; // Create a shallow copy to sort

    if (activeTab === 'ultimas') { // Assuming 'ultimas' is the identifier for the "Latest" tab
      console.log('[useNewsFilter] Applying DATE sort for "ultimas" tab.');
      // Sort by timestamp descending (newest first)
      // Assuming timestamp is a string that can be compared (e.g., ISO date string)
      newsToSort.sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime());
    } else if (activeTab === 'tendencias') { // Assuming 'tendencias' is for "Trends"
      console.log('[useNewsFilter] Applying LIKES sort for "tendencias" tab.');
      // Sort by likes descending (most popular first)
      newsToSort.sort((a, b) => (b.votes?.likes || 0) - (a.votes?.likes || 0));
    } else {
      console.log('[useNewsFilter] No specific sort applied for tab:', activeTab);
    }
    // Add other conditions or a default sort if necessary for other tabs

    console.log(`[useNewsFilter] Sorted items (first 3):`, newsToSort.slice(0, 3).map(item => ({ id: item.id, title: item.title, publishedAt: item.publishedAt, likes: item.votes?.likes })));
    return newsToSort;
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
