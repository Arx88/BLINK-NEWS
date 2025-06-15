
import { useState, useEffect } from 'react';

interface TypewriterTextProps {
  text: string;
  speed?: number;
  className?: string;
}

export const TypewriterText = ({ text, speed = 150, className = '' }: TypewriterTextProps) => {
  const [firstLine, setFirstLine] = useState('');
  const [secondLine, setSecondLine] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  
  const lines = text.split('\n');
  const firstLineText = lines[0] || '';
  const secondLineText = lines[1] || '';
  
  useEffect(() => {
    if (isComplete) return;
    
    const timer = setTimeout(() => {
      // First write the first line
      if (currentIndex < firstLineText.length) {
        setFirstLine(firstLineText.slice(0, currentIndex + 1));
        setCurrentIndex(currentIndex + 1);
      }
      // Then write the second line
      else if (currentIndex < firstLineText.length + secondLineText.length) {
        const secondLineIndex = currentIndex - firstLineText.length;
        setSecondLine(secondLineText.slice(0, secondLineIndex + 1));
        setCurrentIndex(currentIndex + 1);
      }
      // Animation complete
      else {
        setIsComplete(true);
      }
    }, speed);
    
    return () => clearTimeout(timer);
  }, [currentIndex, firstLineText, secondLineText, speed, isComplete]);

  return (
    <div className={className}>
      <div className="h-16 lg:h-20 flex items-center justify-center">
        <span className="text-center">
          {firstLine}
          {!isComplete && currentIndex < firstLineText.length && (
            <span className="inline-block w-1 h-12 lg:h-16 bg-current ml-1 animate-pulse"></span>
          )}
        </span>
      </div>
      <div className="h-16 lg:h-20 flex items-center justify-center">
        <span className="text-center">
          {secondLine}
          {!isComplete && currentIndex >= firstLineText.length && (
            <span className="inline-block w-1 h-12 lg:h-16 bg-current ml-1 animate-pulse"></span>
          )}
        </span>
      </div>
    </div>
  );
};
