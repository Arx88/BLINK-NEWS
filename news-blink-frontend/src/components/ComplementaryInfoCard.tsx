
import React from 'react';
import { LucideIcon } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

interface ComplementaryInfoCardProps {
  point: string;
  info: {
    title: string;
    icon: LucideIcon;
    content: string;
  };
  index: number;
}

export function ComplementaryInfoCard({ point, info, index }: ComplementaryInfoCardProps) {
  const { isDarkMode } = useTheme();
  const IconComponent = info.icon;

  return (
    <div className={`rounded-xl ${isDarkMode ? 'bg-gray-800/50' : 'bg-white'} border ${isDarkMode ? 'border-gray-700/50' : 'border-gray-200'} p-6 shadow-lg hover:shadow-xl transition-all duration-300`}>
      <div className="flex items-start space-x-3 mb-4">
        <div className={`p-2 rounded-lg ${isDarkMode ? 'bg-blue-500/20 text-blue-400' : 'bg-blue-100 text-blue-600'}`}>
          <IconComponent className="w-5 h-5" />
        </div>
        <h3 className={`font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          {info.title}
        </h3>
      </div>
      
      <div className={`p-3 rounded-lg ${isDarkMode ? 'bg-gray-700/30' : 'bg-gray-50'} border-l-4 ${isDarkMode ? 'border-blue-500' : 'border-blue-600'} mb-3`}>
        <p className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
          {point}
        </p>
      </div>
      
      <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
        {info.content}
      </p>
      
      <div className={`mt-4 pt-4 border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} flex items-center justify-between`}>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isDarkMode ? 'bg-green-500' : 'bg-green-600'} animate-pulse`} />
          <span className={`text-xs font-medium ${isDarkMode ? 'text-green-400' : 'text-green-600'}`}>
            Verificado
          </span>
        </div>
        <span className={`text-xs ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`}>
          {Math.floor(Math.random() * 24) + 1}h
        </span>
      </div>
    </div>
  );
}
