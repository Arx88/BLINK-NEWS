
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

  console.log('[NewsContent] Props received:', {
    loading,
    filteredNewsLength: filteredNews.length,
    // Optional: log first item to verify data structure if needed
    // filteredNewsFirstItem: filteredNews.length > 0 ? filteredNews[0] : 'N/A',
    heroNewsExists: !!heroNews,
    searchTerm,
    selectedCategory,
    activeTab
  });

  if (loading) {
    console.log('[NewsContent] Rendering LoadingState because loading is true.');
    return <LoadingState />;
  }

  if (filteredNews.length === 0) {
    if (searchTerm || selectedCategory !== 'all') {
      console.log('[NewsContent] Rendering EmptyState because filteredNews is empty AND search/category filters ARE active.');
    } else {
      console.log('[NewsContent] Rendering EmptyState because filteredNews is empty AND no search/category filters are active.');
    }
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

  // If we reach here, filteredNews.length > 0
  console.log(`[NewsContent] Conditions met to render main content with NewsGrid. Filtered news length: ${filteredNews.length}`);
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

      {/* This condition means if there's only 1 news item, it was shown as hero, so no "Más Noticias" needed.
          If more than 1, the rest are shown in NewsGrid.
          If heroNews is null, all filteredNews (if any) would be in NewsGrid.
          The existing logic for heroNews and slicing seems to handle this,
          but the log for NewsGrid should ideally be right before it's rendered.
          However, the structure returns a single block.
          The log above this return statement already covers that NewsGrid will be rendered if filteredNews.length > 0.
      */}
      {filteredNews.length > 1 && ( // This implies heroNews was shown, and there are more items.
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
      {/* Case: filteredNews.length is 1, and it was shown as heroNews. Nothing else to show in grid. */}
      {/* Case: filteredNews.length > 0, but no heroNews (e.g. heroNews logic changes or is null).
          The current code does not explicitly render NewsGrid for filteredNews[0] if heroNews is null.
          It seems heroNews is expected to be filteredNews[0]. If so, and length is 1, this section is skipped.
          This might be an area for future refinement if heroNews is not always filteredNews[0].
          For now, sticking to adding logs to existing structure.
      */}
       {/* Fallback log if none of the above conditions are met - This should ideally not be reached in current structure */}
      {/*
        The current structure with a final return for filteredNews.length > 0 means a fallback log here isn't quite right.
        If it's not loading and not empty, it renders the main content.
        A true fallback would be if it didn't meet any of these.
        Let's add a log for the case where filteredNews.length is 1 and heroNews is present, so "Más Noticias" is skipped.
      */}
      {heroNews && filteredNews.length === 1 && (
        console.log('[NewsContent] Rendering main content with HeroNews only (filteredNews.length is 1). No "Más Noticias" grid.')
      )}
      {!heroNews && filteredNews.length > 0 && (
         // This case is not explicitly handled by the current NewsGrid rendering logic if heroNews is null.
         // The IntegratedNavigationBar is shown, but NewsGrid might not show all items.
         // The current NewsGrid is only for filteredNews.slice(1).
         // This indicates a potential area for future code improvement if heroNews can be null while filteredNews is not empty.
         // For now, logging the observation.
        console.log('[NewsContent] Rendering main content. heroNews is not present, but filteredNews has items. NewsGrid will show filteredNews.slice(1).')
      )}

    </div>
  );
};
