
import { FuturisticHeroCard } from './FuturisticHeroCard';
import { RumorHeroCard } from './RumorHeroCard';
import { IntegratedNavigationBar } from './IntegratedNavigationBar';
import { NewsGrid } from './NewsGrid';
import { RumorGrid } from './RumorGrid';
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

  const isRumorTab = activeTab === 'rumores';

  return (
    <div className="space-y-12">
      {heroNews && (
        <section>
          <h2 className={`text-2xl font-bold mb-6 ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>
            {isRumorTab ? 'Rumor Destacado' : 'Noticia Destacada'}
          </h2>
          {isRumorTab ? (
            <RumorHeroCard 
              news={heroNews} 
              onCardClick={onCardClick}
            />
          ) : (
            <FuturisticHeroCard 
              news={heroNews} 
              onCardClick={onCardClick}
            />
          )}
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
            {isRumorTab ? 'Más Rumores' : 'Más Noticias'}
          </h2>
          {isRumorTab ? (
            <RumorGrid 
              news={filteredNews.slice(1)}
              onCardClick={onCardClick}
            />
          ) : (
            <NewsGrid 
              news={filteredNews.slice(1)}
              onCardClick={onCardClick}
            />
          )}
        </section>
      )}
    </div>
  );
};
