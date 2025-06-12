import React from 'react';
import { cn } from '@/lib/utils';

const Select = ({ children, value, onValueChange, ...props }) => {
  return (
    <div className="relative" {...props}>
      {React.Children.map(children, child => 
        React.cloneElement(child, { value, onValueChange })
      )}
    </div>
  );
};

const SelectTrigger = React.forwardRef(({ className, children, value, onValueChange, ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
      className
    )}
    {...props}
  >
    {children}
  </button>
));
SelectTrigger.displayName = 'SelectTrigger';

const SelectValue = ({ placeholder }) => (
  <span className="text-muted-foreground">{placeholder}</span>
);

const SelectContent = ({ children, value, onValueChange }) => (
  <div className="absolute top-full left-0 z-50 w-full mt-1 bg-background border border-input rounded-md shadow-lg">
    {React.Children.map(children, child => 
      React.cloneElement(child, { value, onValueChange })
    )}
  </div>
);

const SelectItem = ({ value: itemValue, children, value, onValueChange }) => (
  <button
    className="w-full px-3 py-2 text-left text-sm hover:bg-accent hover:text-accent-foreground"
    onClick={() => onValueChange(itemValue)}
  >
    {children}
  </button>
);

export { Select, SelectTrigger, SelectValue, SelectContent, SelectItem };