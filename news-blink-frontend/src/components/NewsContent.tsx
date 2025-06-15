
import { FuturisticHeroCard } from './FuturisticHeroCard';
import { IntegratedNavigationBar } from './IntegratedNavigationBar';
import { NewsGrid } from './NewsGrid';
import { LoadingState } from './LoadingState';
import { EmptyState } from './EmptyState';
import { useTheme } from '@/contexts/ThemeContext';

interface NewsContentProps {
  loading: boolean;
  filteredNews: any[];
  heroNews: any;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  selectedCategory: string;
  setSelectedCategory: (category: string) => void;
  categories: Array<{ value: string; label: string }>;
  clearFilters: () => void;
  onCardClick: (id: string) => void;
}

export const NewsContent = ({
  loading,
  filteredNews,
  heroNews,
  activeTab,
  setActiveTab,
  searchTerm,
  setSearchTerm,
  selectedCategory,
  setSelectedCategory,
  categories,
  clearFilters,
  onCardClick
}: NewsContentProps) => {
  const { isDarkMode } = useTheme();

  if (loading) {
    return <LoadingState />;
  }

  if (filteredNews.length === 0) {
    return (
      <>
        <IntegratedNavigationBar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
          categories={categories}
        />
        <EmptyState onClearFilters={clearFilters} />
      </>
    );
  }

  return (
    <div className="space-y-12">
      {heroNews && (
        <section>
          <h2 className={`text-2xl font-bold mb-6 ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>
            Noticia Destacada
          </h2>
          <FuturisticHeroCard 
            news={heroNews} 
            onCardClick={onCardClick}
          />
        </section>
      )}

      <IntegratedNavigationBar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
        categories={categories}
      />

      {filteredNews.length > 1 && (
        <section>
          <h2 className={`text-2xl font-bold mb-6 ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>
            Más Noticias
          </h2>
          <NewsGrid 
            news={filteredNews.slice(1)}
            onCardClick={onCardClick}
          />
        </section>
      )}
    </div>
  );
};
