
import { useState, useEffect } from 'react';
import { Header } from '@/components/Header';
import { TabNavigation } from '@/components/TabNavigation';
import { SearchAndFilters } from '@/components/SearchAndFilters';
import { FuturisticHeroCard } from '@/components/FuturisticHeroCard';
import { LoadingState } from '@/components/LoadingState';
import { EmptyState } from '@/components/EmptyState';
import { Newsletter } from '@/components/Newsletter';
import { Footer } from '@/components/ui/footer';
import { useNewsFilter } from '@/hooks/useNewsFilter';
import { useRealNews } from '@/hooks/useRealNews';
import { useTheme } from '@/contexts/ThemeContext';

const Index = () => {
  const { isDarkMode } = useTheme();
  const { news, loading, error, loadNews, refreshNews } = useRealNews();
  const {
    filteredNews,
    searchTerm,
    setSearchTerm,
    selectedCategory,
    setSelectedCategory,
    activeTab,
    setActiveTab,
    clearFilters
  } = useNewsFilter(news);

  const [heroNews, setHeroNews] = useState(null);

  useEffect(() => {
    loadNews('ultimas');
  }, []);

  useEffect(() => {
    loadNews(activeTab);
  }, [activeTab]);

  useEffect(() => {
    if (filteredNews.length > 0) {
      setHeroNews(filteredNews[0]);
    }
  }, [filteredNews]);

  const handleRefresh = () => {
    refreshNews(activeTab);
  };

  const handleCardClick = (id: string) => {
    window.location.href = `/blink/${id}`;
  };

  const categories = [
    { value: 'all', label: 'Todas las categorías' },
    { value: 'TECNOLOGÍA', label: 'Tecnología' },
    { value: 'IA', label: 'Inteligencia Artificial' },
    { value: 'BLOCKCHAIN', label: 'Blockchain' },
    { value: 'STARTUPS', label: 'Startups' },
    { value: 'GAMING', label: 'Gaming' },
    { value: 'RUMORES', label: 'Rumores' },
  ];

  if (error) {
    return (
      <div className={`min-h-screen ${isDarkMode ? 'bg-black' : 'bg-white'}`}>
        <Header onRefresh={handleRefresh} />
        <div className="container mx-auto px-6 py-12">
          <div className="text-center">
            <div className={`${isDarkMode ? 'bg-red-900/20 border-red-800' : 'bg-red-50 border-red-200'} border rounded-lg p-6 max-w-md mx-auto`}>
              <p className={`${isDarkMode ? 'text-red-400' : 'text-red-800'} mb-4`}>{error}</p>
              <button 
                onClick={handleRefresh}
                className={`px-4 py-2 rounded-lg ${isDarkMode ? 'bg-gray-800 text-white hover:bg-gray-700' : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'}`}
              >
                Intentar nuevamente
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${isDarkMode ? 'bg-black' : 'bg-white'}`}>
      <Header onRefresh={handleRefresh} />
      
      <main className="container mx-auto px-6 py-8 space-y-12">
        <div className="text-center space-y-4">
          <h1 className={`text-4xl lg:text-6xl font-black tracking-tighter ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>
            El futuro de las noticias
          </h1>
          <p className={`text-xl ${isDarkMode ? 'text-gray-400' : 'text-slate-600'} max-w-2xl mx-auto`}>
            Mantente al día con las últimas tendencias tecnológicas en formato BLINK
          </p>
        </div>

        <TabNavigation 
          activeTab={activeTab} 
          setActiveTab={setActiveTab}
        />

        <SearchAndFilters
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
          categories={categories}
        />

        {loading ? (
          <LoadingState />
        ) : filteredNews.length === 0 ? (
          <EmptyState 
            onClearFilters={clearFilters}
          />
        ) : (
          <div className="space-y-12">
            {heroNews && (
              <section>
                <h2 className={`text-2xl font-bold mb-6 ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>
                  Noticia Destacada
                </h2>
                <FuturisticHeroCard 
                  news={heroNews} 
                  onCardClick={handleCardClick}
                />
              </section>
            )}

            {filteredNews.length > 1 && (
              <section>
                <h2 className={`text-2xl font-bold mb-6 ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>
                  Más Noticias
                </h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {filteredNews.slice(1).map((news) => (
                    <FuturisticHeroCard 
                      key={news.id}
                      news={news} 
                      onCardClick={handleCardClick}
                    />
                  ))}
                </div>
              </section>
            )}
          </div>
        )}

        <Newsletter />
      </main>
      
      <Footer />
    </div>
  );
};

export default Index;
