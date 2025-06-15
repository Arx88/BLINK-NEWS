
import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';

export function ArticleContent() {
  const { isDarkMode } = useTheme();

  return (
    <div className="space-y-6">
      <p className={`text-lg leading-relaxed ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
        En el panorama tecnológico actual, los avances continúan transformando la manera en que interactuamos con el mundo digital. Este desarrollo representa un cambio paradigmático que promete redefinir los estándares de la industria y establecer nuevas bases para futuras innovaciones.
      </p>
      
      <p className={`text-lg leading-relaxed ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
        Los expertos en el campo han señalado que esta evolución no es solo una mejora incremental, sino un salto cualitativo que aborda problemas fundamentales que han persistido durante años. La implementación de estas nuevas capacidades ha demostrado resultados prometedores en las pruebas iniciales, superando las expectativas más optimistas.
      </p>

      <div className={`p-6 rounded-xl ${isDarkMode ? 'bg-blue-500/10 border-blue-500/20' : 'bg-blue-50 border-blue-200'} border-l-4 ${isDarkMode ? 'border-blue-500' : 'border-blue-600'} my-8`}>
        <blockquote className={`text-xl italic ${isDarkMode ? 'text-blue-300' : 'text-blue-800'}`}>
          "Esta innovación marca el comienzo de una nueva era en la tecnología, donde las posibilidades parecen infinitas y los límites tradicionales se están redefiniendo constantemente."
        </blockquote>
        <cite className={`block mt-4 text-sm ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`}>
          - Dr. María González, Experta en Innovación Tecnológica
        </cite>
      </div>

      <h2 className={`text-2xl font-bold mt-8 mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
        Implicaciones a Largo Plazo
      </h2>
      
      <p className={`text-lg leading-relaxed ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
        El impacto de esta tecnología se extiende más allá de las aplicaciones inmediatas. Los análisis indican que podríamos estar ante un punto de inflexión que influence múltiples sectores, desde la educación hasta la atención médica, pasando por la manufactura y los servicios financieros.
      </p>
      
      <p className={`text-lg leading-relaxed ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
        Las empresas líderes ya están invirtiendo recursos significativos para adaptar sus infraestructuras y procesos a estas nuevas posibilidades. Se estima que el mercado global relacionado con esta tecnología alcanzará los $500 mil millones en los próximos cinco años, representando una oportunidad sin precedentes para innovadores y emprendedores.
      </p>

      <h2 className={`text-2xl font-bold mt-8 mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
        Desafíos y Oportunidades
      </h2>
      
      <p className={`text-lg leading-relaxed ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
        Como ocurre con cualquier avance significativo, existen desafíos importantes que deben abordarse. La regulación, la privacidad de los datos, y la necesidad de actualización de competencias son aspectos críticos que requieren atención inmediata de parte de gobiernos, empresas y instituciones educativas.
      </p>
      
      <p className={`text-lg leading-relaxed ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
        Sin embargo, las oportunidades superan ampliamente los riesgos. La democratización del acceso a herramientas avanzadas, la mejora en la eficiencia operacional, y la posibilidad de resolver problemas complejos que antes parecían intratables, representan beneficios tangibles para la sociedad en su conjunto.
      </p>

      <div className={`p-6 rounded-xl ${isDarkMode ? 'bg-gray-800/30' : 'bg-gray-50'} mt-8`}>
        <h3 className={`text-xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          Conclusiones Clave
        </h3>
        <ul className={`space-y-3 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
          <li className="flex items-start space-x-3">
            <div className={`w-2 h-2 rounded-full ${isDarkMode ? 'bg-blue-500' : 'bg-blue-600'} mt-2 flex-shrink-0`} />
            <span>La adopción temprana será crucial para mantener la competitividad en el mercado global.</span>
          </li>
          <li className="flex items-start space-x-3">
            <div className={`w-2 h-2 rounded-full ${isDarkMode ? 'bg-blue-500' : 'bg-blue-600'} mt-2 flex-shrink-0`} />
            <span>La colaboración entre sectores públicos y privados será fundamental para maximizar los beneficios.</span>
          </li>
          <li className="flex items-start space-x-3">
            <div className={`w-2 h-2 rounded-full ${isDarkMode ? 'bg-blue-500' : 'bg-blue-600'} mt-2 flex-shrink-0`} />
            <span>Es necesaria una inversión continua en educación y capacitación para aprovechar completamente estas nuevas capacidades.</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
