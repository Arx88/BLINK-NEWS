import * as React from 'react';
import { useState } from 'react';
import { Filter } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"; // Assuming this path is correct relative to src

// Mimic the categories data structure
const categoriesData = [
  { value: 'all', label: 'All Categories' },
  { value: 'technology', label: 'Technology' },
  { value: 'science', label: 'Science' },
  { value: 'ai', label: 'Artificial Intelligence' },
  { value: 'programming', label: 'Programming' },
  { value: 'design', label: 'Design' },
];

// Mimic the ThemeContext for isDarkMode, default to false for simplicity
const useMinimalTheme = () => ({ isDarkMode: false });

export const MinimalSelectTest = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const { isDarkMode } = useMinimalTheme(); // Simplified theme context

  return (
    <div className="p-10 bg-gray-100 min-h-screen flex items-start justify-center">
      <div className="w-full max-w-xs"> {/* Added a container to constrain width for better visual testing */}
        <h2 className="mb-4 text-lg font-semibold">Minimal Select Test</h2>
        <div className="min-w-[240px] relative"> {/* This div is from IntegratedNavigationBar */}
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
              {categoriesData.map((category) => (
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
        </div>
      </div>
    </div>
  );
};

export default MinimalSelectTest;
