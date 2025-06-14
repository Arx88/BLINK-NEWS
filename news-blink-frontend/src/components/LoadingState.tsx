
import { useTheme } from '@/contexts/ThemeContext';

export const LoadingState = () => {
  const { isDarkMode } = useTheme();

  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className={`w-12 h-12 border-4 ${isDarkMode ? 'border-gray-700 border-t-white' : 'border-gray-300 border-t-gray-600'} rounded-full animate-spin mb-4`}></div>
      <p className={`${isDarkMode ? 'text-white' : 'text-gray-600'} font-bold`}>Cargando noticias...</p>
    </div>
  );
};
