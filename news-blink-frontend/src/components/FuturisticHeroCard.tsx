
import { Badge } from '@/components/ui/badge';
import { PowerBarVoteSystem } from './PowerBarVoteSystem';
import { useState, useEffect, useCallback, memo } from 'react';
import { useTheme } from '@/contexts/ThemeContext';

interface FuturisticHeroCardProps {
  news: any;
  onCardClick: (id: string) => void;
}

export const FuturisticHeroCard = memo(({ news, onCardClick }: FuturisticHeroCardProps) => {
  const { isDarkMode } = useTheme();
  const [currentBullet, setCurrentBullet] = useState(0);
  const [isHovered, setIsHovered] = useState(false);

  const handleCardClick = useCallback(() => {
    onCardClick(news.id);
  }, [news.id, onCardClick]);

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isHovered && news?.points && news.points.length > 0) {
      setCurrentBullet(0);
      
      // Increased interval to 4 seconds for better performance
      interval = setInterval(() => {
        setCurrentBullet((prev) => (prev + 1) % news.points.length);
      }, 4000);
    } else {
      setCurrentBullet(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isHovered, news?.points]);

  if (!news) return null;

  return (
    <div 
      onClick={handleCardClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className="cursor-pointer"
    >
      <div className={`relative ${isDarkMode 
        ? 'bg-gradient-to-br from-black via-gray-950 to-black border-gray-800/50' 
        : 'bg-white border-slate-200 shadow-lg'} rounded-2xl overflow-hidden border hover:shadow-2xl transition-all duration-300`}>
        <div className={`absolute top-0 left-0 w-full h-1 ${isDarkMode 
          ? 'bg-gradient-to-r from-white to-gray-300' 
          : 'bg-gradient-to-r from-slate-600 to-slate-400'}`} />
        
        <div className="relative grid lg:grid-cols-2 gap-0 min-h-[400px]">
          <div className="relative overflow-hidden lg:order-2">
            <img
              src={news.image}
              alt={news.title}
              className="w-full h-full object-cover"
              loading="eager"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
            
            <div className="absolute top-4 right-4 flex flex-col items-end space-y-2">
              {news.isHot && (
                <Badge className="bg-red-500 text-white px-3 py-1 text-xs font-bold rounded-lg">
                  🔥 HOT
                </Badge>
              )}
              <Badge className={`${isDarkMode 
                ? 'bg-black/80 text-white border-gray-600/30' 
                : 'bg-white/95 text-slate-700 border-slate-200/50 shadow-sm'} px-3 py-1 text-xs font-bold rounded-lg border backdrop-blur-sm`}>
                {news.readTime}
              </Badge>
            </div>
          </div>

          <div className="p-6 flex flex-col justify-center lg:order-1">
            <div className="mb-4">
              <div className="text-center mb-4 relative">
                <h1 className={`text-3xl lg:text-4xl font-black leading-tight tracking-tighter mb-3 transform hover:scale-105 transition-all duration-500 relative z-10 ${isDarkMode ? 'text-white' : 'text-slate-800'}`}>
                  {news.title}
                </h1>
                <div className={`w-16 h-1 mx-auto rounded-full ${isDarkMode ? 'bg-gradient-to-r from-white to-gray-300' : 'bg-gradient-to-r from-slate-600 to-slate-400'} shadow-sm`}></div>
              </div>
              
              <div className="text-center">
                <Badge className={`${isDarkMode 
                  ? 'bg-gradient-to-r from-gray-900 to-black text-white border-gray-600/30' 
                  : 'bg-slate-100 text-slate-700 border-slate-200'} px-3 py-1 text-xs font-bold rounded-lg border`}>
                  {news.category}
                </Badge>
              </div>
            </div>

            {/* Bullets with improved animation */}
            <div className="space-y-2 mb-8 flex-1 relative">
              {news.points.map((point: string, index: number) => {
                const isActive = isHovered && currentBullet === index;
                
                return (
                  <div key={index} className="relative">
                    {/* Background highlight */}
                    <div
                      className={`absolute inset-0 -mx-6 transition-all duration-500 ease-out ${
                        isActive
                          ? isDarkMode
                            ? 'bg-white/20 border-l-4 border-white/50'
                            : 'bg-slate-200 border-l-4 border-slate-500'
                          : 'bg-transparent'
                      }`}
                      style={{
                        opacity: isActive ? 1 : 0,
                        top: '-3px',
                        bottom: '-3px',
                      }}
                    />
                    
                    <div className="flex items-center space-x-3 relative z-10 py-2">
                      <div
                        className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 border-2 shadow-sm transition-all duration-500 ease-out ${
                          isActive
                            ? isDarkMode
                              ? 'bg-white border-gray-300 text-black shadow-white/50'
                              : 'bg-slate-700 border-slate-500 shadow-slate-500/20 text-white'
                            : isDarkMode 
                              ? 'bg-gray-800 border-gray-700/50 shadow-gray-600/20 text-white'
                              : 'bg-slate-600 border-slate-500 shadow-slate-600/10 text-white'
                        }`}
                        style={{
                          transform: isActive ? 'scale(1.1)' : 'scale(1)',
                        }}
                      >
                        <span className="text-xs font-black">
                          ✦
                        </span>
                      </div>
                      <p 
                        className={`${isDarkMode ? 'text-gray-300' : 'text-slate-600'} text-sm leading-relaxed font-medium transition-all duration-500 ease-out flex-1 ${
                          isActive ? (isDarkMode ? 'text-white font-semibold' : 'text-slate-800 font-semibold') : ''
                        }`}
                      >
                        {point}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Vote system - better integrated */}
            <div onClick={(e) => e.stopPropagation()}>
              <PowerBarVoteSystem
                articleId={news.id}
                initialLikes={news.votes?.likes || 0}
                initialDislikes={news.votes?.dislikes || 0}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

FuturisticHeroCard.displayName = 'FuturisticHeroCard';
