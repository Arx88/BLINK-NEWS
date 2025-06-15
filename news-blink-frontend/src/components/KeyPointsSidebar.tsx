
import React, { useState, useEffect, useRef } from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { RealPowerBarVoteSystem } from '@/components/RealPowerBarVoteSystem';
import { ComplementaryInfoCard } from '@/components/ComplementaryInfoCard';
import { Target, TrendingUp, Lightbulb, AlertCircle } from 'lucide-react';
import { NewsItem } from '@/utils/api';

interface KeyPointsSidebarProps {
  article: NewsItem;
}

export function KeyPointsSidebar({ article }: KeyPointsSidebarProps) {
  const { isDarkMode } = useTheme();
  const [currentBullet, setCurrentBullet] = useState(0);
  const [lineHeight, setLineHeight] = useState(0);
  const pointsRef = useRef<(HTMLDivElement | null)[]>([]);

  // Animated bullet indicator
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (article?.points && article.points.length > 1) {
      interval = setInterval(() => {
        setCurrentBullet((prev) => (prev + 1) % article.points.length);
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [article?.points]);

  // Calculate line height based on actual bullet positions
  useEffect(() => {
    if (article.points.length > 1 && pointsRef.current.length > 0) {
      const firstBullet = pointsRef.current[0];
      const lastBullet = pointsRef.current[article.points.length - 1];
      
      if (firstBullet && lastBullet) {
        const firstBulletRect = firstBullet.getBoundingClientRect();
        const lastBulletRect = lastBullet.getBoundingClientRect();
        const calculatedHeight = lastBulletRect.top - firstBulletRect.top;
        setLineHeight(calculatedHeight);
      }
    }
  }, [article.points]);

  // Generate complementary info cards
  const generateComplementaryInfo = (points: string[]) => {
    const infoTypes = [
      { 
        title: "Contexto Clave", 
        icon: Target, 
        content: "Este desarrollo marca un hito importante en la industria tecnológica, con implicaciones que se extienderán durante los próximos años y afectarán múltiples sectores."
      },
      { 
        title: "Impacto del Mercado", 
        icon: TrendingUp, 
        content: "Las inversiones en este sector han crecido exponencialmente, con más de $10 mil millones destinados a investigación y desarrollo en el último trimestre."
      },
      { 
        title: "Perspectiva Futura", 
        icon: Lightbulb, 
        content: "Los expertos predicen que esta tecnología será fundamental para la próxima generación de aplicaciones empresariales y consumidores."
      },
      { 
        title: "Factores Críticos", 
        icon: AlertCircle, 
        content: "Es importante considerar los desafíos regulatorios y de adopción que podrían influir en el ritmo de implementación a gran escala."
      }
    ];

    return points.slice(0, 4).map((point, index) => {
      const info = infoTypes[index] || infoTypes[0];
      
      return (
        <ComplementaryInfoCard
          key={index}
          point={point}
          info={info}
          index={index}
        />
      );
    });
  };

  return (
    <div className={`${isDarkMode ? 'bg-gray-900' : 'bg-white'} rounded-2xl p-6 sticky top-8 space-y-6`}>
      <div>
        <h2 className={`text-xl font-bold mb-6 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          Puntos Clave
        </h2>
        
        <div className="space-y-4 relative">
          {/* Línea vertical que se calcula dinámicamente */}
          {article.points.length > 1 && lineHeight > 0 && (
            <div 
              className={`absolute left-[18px] top-[18px] w-0.5 ${isDarkMode ? 'bg-gray-700' : 'bg-gray-300'}`} 
              style={{ height: `${lineHeight}px` }} 
            />
          )}
          
          {article.points.map((point, index) => (
            <div 
              key={index} 
              ref={(el) => (pointsRef.current[index] = el)}
              className="flex items-start space-x-4 relative z-20"
            >
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-all duration-300 ${
                currentBullet === index
                  ? (isDarkMode ? 'bg-blue-500 text-white scale-110 shadow-lg shadow-blue-500/50' : 'bg-blue-600 text-white scale-110 shadow-lg shadow-blue-600/50')
                  : (isDarkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-200 text-gray-600')
              }`}>
                <span className="text-sm font-bold">{index + 1}</span>
              </div>
              <p className={`text-sm leading-relaxed transition-all duration-300 ${
                currentBullet === index
                  ? (isDarkMode ? 'text-white font-medium' : 'text-gray-900 font-medium')
                  : (isDarkMode ? 'text-gray-400' : 'text-gray-600')
              }`}>
                {point}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="pt-6 border-t border-gray-200 dark:border-gray-800">
        <RealPowerBarVoteSystem
          articleId={article.id}
          initialLikes={article.votes?.likes || 0}
          initialDislikes={article.votes?.dislikes || 0}
        />
      </div>

      <div className="space-y-4">
        {generateComplementaryInfo(article.points)}
      </div>
    </div>
  );
}
