
import { useState, useEffect } from 'react';
import { Header } from '@/components/Header';
import { Newsletter } from '@/components/Newsletter';
import { Footer } from '@/components/ui/footer';
import { AnimatedBackground } from '@/components/AnimatedBackground';
import { HeroSection } from '@/components/HeroSection';
import { NewsContent } from '@/components/NewsContent';
import { MinimalSelectTest } from '@/components/MinimalSelectTest'; // Import the test component
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
  } = useNewsFilter(news, 'ultimas');

  const [heroNews, setHeroNews] = useState(null);

  // REMOVED:
  // useEffect(() => {
  //   loadNews('ultimas');
  // }, []);

  useEffect(() => {
    if (activeTab) { // Ensure activeTab is truthy before loading
      loadNews(activeTab);
    }
  }, [activeTab, loadNews]); // loadNews is from useRealNews

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
      <div className="min-h-screen relative">
        <AnimatedBackground />
        <div className="relative z-10">
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
      </div>
    );
  }

  return (
    <div className="min-h-screen relative">
      <AnimatedBackground />
      <div className="relative z-10">
        <Header onRefresh={handleRefresh} />
        
        <main className="container mx-auto px-6 py-8 space-y-8">
          {/* Render the MinimalSelectTest component here */}
          <div className="my-8"> {/* Added a div for spacing */}
            <MinimalSelectTest />
          </div>

          <HeroSection />

          <NewsContent
            loading={loading}
            filteredNews={filteredNews}
            heroNews={heroNews}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            selectedCategory={selectedCategory}
            setSelectedCategory={setSelectedCategory}
            categories={categories}
            clearFilters={clearFilters}
            onCardClick={handleCardClick}
          />

          <Newsletter />
        </main>
        
        <Footer />
      </div>
    </div>
  );
};

export default Index;
