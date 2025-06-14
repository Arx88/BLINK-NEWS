
import { Search, Filter } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

interface ActiveFiltersProps {
  searchTerm: string;
  selectedCategory: string;
  categories: Array<{ value: string; label: string }>;
  onClearSearch: () => void;
  onClearCategory: () => void;
}

export const ActiveFilters = ({
  searchTerm,
  selectedCategory,
  categories,
  onClearSearch,
  onClearCategory
}: ActiveFiltersProps) => {
  const { isDarkMode } = useTheme();

  if (!searchTerm && selectedCategory === 'all') {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-2 mt-4">
      {searchTerm && (
        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs ${isDarkMode 
          ? 'bg-gray-800 text-white' 
          : 'bg-gray-100 text-gray-800'}`}>
          <Search className="w-3 h-3" />
          <span>"{searchTerm}"</span>
          <button 
            onClick={onClearSearch}
            className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-800'}`}
          >
            ×
          </button>
        </div>
      )}
      {selectedCategory !== 'all' && (
        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs ${isDarkMode 
          ? 'bg-gray-800 text-white' 
          : 'bg-gray-100 text-gray-800'}`}>
          <Filter className="w-3 h-3" />
          <span>{categories.find(c => c.value === selectedCategory)?.label}</span>
          <button 
            onClick={onClearCategory}
            className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-800'}`}
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
};
