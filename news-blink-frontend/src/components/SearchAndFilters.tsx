
import { Input } from '@/components/ui/input';
import { Search, Filter } from 'lucide-react';
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

  return (
    <div className="flex flex-col md:flex-row gap-4">
      {/* Search Input */}
      <div className="flex-1 relative">
        <Search className={`absolute left-4 top-1/2 transform -translate-y-1/2 ${isDarkMode ? 'text-white' : 'text-gray-600'} w-5 h-5`} />
        <Input
          placeholder="Buscar noticias..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className={`pl-12 h-12 rounded-xl ${isDarkMode 
            ? 'border-gray-700 bg-gray-800/50 text-white placeholder:text-gray-500 focus:border-gray-500' 
            : 'border-gray-300 bg-white text-gray-900 placeholder:text-gray-400 focus:border-gray-500'}`}
        />
      </div>

      {/* Category Filter */}
      <div className="min-w-[200px]">
        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className={`h-12 rounded-xl ${isDarkMode 
            ? 'border-gray-700 bg-gray-800/50 text-white' 
            : 'border-gray-300 bg-white text-gray-900'}`}>
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4" />
              <SelectValue placeholder="Categoría" />
            </div>
          </SelectTrigger>
          <SelectContent className={`${isDarkMode 
            ? 'bg-gray-900 border-gray-700' 
            : 'bg-white border-gray-200'} rounded-xl z-50`}>
            {categories.map((category) => (
              <SelectItem 
                key={category.value} 
                value={category.value}
                className={`${isDarkMode 
                  ? 'text-white hover:bg-gray-800 focus:bg-gray-800 data-[highlighted]:bg-gray-800' 
                  : 'text-slate-800 hover:bg-slate-100 focus:bg-slate-100 data-[highlighted]:bg-slate-100'}`}
              >
                {category.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};
