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
      ? 'bg-gray-900' 
      : 'bg-white backdrop-blur-md shadow-sm'} sticky top-0 z-50`}>
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo Section */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-sm">
              <span className="text-lg font-black text-white">✦</span>
            </div>
            <h1 className={`text-2xl font-black ${isDarkMode 
              ? 'text-white' 
              : 'text-gray-900'}`}>
              BLINK
            </h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              to="/" 
              className={`${isDarkMode ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'} font-medium transition-all duration-300 relative group`}
            >
              Inicio
              <span className={`absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 group-hover:w-full transition-all duration-300`}></span>
            </Link>
            <Link 
              to="/tendencias" 
              className={`${isDarkMode ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'} font-medium transition-all duration-300 flex items-center space-x-2 relative group`}
            >
              <TrendingUp className="w-4 h-4" />
              <span>Tendencias</span>
              <span className={`absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 group-hover:w-full transition-all duration-300`}></span>
            </Link>
            <Link 
              to="/rumores" 
              className={`${isDarkMode ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'} font-medium transition-all duration-300 flex items-center space-x-2 relative group`}
            >
              <MessageCircle className="w-4 h-4" />
              <span>Rumores</span>
              <span className={`absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 group-hover:w-full transition-all duration-300`}></span>
            </Link>
            <Link 
              to="/deep-topic-search"
              className={`${isDarkMode ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'} font-medium transition-all duration-300 flex items-center space-x-2 relative group`}
            >
              <Search className="w-4 h-4" />
              <span>Búsqueda</span>
              <span className={`absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 group-hover:w-full transition-all duration-300`}></span>
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
              />
              <Moon className={`w-4 h-4 ${isDarkMode ? 'text-blue-400' : 'text-gray-500'}`} />
            </div>

            <Button
              onClick={onRefresh}
              variant="outline"
              className={`hidden sm:flex items-center space-x-2 ${isDarkMode 
                ? 'bg-gray-800 text-white hover:bg-gray-700 border-gray-600' 
                : 'bg-white text-gray-600 hover:bg-gray-100 border-gray-300'} transition-all duration-300 focus:ring-0 focus:ring-offset-0 focus-visible:ring-0 focus-visible:ring-offset-0`}
            >
              <RefreshCw className="w-4 h-4" />
              <span>Actualizar</span>
            </Button>

            {/* Mobile Menu */}
            <div className="md:hidden">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon" className={`${isDarkMode 
                    ? 'bg-gray-800 text-white hover:bg-gray-700 border-gray-600' 
                    : 'bg-white text-gray-600 hover:bg-gray-100 border-gray-300'} focus:ring-0 focus:ring-offset-0 focus-visible:ring-0 focus-visible:ring-offset-0`}>
                    <Menu className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className={`w-56 ${isDarkMode 
                  ? 'bg-gray-800' 
                  : 'bg-white'} backdrop-blur-sm`} align="end">
                  <DropdownMenuItem asChild>
                    <Link to="/" className={`flex items-center space-x-2 ${isDarkMode 
                      ? 'text-gray-300 hover:text-white focus:text-white' 
                      : 'text-gray-700 hover:text-gray-900 focus:text-gray-900'}`}>
                      <span>Inicio</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/tendencias" className={`flex items-center space-x-2 ${isDarkMode 
                      ? 'text-gray-300 hover:text-white focus:text-white' 
                      : 'text-gray-700 hover:text-gray-900 focus:text-gray-900'}`}>
                      <TrendingUp className="w-4 h-4" />
                      <span>Tendencias</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/rumores" className={`flex items-center space-x-2 ${isDarkMode 
                      ? 'text-gray-300 hover:text-white focus:text-white' 
                      : 'text-gray-700 hover:text-gray-900 focus:text-gray-900'}`}>
                      <MessageCircle className="w-4 h-4" />
                      <span>Rumores</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/deep-topic-search" className={`flex items-center space-x-2 ${isDarkMode
                      ? 'text-gray-300 hover:text-white focus:text-white' 
                      : 'text-gray-700 hover:text-gray-900 focus:text-gray-900'}`}>
                      <Search className="w-4 h-4" />
                      <span>Búsqueda</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={onRefresh} className={`flex items-center space-x-2 ${isDarkMode 
                    ? 'text-gray-300 hover:text-white focus:text-white' 
                    : 'text-gray-700 hover:text-gray-900 focus:text-gray-900'}`}>
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
