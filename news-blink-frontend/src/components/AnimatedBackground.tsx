
import { useTheme } from '@/contexts/ThemeContext';

export const AnimatedBackground = () => {
  const { isDarkMode } = useTheme();

  // Calcular grid dinámicamente basado en el tamaño de pantalla
  const pixelSize = 16;
  const cols = Math.ceil(window.innerWidth / pixelSize);
  const rows = Math.ceil(window.innerHeight / pixelSize);
  const totalPixels = cols * rows;

  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
      {/* Fondo base negro profundo */}
      <div className="absolute inset-0 bg-black" />
      
      {/* Gradiente de oscurecimiento en bordes */}
      <div 
        className="absolute inset-0"
        style={{
          background: `
            radial-gradient(ellipse at center, transparent 30%, rgba(0, 0, 0, 0.3) 70%, rgba(0, 0, 0, 0.6) 100%)
          `
        }}
      />
      
      {/* Matriz de píxeles LED cuadrados */}
      <div className="absolute inset-0">
        {Array.from({ length: totalPixels }).map((_, i) => {
          const x = (i % cols) * pixelSize;
          const y = Math.floor(i / cols) * pixelSize;
          const shouldLight = Math.random() < 0.05; // Solo 5% se encienden
          const animationDelay = Math.random() * 8;
          
          return (
            <div
              key={`led-${i}`}
              className="absolute"
              style={{
                left: `${x}px`,
                top: `${y}px`,
                width: '4px',
                height: '4px',
                backgroundColor: shouldLight 
                  ? 'rgba(59, 130, 246, 0.3)' 
                  : 'rgba(59, 130, 246, 0.02)',
                animation: shouldLight 
                  ? `ledFlicker ${4 + Math.random() * 3}s ease-in-out infinite` 
                  : 'none',
                animationDelay: `${animationDelay}s`
              }}
            />
          );
        })}
      </div>
      
      <style>{`
        @keyframes ledFlicker {
          0%, 90% { 
            opacity: 0.02;
            backgroundColor: rgba(59, 130, 246, 0.02);
          }
          5%, 15% { 
            opacity: 0.4;
            backgroundColor: rgba(59, 130, 246, 0.3);
          }
          20%, 25% { 
            opacity: 0.6;
            backgroundColor: rgba(59, 130, 246, 0.4);
          }
        }
      `}</style>
    </div>
  );
};