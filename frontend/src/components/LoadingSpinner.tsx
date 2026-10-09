export default function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-3',
    lg: 'h-12 w-12 border-4',
  };

  return (
    <div className="flex justify-center items-center p-4">
      <div className={`animate-spin rounded-full border-blue-600 border-t-transparent ${sizeClasses[size]}`}></div>
    </div>
  );
}