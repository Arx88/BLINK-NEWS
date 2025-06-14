
import React from 'react';
import { Github, Twitter, Mail, Globe, Users } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-gradient-to-br from-gray-900 via-black to-gray-800 border-t border-gray-700/50 mt-20">
      <div className="container mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-white via-gray-300 to-gray-400 rounded-2xl flex items-center justify-center shadow-lg shadow-white/25">
                <span className="text-lg font-black text-black">✦</span>
              </div>
              <h3 className="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-300 to-gray-400">BLINK</h3>
            </div>
            <p className="text-gray-400 text-sm leading-relaxed">
              La plataforma más avanzada para estar al día con las últimas tendencias y rumores tecnológicos.
            </p>
            <div className="flex space-x-4">
              <div className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gradient-to-r hover:from-white hover:to-gray-300 transition-all duration-300 cursor-pointer group">
                <Twitter className="w-4 h-4 text-gray-400 group-hover:text-black" />
              </div>
              <div className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gradient-to-r hover:from-white hover:to-gray-300 transition-all duration-300 cursor-pointer group">
                <Github className="w-4 h-4 text-gray-400 group-hover:text-black" />
              </div>
              <div className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gradient-to-r hover:from-white hover:to-gray-300 transition-all duration-300 cursor-pointer group">
                <Mail className="w-4 h-4 text-gray-400 group-hover:text-black" />
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="space-y-4">
            <h4 className="text-white font-bold text-lg">Navegación</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors text-sm">Tendencias</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors text-sm">Rumores</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors text-sm">IA News</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors text-sm">Newsletter</a></li>
            </ul>
          </div>

          {/* Categories */}
          <div className="space-y-4">
            <h4 className="text-white font-bold text-lg">Categorías</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors text-sm">Inteligencia Artificial</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors text-sm">Blockchain</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors text-sm">Startups</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors text-sm">Gaming</a></li>
            </ul>
          </div>

          {/* Stats */}
          <div className="space-y-4">
            <h4 className="text-white font-bold text-lg">Comunidad</h4>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
                  <Users className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className="text-white font-bold text-sm">50K+</p>
                  <p className="text-gray-400 text-xs">Lectores activos</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
                  <Globe className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className="text-white font-bold text-sm">15+</p>
                  <p className="text-gray-400 text-xs">Países</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-gray-700/50 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm">
            © 2024 BLINK. Todos los derechos reservados.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#" className="text-gray-400 hover:text-white transition-colors text-sm">Privacidad</a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors text-sm">Términos</a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors text-sm">Contacto</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
