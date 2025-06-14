
import { useTheme } from '@/contexts/ThemeContext';

export const AnimatedBackground = () => {
  const { isDarkMode } = useTheme();

  return (
    <div className="fixed inset-0 -z-10">
      {/* Fondo base sólido - sin amarillo */}
      <div className={`absolute inset-0 ${isDarkMode ? 'bg-black' : 'bg-gray-50'}`} />
      
      {/* Gradientes sutiles sin amarillo */}
      <div className={`absolute inset-0 ${isDarkMode 
        ? 'bg-gradient-to-br from-gray-900 via-black to-gray-900' 
        : 'bg-gradient-to-br from-gray-50 via-white to-gray-100'}`} />
      
      {/* Efectos de movimiento sin colores amarillos */}
      <div className="absolute inset-0 opacity-30">
        <div className={`absolute top-0 -left-4 w-96 h-96 ${isDarkMode ? 'bg-blue-900' : 'bg-blue-100'} rounded-full mix-blend-multiply filter blur-xl animate-pulse`} />
        <div className={`absolute top-0 -right-4 w-96 h-96 ${isDarkMode ? 'bg-purple-900' : 'bg-purple-100'} rounded-full mix-blend-multiply filter blur-xl animate-pulse`} style={{ animationDelay: '2s' }} />
        <div className={`absolute -bottom-8 left-20 w-96 h-96 ${isDarkMode ? 'bg-cyan-900' : 'bg-cyan-100'} rounded-full mix-blend-multiply filter blur-xl animate-pulse`} style={{ animationDelay: '4s' }} />
      </div>
    </div>
  );
};
