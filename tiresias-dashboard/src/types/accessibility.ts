/**
 * Accessibility type definitions
 */

export type AriaLivePriority = 'polite' | 'assertive' | 'off';

export interface KeyboardShortcutConfig {
  key: string;
  ctrl?: boolean;
  alt?: boolean;
  shift?: boolean;
  action: () => void;
  description: string;
  category: 'navigation' | 'player' | 'general';
}

export interface AccessibilityPreferences {
  keyboardShortcutsEnabled: boolean;
  audioFeedbackEnabled: boolean;
  highContrastMode: boolean;
  reducedMotion: boolean;
  fontSize: 'default' | 'large' | 'extra-large';
}
