/**
 * API type definitions
 */

export interface APIResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T | null;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details: unknown;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
