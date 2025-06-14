
import { Button } from '@/components/ui/button';
import { Search } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

interface EmptyStateProps {
  onClearFilters: () => void;
}

export const EmptyState = ({ onClearFilters }: EmptyStateProps) => {
  const { isDarkMode } = useTheme();

  return (
    <div className="text-center py-16">
      <Search className={`w-16 h-16 mx-auto mb-4 ${isDarkMode ? 'text-gray-700' : 'text-gray-400'}`} />
      <h3 className={`text-xl font-bold ${isDarkMode ? 'text-gray-400' : 'text-gray-600'} mb-2`}>
        Sin resultados
      </h3>
      <p className={`${isDarkMode ? 'text-gray-600' : 'text-gray-500'} mb-6`}>
        No hay noticias para mostrar con los filtros actuales
      </p>
      <Button
        onClick={onClearFilters}
        className={`${isDarkMode 
          ? 'bg-gradient-to-r from-white to-gray-300 text-black hover:from-gray-200 hover:to-gray-400' 
          : 'bg-gradient-to-r from-gray-700 to-gray-800 text-white hover:from-gray-600 hover:to-gray-700'} font-bold rounded-xl px-6 py-2`}
      >
        Limpiar filtros
      </Button>
    </div>
  );
};
