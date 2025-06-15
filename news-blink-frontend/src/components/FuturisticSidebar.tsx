
import { TrendingUp, Clock, Users } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

interface FuturisticSidebarProps {
  news: any[];
}

export const FuturisticSidebar = ({ news }: FuturisticSidebarProps) => {
  const { isDarkMode } = useTheme();
  const recentNews = news
    .sort((a, b) => new Date(b.timestamp || 0).getTime() - new Date(a.timestamp || 0).getTime())
    .slice(0, 5);

  const totalVotes = news.reduce((acc, item) => acc + (item.votes?.likes || 0) + (item.votes?.dislikes || 0), 0);

  return (
    <div className={`${isDarkMode 
      ? 'bg-gray-900' 
      : 'bg-white'} rounded-2xl p-6 shadow-xl sticky top-24 space-y-6`}>
      {/* Stats */}
      <div className="text-center">
        <div className={`w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4`}>
          <Users className="w-6 h-6 text-white" />
        </div>
        <h3 className={`font-black ${isDarkMode ? 'text-white' : 'text-gray-900'} text-lg mb-2`}>ESTADÍSTICAS</h3>
        <div className="space-y-3">
          <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-gray-100'} rounded-lg p-3`}>
            <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-blue-600'}`}>{news.length}</div>
            <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Noticias activas</div>
          </div>
          <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-gray-100'} rounded-lg p-3`}>
            <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-green-600'}`}>{totalVotes}</div>
            <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Votos totales</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <div className="flex items-center space-x-2 mb-4">
          <Clock className={`w-5 h-5 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
          <h4 className={`font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'} text-sm`}>ACTIVIDAD RECIENTE</h4>
        </div>
        <div className="space-y-2">
          {recentNews.slice(0, 3).map((item, index) => (
            <div key={item.id} className={`${isDarkMode 
              ? 'bg-gray-800 hover:bg-gray-700' 
              : 'bg-gray-100 hover:bg-gray-200'} rounded-lg p-3 transition-all duration-300`}>
              <div className={`text-xs ${isDarkMode ? 'text-white' : 'text-blue-600'} font-bold line-clamp-2 mb-1`}>
                {item.title}
              </div>
              <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                Hace {Math.floor(Math.random() * 24)} horas
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
