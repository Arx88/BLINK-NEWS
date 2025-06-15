
import { TypewriterText } from './TypewriterText';
import { AnimatedEye } from './AnimatedEye';
import { useTheme } from '@/contexts/ThemeContext';

export const HeroSection = () => {
  const { isDarkMode } = useTheme();

  return (
    <div className="text-center space-y-8">
      <div className="space-y-8">
        <div className="flex justify-center mb-6">
          <AnimatedEye />
        </div>
        <div className={`text-6xl lg:text-8xl font-black tracking-tight mb-12 ${isDarkMode ? 'text-blue-500' : 'text-blue-700'}`}>
          BLINK
        </div>
        <div className="h-40 lg:h-48 flex items-center justify-center mt-16">
          <h1 className={`text-6xl lg:text-8xl font-black tracking-tight leading-tight ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>
            <TypewriterText 
              text="INFORMACIÓN EN
SEGUNDOS"
              speed={100}
            />
          </h1>
        </div>
      </div>
      
      <div className="max-w-3xl mx-auto space-y-6 mt-16">
        <p className={`text-xl lg:text-2xl font-bold ${isDarkMode ? 'text-gray-200' : 'text-slate-700'}`}>
          ⚡ AI-powered
        </p>
      </div>
    </div>
  );
};
