
import { useTheme } from '@/contexts/ThemeContext';
import { useEffect, useState } from 'react';

interface DataPoint {
  id: number;
  x: number;
  y: number;
  size: number;
  opacity: number;
  speedX: number;
  speedY: number;
  pulse: number;
  type: 'data' | 'signal' | 'node';
}

export const AnimatedDotsBackground = () => {
  const { isDarkMode } = useTheme();
  const [dataPoints, setDataPoints] = useState<DataPoint[]>([]);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [gradientOffset, setGradientOffset] = useState(0);

  useEffect(() => {
    const updateDimensions = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (dimensions.width === 0 || dimensions.height === 0) return;

    // Crear puntos de datos que representan información fluyendo
    const initialPoints: DataPoint[] = [];
    const numPoints = 12;

    for (let i = 0; i < numPoints; i++) {
      initialPoints.push({
        id: i,
        x: Math.random() * dimensions.width,
        y: Math.random() * dimensions.height,
        size: Math.random() * 3 + 2,
        opacity: Math.random() * 0.4 + 0.1,
        speedX: (Math.random() - 0.5) * 0.8,
        speedY: (Math.random() - 0.5) * 0.8,
        pulse: Math.random() * Math.PI * 2,
        type: ['data', 'signal', 'node'][Math.floor(Math.random() * 3)] as 'data' | 'signal' | 'node'
      });
    }

    setDataPoints(initialPoints);
  }, [dimensions]);

  useEffect(() => {
    const animationInterval = setInterval(() => {
      const time = Date.now() * 0.001;

      // Animar el gradiente de fondo
      setGradientOffset(prev => (prev + 0.5) % 360);

      // Animar puntos de datos
      setDataPoints(prev => prev.map(point => {
        let newX = point.x + point.speedX;
        let newY = point.y + point.speedY;

        // Rebote en los bordes
        if (newX < 0 || newX > dimensions.width) point.speedX *= -1;
        if (newY < 0 || newY > dimensions.height) point.speedY *= -1;

        // Mantener dentro de los límites
        newX = Math.max(0, Math.min(dimensions.width, newX));
        newY = Math.max(0, Math.min(dimensions.height, newY));

        // Efecto de pulso para simular procesamiento de datos
        const pulseFactor = Math.sin(time * 2 + point.pulse) * 0.3 + 0.7;

        return {
          ...point,
          x: newX,
          y: newY,
          opacity: point.opacity * pulseFactor
        };
      }));
    }, 60);

    return () => clearInterval(animationInterval);
  }, [dimensions]);

  const renderDataPoint = (point: DataPoint) => {
    const baseColor = isDarkMode ? '59, 130, 246' : '37, 99, 235';
    const fillColor = `rgba(${baseColor}, ${point.opacity})`;
    
    if (point.type === 'signal') {
      // Señal como pequeño diamante
      const size = point.size;
      const points = [
        [point.x, point.y - size],
        [point.x + size, point.y],
        [point.x, point.y + size],
        [point.x - size, point.y]
      ].map(p => p.join(',')).join(' ');
      
      return (
        <polygon
          key={point.id}
          points={points}
          fill={fillColor}
          style={{ filter: 'blur(0.5px)' }}
        />
      );
    }
    
    // Puntos de datos como círculos
    return (
      <circle
        key={point.id}
        cx={point.x}
        cy={point.y}
        r={point.size}
        fill={fillColor}
        style={{ filter: 'blur(0.5px)' }}
      />
    );
  };

  if (dimensions.width === 0 || dimensions.height === 0) return null;

  const gradientStyle = isDarkMode 
    ? {
        background: `radial-gradient(circle at ${50 + Math.sin(gradientOffset * 0.02) * 20}% ${50 + Math.cos(gradientOffset * 0.015) * 15}%, rgba(15, 23, 42, 0.8) 0%, rgba(0, 0, 0, 0.95) 50%, rgba(0, 0, 0, 1) 100%)`
      }
    : {
        background: `radial-gradient(circle at ${50 + Math.sin(gradientOffset * 0.02) * 20}% ${50 + Math.cos(gradientOffset * 0.015) * 15}%, rgba(226, 232, 240, 0.9) 0%, rgba(248, 250, 252, 0.95) 50%, rgba(255, 255, 255, 1) 100%)`
      };

  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
      {/* Fondo con gradiente móvil */}
      <div 
        className="absolute inset-0 transition-all duration-1000 ease-in-out"
        style={gradientStyle}
      />
      
      <svg
        width={dimensions.width}
        height={dimensions.height}
        className="absolute inset-0"
        style={{ background: 'transparent' }}
      >
        {/* Cuadrícula más visible */}
        <defs>
          <pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse">
            <path 
              d="M 80 0 L 0 0 0 80" 
              fill="none" 
              stroke={isDarkMode ? 'rgba(59, 130, 246, 0.092)' : 'rgba(37, 99, 235, 0.15)'} 
              strokeWidth="1"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
        
        {/* Puntos de datos */}
        {dataPoints.map(renderDataPoint)}
      </svg>
    </div>
  );
};
