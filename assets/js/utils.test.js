import { formatDate } from './utils';

describe('Utility Functions', () => {
  describe('formatDate', () => {
    it('should format a valid date string correctly', () => {
      const date = '2024-04-10T12:00:00Z';
      const formatted = formatDate(date);
      expect(formatted).toBe('April 10, 2024');
    });

    it('should return empty string for null input', () => {
      const formatted = formatDate(null);
      expect(formatted).toBe('');
    });

    it('should return empty string for undefined input', () => {
      const formatted = formatDate(undefined);
      expect(formatted).toBe('');
    });
  });
});