// news-blink-frontend/src/pages/Index.tsx
import { useEffect } from 'react';
import { useNewsStore, NewsItem as Blink } from '@/store/newsStore'; // Import NewsItem as Blink
import { Header } from '@/components/Header';
import { Newsletter } from '@/components/Newsletter';
import { Footer } from '@/components/ui/footer';
import { AnimatedBackground } from '@/components/AnimatedBackground';
import { HeroSection } from '@/components/HeroSection';
import { NewsContent } from '@/components/NewsContent';
import { useNewsFilter } from '@/hooks/useNewsFilter';
import { useTheme } from '@/contexts/ThemeContext';

const Index = () => {
  const { isDarkMode } = useTheme();
  // Obteniendo TODO el estado desde el store de Zustand
  const blinks = useNewsStore(state => state.blinks);
  const isLoading = useNewsStore(state => state.isLoading);
  const error = useNewsStore(state => state.error);
  const fetchBlinks = useNewsStore(state => state.fetchBlinks);
  const heroBlink = useNewsStore(state => state.heroBlink);

  // El hook de filtro ahora recibe los blinks del store
  const {
    filteredNews,
    searchTerm,
    setSearchTerm,
    selectedCategory,
    setSelectedCategory,
    activeTab,
    setActiveTab,
    clearFilters
  } = useNewsFilter(blinks, 'tendencias');

  // El heroBlink ahora viene directamente del store, que ya tiene la lógica del blink destacado
  const heroNews = heroBlink;

  // Cargar las noticias cuando el componente se monta por primera vez
  useEffect(() => {
    fetchBlinks();
  }, [fetchBlinks]);

  const handleRefresh = () => {
    fetchBlinks();
  };

  const handleCardClick = (id: string) => {
    // Idealmente, usar React Router para la navegación sin recargar la página
    window.location.href = `/blink/${id}`;
  };

  const categories = [
    { value: 'all', label: 'Todas' },
    { value: 'TECNOLOGIA', label: 'Tecnología' },
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
          <div className="container mx-auto px-6 py-12 text-center">
            <div className={`${isDarkMode ? 'bg-red-900/20 text-red-400' : 'bg-red-50 text-red-800'} border ${isDarkMode ? 'border-red-800' : 'border-red-200'} rounded-lg p-6 max-w-md mx-auto`}>
              <p className="mb-4">{error}</p>
              <button
                onClick={handleRefresh}
                className={`px-4 py-2 rounded-lg ${isDarkMode ? 'bg-gray-800 text-white hover:bg-gray-700' : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'}`}
              >
                Intentar de nuevo
              </button>
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
          <HeroSection />

          <NewsContent
            loading={isLoading}
            filteredNews={filteredNews}
            heroNews={heroNews} // El hero news ahora es el del store
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
