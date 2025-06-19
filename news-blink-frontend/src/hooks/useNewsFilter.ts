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
    // Si en el futuro una pestaña necesita un filtro especial, se puede añadir aquí.
    // Por ahora, todas las pestañas usan los datos ya filtrados por categoría y búsqueda.
    return categoryFilteredNews;
  }, [categoryFilteredNews]);

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
