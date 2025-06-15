import React from 'react';
import { Github, Twitter, Mail, Globe, Users, Home } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

export const Footer = () => {
  const { isDarkMode } = useTheme();

  const addToHomepage = () => {
    try {
      // For modern browsers, we can only suggest - browsers don't allow automatic homepage setting for security
      if (window.confirm('¿Te gustaría agregar BLINK como tu página de inicio? Puedes hacerlo manualmente en la configuración de tu navegador.')) {
        // Open browser settings (this varies by browser)
        const userAgent = navigator.userAgent;
        let message = 'Para agregar BLINK como página de inicio:\n\n';
        
        if (userAgent.includes('Chrome')) {
          message += '1. Ve a Configuración de Chrome\n2. En "Al iniciar", selecciona "Abrir una página específica"\n3. Agrega: ' + window.location.origin;
        } else if (userAgent.includes('Firefox')) {
          message += '1. Ve a Configuración de Firefox\n2. En "Inicio", establece la página de inicio\n3. Agrega: ' + window.location.origin;
        } else if (userAgent.includes('Safari')) {
          message += '1. Ve a Preferencias de Safari\n2. En "General", establece la página de inicio\n3. Agrega: ' + window.location.origin;
        } else {
          message += 'Ve a la configuración de tu navegador y establece como página de inicio:\n' + window.location.origin;
        }
        
        alert(message);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Por favor, agrega manualmente ' + window.location.origin + ' como tu página de inicio en la configuración del navegador.');
    }
  };

  return (
    <footer className={`${isDarkMode ? 'bg-gray-900' : 'bg-gray-100'} mt-20`}>
      <div className="container mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-lg font-black text-white">✦</span>
              </div>
              <h3 className={`text-xl font-black ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>BLINK</h3>
            </div>
            <p className={`${isDarkMode ? 'text-gray-400' : 'text-gray-600'} text-sm leading-relaxed`}>
              Información instantánea del mundo. Todo lo importante que necesitas saber, comprimido en segundos.
            </p>
            <div className="flex space-x-4">
              <div className={`w-8 h-8 ${isDarkMode ? 'bg-gray-800 hover:bg-white' : 'bg-white hover:bg-gray-900'} rounded-lg flex items-center justify-center transition-all duration-300 cursor-pointer group`}>
                <Twitter className={`w-4 h-4 ${isDarkMode ? 'text-gray-400 group-hover:text-black' : 'text-gray-600 group-hover:text-white'}`} />
              </div>
              <div className={`w-8 h-8 ${isDarkMode ? 'bg-gray-800 hover:bg-white' : 'bg-white hover:bg-gray-900'} rounded-lg flex items-center justify-center transition-all duration-300 cursor-pointer group`}>
                <Github className={`w-4 h-4 ${isDarkMode ? 'text-gray-400 group-hover:text-black' : 'text-gray-600 group-hover:text-white'}`} />
              </div>
              <div className={`w-8 h-8 ${isDarkMode ? 'bg-gray-800 hover:bg-white' : 'bg-white hover:bg-gray-900'} rounded-lg flex items-center justify-center transition-all duration-300 cursor-pointer group`}>
                <Mail className={`w-4 h-4 ${isDarkMode ? 'text-gray-400 group-hover:text-black' : 'text-gray-600 group-hover:text-white'}`} />
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="space-y-4">
            <h4 className={`${isDarkMode ? 'text-white' : 'text-gray-900'} font-bold text-lg`}>Navegación</h4>
            <ul className="space-y-2">
              <li><a href="#" className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors text-sm`}>Resúmenes</a></li>
              <li><a href="#" className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors text-sm`}>Tendencias</a></li>
              <li><a href="#" className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors text-sm`}>Alertas</a></li>
              <li><a href="#" className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors text-sm`}>Newsletter</a></li>
            </ul>
          </div>

          {/* Categories */}
          <div className="space-y-4">
            <h4 className={`${isDarkMode ? 'text-white' : 'text-gray-900'} font-bold text-lg`}>Categorías</h4>
            <ul className="space-y-2">
              <li><a href="#" className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors text-sm`}>Mundo</a></li>
              <li><a href="#" className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors text-sm`}>Tecnología</a></li>
              <li><a href="#" className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors text-sm`}>Economía</a></li>
              <li><a href="#" className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors text-sm`}>Cultura</a></li>
            </ul>
          </div>

          {/* Community & Homepage Button */}
          <div className="space-y-4">
            <h4 className={`${isDarkMode ? 'text-white' : 'text-gray-900'} font-bold text-lg`}>Comunidad</h4>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                  <Users className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className={`${isDarkMode ? 'text-white' : 'text-gray-900'} font-bold text-sm`}>50K+</p>
                  <p className={`${isDarkMode ? 'text-gray-400' : 'text-gray-600'} text-xs`}>Lectores activos</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                  <Globe className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className={`${isDarkMode ? 'text-white' : 'text-gray-900'} font-bold text-sm`}>15+</p>
                  <p className={`${isDarkMode ? 'text-gray-400' : 'text-gray-600'} text-xs`}>Países</p>
                </div>
              </div>
              <div 
                className="flex items-center space-x-3 cursor-pointer hover:opacity-80 transition-opacity"
                onClick={addToHomepage}
              >
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Home className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className={`${isDarkMode ? 'text-white' : 'text-gray-900'} font-bold text-sm`}>Agregar</p>
                  <p className={`${isDarkMode ? 'text-gray-400' : 'text-gray-600'} text-xs`}>a inicio</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700 flex flex-col md:flex-row justify-between items-center">
          <p className={`${isDarkMode ? 'text-gray-400' : 'text-gray-600'} text-sm`}>
            © 2024 BLINK. Todos los derechos reservados.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#" className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors text-sm`}>Privacidad</a>
            <a href="#" className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors text-sm`}>Términos</a>
            <a href="#" className={`${isDarkMode ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors text-sm`}>Contacto</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
