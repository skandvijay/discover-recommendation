import { format, formatDistanceToNow, parseISO } from 'date-fns';

/**
 * Format a date string or Date object to a readable format
 */
export const formatDate = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'MMM d, yyyy');
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid date';
  }
};

/**
 * Format a date string or Date object to a relative time format (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDistanceToNow(dateObj, { addSuffix: true });
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return 'Unknown time';
  }
};

/**
 * Format a date string or Date object to a datetime format
 */
export const formatDateTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, 'MMM d, yyyy h:mm a');
  } catch (error) {
    console.error('Error formatting datetime:', error);
    return 'Invalid datetime';
  }
};

/**
 * Truncate text to a specified length with ellipsis
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

/**
 * Format confidence score as percentage
 */
export const formatConfidence = (confidence: number): string => {
  return `${Math.round(confidence * 100)}%`;
};

/**
 * Format relevance score as percentage with color class
 */
export const formatRelevanceScore = (score: number): { 
  text: string; 
  colorClass: string;
} => {
  const percentage = Math.round(score * 100);
  
  let colorClass = 'text-gray-500';
  if (percentage >= 80) colorClass = 'text-green-600';
  else if (percentage >= 60) colorClass = 'text-blue-600';
  else if (percentage >= 40) colorClass = 'text-yellow-600';
  else if (percentage >= 20) colorClass = 'text-orange-600';
  else colorClass = 'text-red-600';

  return {
    text: `${percentage}%`,
    colorClass,
  };
};

/**
 * Get initials from a name
 */
export const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase())
    .join('')
    .slice(0, 2);
};

/**
 * Format user display name
 */
export const formatUserName = (user: { name: string; email: string }): string => {
  return `${user.name} (${user.email})`;
};

/**
 * Generate a color based on a string (for avatars, etc.)
 */
export const stringToColor = (str: string): string => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-yellow-500',
    'bg-red-500',
    'bg-teal-500',
  ];
  
  return colors[Math.abs(hash) % colors.length];
};

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Sanitize HTML content for safe display
 */
export const sanitizeHtml = (html: string): string => {
  // Basic HTML sanitization - in production, use a proper library like DOMPurify
  return html
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    .replace(/javascript:/gi, '');
};