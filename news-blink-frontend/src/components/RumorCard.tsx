
import { Badge } from '@/components/ui/badge';
import { RealPowerBarVoteSystem } from './RealPowerBarVoteSystem'; // Changed import
import { useState, useCallback, memo } from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { Eye, MessageCircle } from 'lucide-react';

interface RumorCardProps {
  news: any;
  onCardClick: (id: string) => void;
}

export const RumorCard = memo(({ news, onCardClick }: RumorCardProps) => {
  const { isDarkMode } = useTheme();

  const handleCardClick = useCallback(() => {
    onCardClick(news.id);
  }, [news.id, onCardClick]);

  const getConfidenceLevel = (aiScore: number) => {
    if (aiScore >= 70) return { label: 'Alta Confiabilidad', color: 'bg-green-500', textColor: 'text-green-600' };
    if (aiScore >= 50) return { label: 'Confiabilidad Media', color: 'bg-yellow-500', textColor: 'text-yellow-600' };
    return { label: 'Baja Confiabilidad', color: 'bg-red-500', textColor: 'text-red-600' };
  };

  const confidence = getConfidenceLevel(news.aiScore);

  return (
    <div 
      onClick={handleCardClick}
      className="cursor-pointer h-full flex flex-col" // Changed
    >
      <div className={`relative h-full flex flex-col ${isDarkMode 
        ? 'bg-slate-900/80' 
        : 'bg-white'} rounded-xl overflow-hidden transition-all duration-300`}>
        
        {/* Rumor indicator */}
        <div className="bg-gradient-to-r from-orange-500 to-red-500 h-1"></div>
        
        {/* Image section */}
        <div className="relative overflow-hidden h-48 flex-shrink-0">
          <img
            src={news.image}
            alt={news.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent" />
          
          {/* Badges */}
          <div className="absolute top-3 left-3">
            <Badge className="bg-orange-500/90 text-white px-2 py-1 text-xs font-medium rounded-md backdrop-blur-sm flex items-center space-x-1">
              <MessageCircle className="w-3 h-3" />
              <span>RUMOR</span>
            </Badge>
          </div>
          
          <div className="absolute top-3 right-3 flex flex-col items-end space-y-2">
            <Badge className={`${isDarkMode 
              ? 'bg-slate-800/90 text-slate-200' 
              : 'bg-white/90 text-slate-700'} backdrop-blur-sm px-2 py-1 text-xs font-medium rounded-md`}>
              {news.readTime}
            </Badge>
          </div>
          
          <div className="absolute bottom-3 left-3">
            <Badge className={`${isDarkMode 
              ? 'bg-slate-800/80 text-orange-400' 
              : 'bg-white/80 text-orange-600'} text-xs font-medium px-2 py-1 rounded-md backdrop-blur-sm`}>
              {news.category}
            </Badge>
          </div>
        </div>
        
        {/* Content section */}
        <div className="p-5 flex-1 flex flex-col space-y-4 overflow-hidden"> {/* Added overflow-hidden */}
          <div>
            <h3 className={`text-lg font-bold ${isDarkMode ? 'text-white' : 'text-slate-900'} leading-tight mb-2`}>
              {news.title}
            </h3>
          </div>
          
          {/* Confidence indicator */}
          <div className={`${isDarkMode ? 'bg-slate-800/50' : 'bg-slate-50'} rounded-lg p-3`}>
            <div className="flex items-center justify-between mb-2">
              <span className={`text-xs font-medium ${isDarkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                Confiabilidad
              </span>
              <span className={`text-xs font-bold ${confidence.textColor}`}>
                {news.aiScore}%
              </span>
            </div>
            <div className={`w-full h-2 ${isDarkMode ? 'bg-slate-700' : 'bg-slate-200'} rounded-full overflow-hidden`}>
              <div 
                className={`h-full ${confidence.color} transition-all duration-300 rounded-full`}
                style={{ width: `${news.aiScore}%` }}
              />
            </div>
          </div>
          
          {/* Rumor points */}
          <div className="flex-1 space-y-2 overflow-y-auto"> {/* Added overflow-y-auto */}
            {news.points.slice(0, 3).map((point: string, index: number) => (
              <div key={index} className="flex items-start space-x-2">
                <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${isDarkMode 
                  ? 'bg-slate-800 text-orange-400' 
                  : 'bg-slate-100 text-orange-600'} mt-0.5`}>
                  <span className="text-xs">?</span>
                </div>
                <p className={`${isDarkMode ? 'text-slate-300' : 'text-slate-600'} text-sm leading-relaxed italic`}>
                  "{point}"
                </p>
              </div>
            ))}
          </div>
          
          {/* Warning disclaimer */}
          <div className={`${isDarkMode ? 'bg-amber-500/10' : 'bg-amber-50'} rounded-lg p-3`}>
            <div className="flex items-start space-x-2">
              <Eye className={`w-4 h-4 ${isDarkMode ? 'text-amber-400' : 'text-amber-600'} mt-0.5 flex-shrink-0`} />
              <div>
                <p className={`text-xs font-medium ${isDarkMode ? 'text-amber-400' : 'text-amber-700'}`}>
                  Información no verificada
                </p>
              </div>
            </div>
          </div>
          
          {/* Vote system */}
          <div className="flex-shrink-0" onClick={(e) => e.stopPropagation()}>
            <RealPowerBarVoteSystem // Changed component
              articleId={news.id}
              initialLikes={news.votes?.likes || 0}
              initialDislikes={news.votes?.dislikes || 0}
            />
          </div>
        </div>
      </div>
    </div>
  );
});

RumorCard.displayName = 'RumorCard';
