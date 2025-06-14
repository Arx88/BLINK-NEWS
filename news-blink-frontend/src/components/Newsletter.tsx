
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Bell } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

export const Newsletter = () => {
  const { isDarkMode } = useTheme();

  return (
    <div className="mt-16">
      <div className={`${isDarkMode 
        ? 'bg-gradient-to-r from-gray-900 via-black to-gray-900 border-gray-500/30' 
        : 'bg-gradient-to-r from-gray-50 to-gray-100 border-gray-200'} rounded-2xl p-8 border text-center`}>
        <div className={`w-16 h-16 ${isDarkMode 
          ? 'bg-gradient-to-r from-white to-gray-300' 
          : 'bg-gradient-to-r from-gray-700 to-gray-800'} rounded-2xl flex items-center justify-center mx-auto mb-6`}>
          <Bell className={`w-8 h-8 ${isDarkMode ? 'text-black' : 'text-white'}`} />
        </div>
        <h3 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'} mb-4`}>
          Suscríbete a las noticias
        </h3>
        <p className={`${isDarkMode ? 'text-gray-400' : 'text-gray-600'} mb-6`}>
          Recibe las últimas tendencias y rumores directamente
        </p>
        <div className="flex max-w-md mx-auto gap-3">
          <Input
            type="email"
            placeholder="tu@email.com"
            className={`flex-1 h-12 rounded-xl ${isDarkMode 
              ? 'border-gray-700 bg-gray-800/50 text-white placeholder:text-gray-500' 
              : 'border-gray-300 bg-white text-gray-900 placeholder:text-gray-400'}`}
          />
          <Button className={`h-12 px-6 ${isDarkMode 
            ? 'bg-gradient-to-r from-white to-gray-300 text-black hover:from-gray-200 hover:to-gray-400' 
            : 'bg-gradient-to-r from-gray-700 to-gray-800 text-white hover:from-gray-600 hover:to-gray-700'} font-bold rounded-xl`}>
            SUSCRIBIR
          </Button>
        </div>
      </div>
    </div>
  );
};
