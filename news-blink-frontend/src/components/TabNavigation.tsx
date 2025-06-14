
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
    <Tabs value={activeTab} onValueChange={setActiveTab}>
      <TabsList className={`grid w-full grid-cols-3 mb-6 h-14 ${isDarkMode 
        ? 'bg-gradient-to-r from-gray-900 to-black border-gray-700/50' 
        : 'bg-slate-50 border-slate-200'} rounded-xl p-2 border`}>
        <TabsTrigger 
          value="tendencias" 
          className={`flex items-center justify-center space-x-2 rounded-lg h-10 ${isDarkMode 
            ? 'data-[state=active]:bg-gradient-to-r data-[state=active]:from-white data-[state=active]:to-gray-300 data-[state=active]:text-black text-gray-400 hover:text-gray-300' 
            : 'data-[state=active]:bg-slate-800 data-[state=active]:text-white text-slate-600 hover:text-slate-800 hover:bg-slate-100'} font-bold transition-all duration-300`}
        >
          <TrendingUp className="w-4 h-4" />
          <span>TENDENCIAS</span>
        </TabsTrigger>
        <TabsTrigger 
          value="rumores" 
          className={`flex items-center justify-center space-x-2 rounded-lg h-10 ${isDarkMode 
            ? 'data-[state=active]:bg-gradient-to-r data-[state=active]:from-gray-600 data-[state=active]:to-gray-700 data-[state=active]:text-white text-gray-400 hover:text-gray-300' 
            : 'data-[state=active]:bg-slate-700 data-[state=active]:text-white text-slate-600 hover:text-slate-800 hover:bg-slate-100'} font-bold transition-all duration-300`}
        >
          <MessageCircle className="w-4 h-4" />
          <span>RUMORES</span>
        </TabsTrigger>
        <TabsTrigger 
          value="ultimas" 
          className={`flex items-center justify-center space-x-2 rounded-lg h-10 ${isDarkMode 
            ? 'data-[state=active]:bg-gradient-to-r data-[state=active]:from-gray-500 data-[state=active]:to-gray-600 data-[state=active]:text-white text-gray-400 hover:text-gray-300' 
            : 'data-[state=active]:bg-slate-600 data-[state=active]:text-white text-slate-600 hover:text-slate-800 hover:bg-slate-100'} font-bold transition-all duration-300`}
        >
          <Clock className="w-4 h-4" />
          <span>ÚLTIMA</span>
        </TabsTrigger>
      </TabsList>
    </Tabs>
  );
};
