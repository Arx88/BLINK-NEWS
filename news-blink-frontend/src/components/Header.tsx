
import { Button } from '@/components/ui/button';
import { RefreshCw, Menu, Search, TrendingUp, MessageCircle, Sun, Moon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Switch } from '@/components/ui/switch';
import { useTheme } from '@/contexts/ThemeContext';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface HeaderProps {
  onRefresh: () => void;
}

export const Header = ({ onRefresh }: HeaderProps) => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <header className={`${isDarkMode 
      ? 'bg-gradient-to-r from-black via-gray-950 to-black border-gray-800/20' 
      : 'bg-white/95 border-slate-200 backdrop-blur-md shadow-sm'} border-b sticky top-0 z-50`}>
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo Section */}
          <div className="flex items-center space-x-3">
            <div className={`w-8 h-8 ${isDarkMode 
              ? 'bg-gradient-to-br from-white via-gray-300 to-gray-400 shadow-white/25' 
              : 'bg-slate-800 shadow-slate-800/20'} rounded-lg flex items-center justify-center shadow-sm`}>
              <span className={`text-lg font-black ${isDarkMode ? 'text-black' : 'text-white'}`}>✦</span>
            </div>
            <h1 className={`text-2xl font-black ${isDarkMode 
              ? 'text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-300 to-gray-400' 
              : 'text-slate-800'}`}>
              BLINK
            </h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              to="/" 
              className={`${isDarkMode ? 'text-gray-300 hover:text-white' : 'text-slate-600 hover:text-slate-800'} font-medium transition-all duration-300 relative group`}
            >
              Inicio
              <span className={`absolute -bottom-1 left-0 w-0 h-0.5 ${isDarkMode 
                ? 'bg-gradient-to-r from-white to-gray-300' 
                : 'bg-slate-600'} group-hover:w-full transition-all duration-300`}></span>
            </Link>
            <Link 
              to="/tendencias" 
              className={`${isDarkMode ? 'text-gray-300 hover:text-white' : 'text-slate-600 hover:text-slate-800'} font-medium transition-all duration-300 flex items-center space-x-2 relative group`}
            >
              <TrendingUp className="w-4 h-4" />
              <span>Tendencias</span>
              <span className={`absolute -bottom-1 left-0 w-0 h-0.5 ${isDarkMode 
                ? 'bg-gradient-to-r from-white to-gray-300' 
                : 'bg-slate-600'} group-hover:w-full transition-all duration-300`}></span>
            </Link>
            <Link 
              to="/rumores" 
              className={`${isDarkMode ? 'text-gray-300 hover:text-white' : 'text-slate-600 hover:text-slate-800'} font-medium transition-all duration-300 flex items-center space-x-2 relative group`}
            >
              <MessageCircle className="w-4 h-4" />
              <span>Rumores</span>
              <span className={`absolute -bottom-1 left-0 w-0 h-0.5 ${isDarkMode 
                ? 'bg-gradient-to-r from-white to-gray-300' 
                : 'bg-slate-600'} group-hover:w-full transition-all duration-300`}></span>
            </Link>
            <Link 
              to="/busqueda" 
              className={`${isDarkMode ? 'text-gray-300 hover:text-white' : 'text-slate-600 hover:text-slate-800'} font-medium transition-all duration-300 flex items-center space-x-2 relative group`}
            >
              <Search className="w-4 h-4" />
              <span>Búsqueda</span>
              <span className={`absolute -bottom-1 left-0 w-0 h-0.5 ${isDarkMode 
                ? 'bg-gradient-to-r from-white to-gray-300' 
                : 'bg-slate-600'} group-hover:w-full transition-all duration-300`}></span>
            </Link>
          </nav>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            {/* Theme Toggle */}
            <div className="flex items-center space-x-2">
              <Sun className={`w-4 h-4 ${isDarkMode ? 'text-gray-500' : 'text-amber-500'}`} />
              <Switch 
                checked={isDarkMode} 
                onCheckedChange={toggleTheme}
                className={`${isDarkMode 
                  ? 'data-[state=checked]:bg-white data-[state=unchecked]:bg-gray-600' 
                  : 'data-[state=checked]:bg-slate-800 data-[state=unchecked]:bg-slate-300'}`}
              />
              <Moon className={`w-4 h-4 ${isDarkMode ? 'text-white' : 'text-slate-500'}`} />
            </div>

            <Button
              onClick={onRefresh}
              variant="outline"
              className={`hidden sm:flex items-center space-x-2 ${isDarkMode 
                ? 'bg-gray-900/50 border-gray-700/30 text-white hover:bg-gray-800/50 hover:border-gray-600' 
                : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300'} transition-all duration-300`}
            >
              <RefreshCw className="w-4 h-4" />
              <span>Actualizar</span>
            </Button>

            {/* Mobile Menu */}
            <div className="md:hidden">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon" className={`${isDarkMode 
                    ? 'bg-gray-900/50 border-gray-700/30 text-white hover:bg-gray-800/50 hover:border-gray-600' 
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300'}`}>
                    <Menu className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className={`w-56 ${isDarkMode 
                  ? 'bg-gray-950/95 border-gray-800/20' 
                  : 'bg-white/95 border-slate-200'} backdrop-blur-sm`} align="end">
                  <DropdownMenuItem asChild>
                    <Link to="/" className={`flex items-center space-x-2 ${isDarkMode 
                      ? 'text-gray-300 hover:text-white focus:text-white' 
                      : 'text-slate-700 hover:text-slate-900 focus:text-slate-900'}`}>
                      <span>Inicio</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/tendencias" className={`flex items-center space-x-2 ${isDarkMode 
                      ? 'text-gray-300 hover:text-white focus:text-white' 
                      : 'text-slate-700 hover:text-slate-900 focus:text-slate-900'}`}>
                      <TrendingUp className="w-4 h-4" />
                      <span>Tendencias</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/rumores" className={`flex items-center space-x-2 ${isDarkMode 
                      ? 'text-gray-300 hover:text-white focus:text-white' 
                      : 'text-slate-700 hover:text-slate-900 focus:text-slate-900'}`}>
                      <MessageCircle className="w-4 h-4" />
                      <span>Rumores</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/busqueda" className={`flex items-center space-x-2 ${isDarkMode 
                      ? 'text-gray-300 hover:text-white focus:text-white' 
                      : 'text-slate-700 hover:text-slate-900 focus:text-slate-900'}`}>
                      <Search className="w-4 h-4" />
                      <span>Búsqueda</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={onRefresh} className={`flex items-center space-x-2 ${isDarkMode 
                    ? 'text-gray-300 hover:text-white focus:text-white' 
                    : 'text-slate-700 hover:text-slate-900 focus:text-slate-900'}`}>
                    <RefreshCw className="w-4 h-4" />
                    <span>Actualizar</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
