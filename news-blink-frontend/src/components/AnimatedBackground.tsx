
import { useTheme } from '@/contexts/ThemeContext';
import { useEffect, useState } from 'react';
import { AnimatedDotsBackground } from './AnimatedDotsBackground';

export const AnimatedBackground = () => {
  const { isDarkMode } = useTheme();
  const [gradientState, setGradientState] = useState({
    hue1: 240,
    hue2: 280,
    saturation: 15,
    lightness: isDarkMode ? 5 : 95,
    position: 50
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setGradientState(prev => {
        // Slow, organic color evolution based on sine waves
        const time = Date.now() * 0.0001; // Very slow time progression
        
        // Primary hue shifts slowly through cool colors
        const newHue1 = 220 + Math.sin(time) * 40; // 180-260 range (blues to purples)
        
        // Secondary hue follows with offset
        const newHue2 = newHue1 + 30 + Math.sin(time * 0.7) * 20;
        
        // Subtle saturation breathing
        const newSaturation = 12 + Math.sin(time * 1.3) * 8; // 4-20 range
        
        // Very subtle lightness variation
        const baseLightness = isDarkMode ? 5 : 95;
        const newLightness = baseLightness + Math.sin(time * 0.9) * 3;
        
        // Gradient position slowly shifts
        const newPosition = 45 + Math.sin(time * 0.6) * 10; // 35-55 range
        
        return {
          hue1: newHue1,
          hue2: newHue2,
          saturation: newSaturation,
          lightness: newLightness,
          position: newPosition
        };
      });
    }, 100); // Update every 100ms for smooth transitions

    return () => clearInterval(interval);
  }, [isDarkMode]);

  // Generate the dynamic gradient
  const dynamicGradient = `
    radial-gradient(
      ellipse at ${gradientState.position}% 40%, 
      hsl(${gradientState.hue1}, ${gradientState.saturation}%, ${gradientState.lightness}%) 0%,
      hsl(${(gradientState.hue1 + gradientState.hue2) / 2}, ${gradientState.saturation * 0.7}%, ${gradientState.lightness * 0.98}%) 30%,
      hsl(${gradientState.hue2}, ${gradientState.saturation * 0.5}%, ${gradientState.lightness * 0.95}%) 60%,
      ${isDarkMode ? 'hsl(0, 0%, 0%)' : 'hsl(0, 0%, 100%)'} 100%
    )
  `;

  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
      {/* Base gradient background */}
      <div 
        className="absolute inset-0 transition-all duration-[2000ms] ease-in-out"
        style={{
          background: dynamicGradient,
        }}
      />
      
      {/* Animated dots layer */}
      <AnimatedDotsBackground />
      
      {/* Subtle overlay for depth */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          background: `linear-gradient(
            45deg, 
            transparent 0%, 
            ${isDarkMode ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)'} 50%, 
            transparent 100%
          )`,
          transform: `translateX(${Math.sin(Date.now() * 0.0001) * 20}px)`,
          transition: 'transform 2s ease-in-out'
        }}
      />
    </div>
  );
};
