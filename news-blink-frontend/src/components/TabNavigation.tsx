
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TrendingUp, MessageCircle, Clock } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

interface TabNavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const TabNavigation = ({ activeTab, setActiveTab }: TabNavigationProps) => {
  const { isDarkMode } = useTheme();

  return (
    <div className="w-full">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className={`grid w-full grid-cols-3 h-16 p-1 ${isDarkMode 
          ? 'bg-gray-900/80 backdrop-blur-md' 
          : 'bg-white/80 backdrop-blur-md shadow-lg'} rounded-2xl`}>
          <TabsTrigger 
            value="tendencias" 
            className={`flex items-center justify-center space-x-3 rounded-xl h-12 transition-all duration-300 ${isDarkMode 
              ? 'data-[state=active]:bg-blue-500 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-500/25 text-gray-400 hover:text-gray-200 hover:bg-gray-800/50' 
              : 'data-[state=active]:bg-blue-700 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-700/25 text-gray-600 hover:text-gray-800 hover:bg-gray-100/70'} font-bold`}
          >
            <TrendingUp className="w-5 h-5" />
            <span className="hidden sm:inline">TENDENCIAS</span>
            <span className="sm:hidden">TREND</span>
          </TabsTrigger>
          <TabsTrigger 
            value="rumores" 
            className={`flex items-center justify-center space-x-3 rounded-xl h-12 transition-all duration-300 ${isDarkMode 
              ? 'data-[state=active]:bg-blue-500 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-500/25 text-gray-400 hover:text-gray-200 hover:bg-gray-800/50' 
              : 'data-[state=active]:bg-blue-700 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-700/25 text-gray-600 hover:text-gray-800 hover:bg-gray-100/70'} font-bold`}
          >
            <MessageCircle className="w-5 h-5" />
            <span className="hidden sm:inline">RUMORES</span>
            <span className="sm:hidden">RUMOR</span>
          </TabsTrigger>
          <TabsTrigger 
            value="ultimas" 
            className={`flex items-center justify-center space-x-3 rounded-xl h-12 transition-all duration-300 ${isDarkMode 
              ? 'data-[state=active]:bg-blue-500 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-500/25 text-gray-400 hover:text-gray-200 hover:bg-gray-800/50' 
              : 'data-[state=active]:bg-blue-700 data-[state=active]:text-white data-[state=active]:shadow-lg data-[state=active]:shadow-blue-700/25 text-gray-600 hover:text-gray-800 hover:bg-gray-100/70'} font-bold`}
          >
            <Clock className="w-5 h-5" />
            <span className="hidden sm:inline">ÚLTIMAS</span>
            <span className="sm:hidden">LAST</span>
          </TabsTrigger>
        </TabsList>
      </Tabs>
    </div>
  );
};
