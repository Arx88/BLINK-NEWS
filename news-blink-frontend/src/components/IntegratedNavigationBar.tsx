
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { TrendingUp, MessageCircle, Clock, Search, Filter, X } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface IntegratedNavigationBarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  selectedCategory: string;
  setSelectedCategory: (category: string) => void;
  categories: Array<{ value: string; label: string }>;
}

export const IntegratedNavigationBar = ({
  activeTab,
  setActiveTab,
  searchTerm,
  setSearchTerm,
  selectedCategory,
  setSelectedCategory,
  categories
}: IntegratedNavigationBarProps) => {
  const { isDarkMode } = useTheme();

  const clearSearch = () => setSearchTerm('');
  const clearCategory = () => setSelectedCategory('all');

  return (
    <div className={`w-full p-6 rounded-3xl backdrop-blur-md ${isDarkMode 
      ? 'bg-gray-800 shadow-2xl shadow-black/50' 
      : 'bg-white shadow-2xl shadow-gray-900/10'}`}>
      
      {/* Tab Navigation */}
      <div className="mb-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList 
            className={`grid w-full grid-cols-3 h-16 p-1 rounded-2xl backdrop-blur-sm ${isDarkMode 
              ? 'bg-gray-700' 
              : 'bg-white'}`}
          >
            
            <TabsTrigger
              value="ultimas"
              className={`flex items-center justify-center space-x-3 rounded-xl h-12 transition-all duration-300 ${isDarkMode
                ? 'data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-600/25 text-gray-400 hover:text-gray-200 hover:bg-gray-600'
                : 'data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-600/25 text-gray-600 hover:text-gray-800 hover:bg-gray-200'} font-bold`}
            >
              <Clock className="w-5 h-5" />
              <span className="hidden sm:inline">ÚLTIMAS</span>
              <span className="sm:hidden">LAST</span>
            </TabsTrigger>

            <TabsTrigger 
              value="tendencias" 
              className={`flex items-center justify-center space-x-3 rounded-xl h-12 transition-all duration-300 ${isDarkMode 
                ? 'data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-600/25 text-gray-400 hover:text-gray-200 hover:bg-gray-600' 
                : 'data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-600/25 text-gray-600 hover:text-gray-800 hover:bg-gray-200'} font-bold`}
            >
              <TrendingUp className="w-5 h-5" />
              <span className="hidden sm:inline">TENDENCIAS</span>
              <span className="sm:hidden">TREND</span>
            </TabsTrigger>
            
            <TabsTrigger 
              value="rumores" 
              className={`flex items-center justify-center space-x-3 rounded-xl h-12 transition-all duration-300 ${isDarkMode 
                ? 'data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-600/25 text-gray-400 hover:text-gray-200 hover:bg-gray-600' 
                : 'data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-600/25 text-gray-600 hover:text-gray-800 hover:bg-gray-200'} font-bold`}
            >
              <MessageCircle className="w-5 h-5" />
              <span className="hidden sm:inline">RUMORES</span>
              <span className="sm:hidden">RUMOR</span>
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Search and Filters Section */}
      <div className="flex flex-col lg:flex-row gap-4">
        {/* Search Input */}
        <div className="flex-1 relative group">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-blue-600 w-5 h-5 transition-colors group-focus-within:text-blue-600" />
          <Input
            placeholder="Buscar noticias tecnológicas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`pl-12 pr-10 h-14 rounded-xl text-base font-medium transition-all duration-300 focus:ring-2 focus:ring-offset-2 ${isDarkMode 
              ? 'bg-gray-700 text-white placeholder:text-gray-400 border border-gray-600 hover:border-gray-500 focus:border-blue-500 focus:ring-blue-500/20' 
              : 'bg-white text-gray-900 placeholder:text-gray-500 border border-gray-200 hover:border-gray-300 focus:border-blue-500 focus:ring-blue-500/20'} backdrop-blur-sm`}
          />
          {searchTerm && (
            <button
              onClick={clearSearch}
              className={`absolute right-4 top-1/2 transform -translate-y-1/2 ${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-400 hover:text-gray-700'} transition-colors`}
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Category Filter */}
        <div className="min-w-[240px] relative">
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className={`h-14 rounded-xl text-base font-medium transition-all duration-300 focus:ring-2 focus:ring-offset-2 ${isDarkMode 
              ? 'bg-gray-700 text-white border border-gray-600 hover:border-gray-500 focus:border-blue-500 focus:ring-blue-500/20' 
              : 'bg-white text-gray-900 border border-gray-200 hover:border-gray-300 focus:border-blue-500 focus:ring-blue-500/20'} backdrop-blur-sm`}>
              <div className="flex items-center space-x-3">
                <Filter className="w-5 h-5 text-blue-600" />
                <SelectValue placeholder="Seleccionar categoría" />
              </div>
            </SelectTrigger>
            <SelectContent className={`${isDarkMode 
              ? 'bg-gray-800 backdrop-blur-md border-gray-600' 
              : 'bg-white backdrop-blur-md border-gray-200'} rounded-xl z-50 shadow-xl border`}>
              {categories.map((category) => (
                <SelectItem 
                  key={category.value} 
                  value={category.value}
                  className={`text-base py-3 pl-8 pr-4 rounded-lg transition-all duration-200 ${isDarkMode
                    ? 'text-white hover:bg-gray-700 focus:bg-gray-700 data-[highlighted]:bg-gray-700' 
                    : 'text-gray-800 hover:bg-gray-100 focus:bg-gray-100 data-[highlighted]:bg-gray-100'}`}
                >
                  {category.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {selectedCategory !== 'all' && (
            <button
              onClick={clearCategory}
              className={`absolute right-12 top-1/2 transform -translate-y-1/2 ${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-400 hover:text-gray-700'} transition-colors`}
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Active Filters Display */}
      {(searchTerm || selectedCategory !== 'all') && (
        <div className="flex flex-wrap gap-2 mt-6 pt-4">
          {searchTerm && (
            <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium backdrop-blur-sm ${isDarkMode 
              ? 'bg-blue-600/20 text-blue-300' 
              : 'bg-blue-100 text-blue-700'}`}>
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
            <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium backdrop-blur-sm ${isDarkMode 
              ? 'bg-blue-600/20 text-blue-300' 
              : 'bg-blue-100 text-blue-700'}`}>
              <Filter className="w-3 h-3" />
              <span>{categories.find(c => c.value === selectedCategory)?.label}</span>
              <button 
                onClick={clearCategory}
                className={`${isDarkMode ? 'text-blue-400 hover:text-blue-200' : 'text-blue-600 hover:text-blue-800'} ml-1`}
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
