
import { useState, useEffect } from 'react';
import { ThumbsUp } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

interface SidebarNewsItemProps {
  item: any;
  index: number;
}

export const SidebarNewsItem = ({ item, index }: SidebarNewsItemProps) => {
  const { isDarkMode } = useTheme();
  const [currentBullet, setCurrentBullet] = useState(0);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isHovered && item.points && item.points.length > 1) {
      interval = setInterval(() => {
        setCurrentBullet((prev) => (prev + 1) % item.points.length);
      }, 3500);
    } else {
      setCurrentBullet(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isHovered, item.points]);

  return (
    <div 
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`p-3 rounded-xl ${isDarkMode 
        ? 'bg-gray-800/50 hover:bg-gray-800' 
        : 'bg-white hover:bg-gray-50'} transition-all duration-300 group cursor-pointer shadow-sm`}
    >
      <div className="flex items-start space-x-3">
        <div className={`w-8 h-8 ${isDarkMode 
          ? 'bg-white text-black' 
          : 'bg-blue-500 text-white'} rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0 mt-1 group-hover:scale-110 transition-transform duration-300`}>
          {index + 1}
        </div>
        <div className="flex-1 min-w-0">
          <div className="relative h-20 rounded-lg overflow-hidden mb-2 shadow-lg">
             <img src={item.image} alt={item.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
             <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
          </div>
        
          <h4 className={`font-bold text-sm ${isDarkMode 
            ? 'text-white group-hover:text-gray-300' 
            : 'text-blue-600 group-hover:text-blue-800'} line-clamp-2 mb-1.5 transition-colors`}>
            {item.title}
          </h4>

          <div className="h-10 text-xs relative overflow-hidden">
             {item.points && item.points.length > 0 && (
                <p key={currentBullet} className={`line-clamp-2 animate-fade-in absolute inset-0 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    {item.points[currentBullet]}
                </p>
             )}
          </div>
          
          <div className="flex items-center space-x-3 text-xs mt-1">
            <div className={`flex items-center space-x-1 ${isDarkMode ? 'text-green-400' : 'text-green-600'}`}>
              <ThumbsUp className="w-3 h-3" />
              <span className="font-bold">{item.votes?.likes || 0}</span>
            </div>
            <div className={`w-1 h-1 ${isDarkMode ? 'bg-gray-600' : 'bg-gray-400'} rounded-full`}></div>
            <span className={`${isDarkMode ? 'text-gray-500' : 'text-gray-500'} font-bold`}>{item.readTime}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
