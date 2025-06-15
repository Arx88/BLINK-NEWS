
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Bell } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

export const Newsletter = () => {
  const { isDarkMode } = useTheme();

  return (
    <div className="mt-16">
      <div className={`${isDarkMode 
        ? 'bg-gray-900' 
        : 'bg-gray-100'} rounded-2xl p-8 text-center`}>
        <div className={`w-16 h-16 ${isDarkMode 
          ? 'bg-blue-600' 
          : 'bg-blue-600'} rounded-2xl flex items-center justify-center mx-auto mb-6`}>
          <Bell className="w-8 h-8 text-white" />
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
            className={`flex-1 h-12 rounded-xl border-gray-300 focus:border-blue-500 focus:ring-blue-500 ${isDarkMode 
              ? 'bg-gray-800 text-white placeholder:text-gray-400 border-gray-600' 
              : 'bg-white text-gray-900 placeholder:text-gray-500 border-gray-300'}`}
          />
          <Button className={`h-12 px-6 ${isDarkMode 
            ? 'bg-blue-600 text-white hover:bg-blue-700' 
            : 'bg-blue-600 text-white hover:bg-blue-700'} font-bold rounded-xl`}>
            SUSCRIBIR
          </Button>
        </div>
      </div>
    </div>
  );
};
