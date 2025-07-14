// Mobile Testing Configuration
// Centralized configuration for mobile usability tests

export const MOBILE_DEVICES = [
  { name: 'iPhone 12', width: 390, height: 844 },
  { name: 'iPhone 12 Pro Max', width: 428, height: 926 },
  { name: 'Samsung Galaxy S21', width: 360, height: 800 },
  { name: 'iPad', width: 768, height: 1024 },
  { name: 'iPad Pro', width: 1024, height: 1366 }
];

export const TOUCH_TARGETS = {
  MIN_BUTTON_SIZE: 44,
  MIN_SPACING: 8,
  MIN_FONT_SIZE: 14,
  MIN_READABLE_FONT_SIZE: 16
};

export const PERFORMANCE_THRESHOLDS = {
  PAGE_LOAD_TIME: 3000, // 3 seconds
  ACTION_RESPONSE_TIME: 1000, // 1 second
  ANIMATION_DURATION: 500 // 500ms
};

export const SELECTORS = {
  // Game setup
  PLAYER_INPUT: 'input[placeholder*="Player"]',
  START_GAME_BUTTON: 'button:has-text("Start Game")',
  GAME_CONTAINER: '.game-container',
  
  // Action buttons
  ACTION_BUTTONS: 'button:has-text("Fundraise"), button:has-text("Network"), button:has-text("Sponsor Legislation"), button:has-text("Declare Candidacy"), button:has-text("Use Favor"), button:has-text("Campaign")',
  FUNDRAISE_BUTTON: 'button:has-text("Fundraise")',
  NETWORK_BUTTON: 'button:has-text("Network")',
  SPONSOR_BUTTON: 'button:has-text("Sponsor Legislation")',
  FAVOR_BUTTON: 'button:has-text("Use Favor")',
  
  // Game state
  PLAYER_INFO: '.player-info, .current-player, [data-current-player]',
  ACTION_POINTS: '.action-points, [data-action-points], .ap-display',
  POLITICAL_CAPITAL: '.political-capital, .pc-display, [data-pc]',
  PHASE_DISPLAY: '.phase-display, .game-phase, [data-phase]',
  
  // Modals and dialogs
  MODAL: '.modal, .dialog, [role="dialog"]',
  FAVOR_MENU: '.favor-menu, .favor-selection, [data-favor-menu]',
  VOTING_INTERFACE: '.voting-interface, .legislation-voting, [data-voting]',
  
  // Game info and identity
  GAME_INFO_PANEL: '.quick-access-panel, .game-info-panel, .identity-panel',
  IDENTITY_CARDS: '.identity-card, .archetype-card, .mandate-card',
  
  // Game log and messages
  GAME_LOG: '.game-log, .log-container',
  ERROR_MESSAGE: '.error, .alert, [role="alert"]',
  
  // Interactive elements
  INTERACTIVE_ELEMENTS: 'button, input, select, a[href]',
  FOCUSABLE_ELEMENTS: 'button, input, select, a[href]',
  TEXT_ELEMENTS: 'p, span, div, button, label'
};

export const TEST_DATA = {
  PLAYER_NAME: 'Mobile Test Player',
  TEST_PC_AMOUNT: '10',
  TEST_ACTION_COUNT: 5
};

export const GESTURES = {
  SWIPE_UP: {
    startY: 744, // Near bottom of iPhone 12
    endY: 100,   // Near top
    steps: 10
  },
  SWIPE_DOWN: {
    startY: 100,
    endY: 744,
    steps: 10
  }
};

export const ACCESSIBILITY = {
  MIN_CONTRAST_RATIO: 4.5,
  FOCUS_INDICATORS: ['outline', 'boxShadow'],
  ARIA_ATTRIBUTES: ['aria-label', 'aria-labelledby', 'aria-describedby']
};

export const ERROR_MESSAGES = {
  BUTTON_TOO_SMALL: 'Button too small for touch (44px minimum)',
  ELEMENTS_OVERLAP: 'Elements overlap causing usability issues',
  TEXT_TOO_SMALL: 'Font size too small for mobile (14px minimum)',
  MODAL_TOO_LARGE: 'Modal too large for mobile screen',
  NO_HORIZONTAL_OVERFLOW: 'Content causes horizontal overflow',
  SLOW_LOAD_TIME: 'Page load time exceeds 3 seconds',
  SLOW_RESPONSE_TIME: 'Action response time exceeds 1 second'
};

export const MOBILE_BEST_PRACTICES = {
  TOUCH_TARGETS: {
    MIN_SIZE: 44,
    MIN_SPACING: 8,
    VISUAL_FEEDBACK: true
  },
  TYPOGRAPHY: {
    MIN_FONT_SIZE: 16,
    LINE_HEIGHT: 1.5,
    MIN_CONTRAST: 4.5
  },
  LAYOUT: {
    NO_HORIZONTAL_OVERFLOW: true,
    RESPONSIVE_DESIGN: true,
    VIEWPORT_META: true
  },
  PERFORMANCE: {
    MAX_LOAD_TIME: 3000,
    MAX_RESPONSE_TIME: 1000,
    NO_MEMORY_LEAKS: true
  }
};

// Helper functions for common test operations
export const TestHelpers = {
  // Check if element meets touch target requirements
  isTouchFriendly: (element: any) => {
    const box = element.boundingBox();
    return box && box.width >= TOUCH_TARGETS.MIN_BUTTON_SIZE && 
           box.height >= TOUCH_TARGETS.MIN_BUTTON_SIZE;
  },
  
  // Check if text is readable on mobile
  isReadable: (element: any) => {
    const fontSize = element.evaluate((el: any) => {
      const style = window.getComputedStyle(el);
      return parseInt(style.fontSize);
    });
    return fontSize >= TOUCH_TARGETS.MIN_FONT_SIZE;
  },
  
  // Check if modal is properly sized for mobile
  isMobileModal: (element: any, deviceWidth: number, deviceHeight: number) => {
    const box = element.boundingBox();
    return box && 
           box.width <= deviceWidth - 40 && // 20px margin on each side
           box.height <= deviceHeight - 40;
  },
  
  // Check if elements overlap
  elementsOverlap: (box1: any, box2: any) => {
    return !(box1.x + box1.width <= box2.x || 
             box2.x + box2.width <= box1.x || 
             box1.y + box1.height <= box2.y || 
             box2.y + box2.height <= box1.y);
  }
}; 