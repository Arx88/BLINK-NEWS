
import { Input } from '@/components/ui/input';
import { Search, Filter, X } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface SearchAndFiltersProps {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  selectedCategory: string;
  setSelectedCategory: (category: string) => void;
  categories: Array<{ value: string; label: string }>;
}

export const SearchAndFilters = ({
  searchTerm,
  setSearchTerm,
  selectedCategory,
  setSelectedCategory,
  categories
}: SearchAndFiltersProps) => {
  const { isDarkMode } = useTheme();

  const clearSearch = () => setSearchTerm('');
  const clearCategory = () => setSelectedCategory('all');

  return (
    <div className={`p-6 rounded-2xl ${isDarkMode 
      ? 'bg-gradient-to-r from-gray-900/80 via-black/60 to-gray-900/80 backdrop-blur-md' 
      : 'bg-white/80 backdrop-blur-md shadow-lg'}`}>
      
      <div className="flex flex-col lg:flex-row gap-4">
        {/* Search Input */}
        <div className="flex-1 relative group">
          <Search className={`absolute left-4 top-1/2 transform -translate-y-1/2 ${isDarkMode ? 'text-blue-400' : 'text-slate-500'} w-5 h-5 transition-colors`} />
          <Input
            placeholder="Buscar noticias tecnológicas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`pl-12 pr-10 h-14 rounded-xl text-base font-medium transition-all duration-300 focus:ring-2 focus:ring-offset-2 ${isDarkMode 
              ? 'bg-gray-800/50 text-white placeholder:text-gray-400 border border-gray-700 hover:border-gray-600 focus:border-blue-500 focus:ring-blue-500/20' 
              : 'bg-white/70 text-slate-900 placeholder:text-slate-400 border border-gray-200 hover:border-gray-300 focus:border-blue-500 focus:ring-blue-500/20'}`}
          />
          {searchTerm && (
            <button
              onClick={clearSearch}
              className={`absolute right-4 top-1/2 transform -translate-y-1/2 ${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-slate-400 hover:text-slate-700'} transition-colors`}
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Category Filter */}
        <div className="min-w-[240px] relative">
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className={`h-14 rounded-xl text-base font-medium transition-all duration-300 focus:ring-2 focus:ring-offset-2 ${isDarkMode 
              ? 'bg-gray-800/50 text-white border border-gray-700 hover:border-gray-600 focus:border-purple-500 focus:ring-purple-500/20' 
              : 'bg-white/70 text-slate-900 border border-gray-200 hover:border-gray-300 focus:border-purple-500 focus:ring-purple-500/20'}`}>
              <div className="flex items-center space-x-3">
                <Filter className={`w-5 h-5 ${isDarkMode ? 'text-purple-400' : 'text-slate-500'}`} />
                <SelectValue placeholder="Seleccionar categoría" />
              </div>
            </SelectTrigger>
            <SelectContent className={`${isDarkMode 
              ? 'bg-gray-900/95 backdrop-blur-md border-gray-700' 
              : 'bg-white/95 backdrop-blur-md border-gray-200'} rounded-xl z-50 shadow-xl border`}>
              {categories.map((category) => (
                <SelectItem 
                  key={category.value} 
                  value={category.value}
                  className={`text-base py-3 px-4 rounded-lg margin-1 transition-all duration-200 ${isDarkMode 
                    ? 'text-white hover:bg-gray-800/70 focus:bg-gray-800/70 data-[highlighted]:bg-gray-800/70' 
                    : 'text-slate-800 hover:bg-slate-100/70 focus:bg-slate-100/70 data-[highlighted]:bg-slate-100/70'}`}
                >
                  {category.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {selectedCategory !== 'all' && (
            <button
              onClick={clearCategory}
              className={`absolute right-12 top-1/2 transform -translate-y-1/2 ${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-slate-400 hover:text-slate-700'} transition-colors`}
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Active Filters Display */}
      {(searchTerm || selectedCategory !== 'all') && (
        <div className="flex flex-wrap gap-2 mt-4 pt-4">
          {searchTerm && (
            <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium ${isDarkMode 
              ? 'bg-blue-500/20 text-blue-300' 
              : 'bg-blue-50 text-blue-700'}`}>
              <Search className="w-3 h-3" />
              <span>"{searchTerm}"</span>
              <button 
                onClick={clearSearch}
                className={`${isDarkMode ? 'text-blue-400 hover:text-blue-200' : 'text-blue-600 hover:text-blue-800'} ml-1`}
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}
          {selectedCategory !== 'all' && (
            <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium ${isDarkMode 
              ? 'bg-purple-500/20 text-purple-300' 
              : 'bg-purple-50 text-purple-700'}`}>
              <Filter className="w-3 h-3" />
              <span>{categories.find(c => c.value === selectedCategory)?.label}</span>
              <button 
                onClick={clearCategory}
                className={`${isDarkMode ? 'text-purple-400 hover:text-purple-200' : 'text-purple-600 hover:text-purple-800'} ml-1`}
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
