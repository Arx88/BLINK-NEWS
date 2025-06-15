
import { useState, useEffect } from 'react';
import { Eye } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

export const AnimatedEye = () => {
  const { isDarkMode } = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setIsOpen(prev => !prev);
    }, 2000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex items-center justify-center">
      <div className={`transition-all duration-500 transform ${isOpen ? 'scale-100 opacity-100' : 'scale-75 opacity-60'}`}>
        <Eye 
          size={80} 
          className={`${isDarkMode ? 'text-blue-500' : 'text-blue-700'} transition-all duration-500`}
          strokeWidth={2}
        />
      </div>
    </div>
  );
};
