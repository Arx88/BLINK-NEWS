import React from 'react';
import { cn } from '@/lib/utils';

const Dialog = ({ children, ...props }) => {
  return <div {...props}>{children}</div>;
};

const DialogTrigger = ({ children, asChild, ...props }) => {
  return React.cloneElement(children, props);
};

const DialogContent = React.forwardRef(({ className, children, ...props }, ref) => (
  <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
    <div
      ref={ref}
      className={cn(
        'relative bg-background rounded-lg shadow-lg max-w-lg w-full max-h-[85vh] overflow-auto',
        className
      )}
      {...props}
    >
      {children}
    </div>
  </div>
));
DialogContent.displayName = 'DialogContent';

const DialogHeader = ({ className, ...props }) => (
  <div
    className={cn('flex flex-col space-y-1.5 text-center sm:text-left p-6 pb-0', className)}
    {...props}
  />
);

const DialogTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h2
    ref={ref}
    className={cn('text-lg font-semibold leading-none tracking-tight', className)}
    {...props}
  />
));
DialogTitle.displayName = 'DialogTitle';

export { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle };