
import { Badge } from '@/components/ui/badge';
import { RealPowerBarVoteSystem } from './RealPowerBarVoteSystem'; // Changed import
import { useState, useEffect, useCallback, memo } from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { Eye, MessageCircle } from 'lucide-react';

interface RumorHeroCardProps {
  news: any;
  onCardClick: (id: string) => void;
}

export const RumorHeroCard = memo(({ news, onCardClick }: RumorHeroCardProps) => {
  const { isDarkMode } = useTheme();
  const [currentBullet, setCurrentBullet] = useState(0);

  const handleCardClick = useCallback(() => {
    onCardClick(news.id);
  }, [news.id, onCardClick]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (news?.points && news.points.length > 0) {
      interval = setInterval(() => {
        setCurrentBullet((prev) => (prev + 1) % news.points.length);
      }, 3000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [news?.points]);

  if (!news) return null;

  const getConfidenceLevel = (aiScore: number) => {
    if (aiScore >= 70) return { label: 'Alta Confiabilidad', color: 'bg-green-500', textColor: 'text-green-600' };
    if (aiScore >= 50) return { label: 'Confiabilidad Media', color: 'bg-yellow-500', textColor: 'text-yellow-600' };
    return { label: 'Baja Confiabilidad', color: 'bg-red-500', textColor: 'text-red-600' };
  };

  const confidence = getConfidenceLevel(news.aiScore);

  return (
    <div 
      onClick={handleCardClick}
      className="cursor-pointer"
    >
      <div className={`relative ${isDarkMode 
        ? 'bg-slate-900/90' 
        : 'bg-white'} rounded-xl overflow-hidden transition-all duration-300`}>
        
        {/* Rumor indicator */}
        <div className="bg-gradient-to-r from-orange-500 to-red-500 h-1"></div>
        
        <div className="relative grid lg:grid-cols-2 gap-0 min-h-[450px]">
          <div className="relative overflow-hidden lg:order-2">
            <img
              src={news.image}
              alt={news.title}
              className="w-full h-full object-cover"
              loading="eager"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent" />
            
            <div className="absolute top-4 right-4 flex flex-col items-end space-y-2">
              <Badge className="bg-orange-500/90 text-white px-3 py-1 text-sm font-medium rounded-lg backdrop-blur-sm flex items-center space-x-1">
                <MessageCircle className="w-4 h-4" />
                <span>RUMOR</span>
              </Badge>
              <Badge className={`${isDarkMode 
                ? 'bg-slate-800/90 text-slate-200' 
                : 'bg-white/90 text-slate-700'} px-3 py-1 text-sm font-medium rounded-lg backdrop-blur-sm`}>
                {news.readTime}
              </Badge>
            </div>
          </div>

          <div className="p-8 flex flex-col justify-center lg:order-1">
            <div className="space-y-6">
              <div>
                <h1 className={`text-3xl lg:text-4xl font-bold leading-tight mb-4 ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>
                  {news.title}
                </h1>
                
                <div className="mb-4">
                  <Badge className={`${isDarkMode 
                    ? 'bg-slate-800 text-orange-400' 
                    : 'bg-slate-100 text-orange-600'} px-3 py-1 text-sm font-medium rounded-lg`}>
                    {news.category}
                  </Badge>
                </div>
              </div>

              {/* Confidence meter */}
              <div className={`${isDarkMode ? 'bg-slate-800/50' : 'bg-slate-50'} rounded-xl p-4`}>
                <div className="flex items-center justify-between mb-3">
                  <span className={`text-sm font-medium ${isDarkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                    Nivel de Confiabilidad
                  </span>
                  <span className={`text-sm font-bold ${confidence.textColor}`}>
                    {news.aiScore}%
                  </span>
                </div>
                <div className={`w-full h-3 ${isDarkMode ? 'bg-slate-700' : 'bg-slate-200'} rounded-full overflow-hidden`}>
                  <div 
                    className={`h-full ${confidence.color} transition-all duration-700 rounded-full`}
                    style={{ width: `${news.aiScore}%` }}
                  />
                </div>
                <p className={`text-xs mt-2 ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                  {confidence.label}
                </p>
              </div>

              {/* Rumor points with simple animation */}
              <div className="space-y-3">
                {news.points.map((point: string, index: number) => {
                  const isActive = currentBullet === index;
                  
                  return (
                    <div key={index} className="flex items-start space-x-3">
                      <div
                        className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300 ${
                          isActive
                            ? 'bg-orange-500 text-white'
                            : isDarkMode 
                              ? 'bg-slate-800 text-orange-400'
                              : 'bg-slate-100 text-orange-600'
                        }`}
                      >
                        <span className="text-xs font-medium">?</span>
                      </div>
                      <p 
                        className={`${isDarkMode ? 'text-slate-300' : 'text-slate-600'} text-sm leading-relaxed italic transition-all duration-300 flex-1 ${
                          isActive ? (isDarkMode ? 'text-white font-medium' : 'text-slate-900 font-medium') : ''
                        }`}
                      >
                        "{point}"
                      </p>
                    </div>
                  );
                })}
              </div>

              {/* Warning disclaimer */}
              <div className={`${isDarkMode ? 'bg-amber-500/10' : 'bg-amber-50'} rounded-xl p-4`}>
                <div className="flex items-start space-x-3">
                  <Eye className={`w-5 h-5 ${isDarkMode ? 'text-amber-400' : 'text-amber-600'} mt-0.5 flex-shrink-0`} />
                  <div>
                    <p className={`text-sm font-medium ${isDarkMode ? 'text-amber-400' : 'text-amber-700'} mb-1`}>
                      Información no verificada
                    </p>
                    <p className={`text-sm ${isDarkMode ? 'text-amber-300/80' : 'text-amber-600'}`}>
                      Este rumor circula en internet pero no ha sido confirmado oficialmente.
                    </p>
                  </div>
                </div>
              </div>

              {/* Vote system */}
              <div onClick={(e) => e.stopPropagation()}>
                <RealPowerBarVoteSystem // Changed component
                  articleId={news.id}
                  initialLikes={news.votes?.likes || 0}
                  initialDislikes={news.votes?.dislikes || 0}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

RumorHeroCard.displayName = 'RumorHeroCard';
