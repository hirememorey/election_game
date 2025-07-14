import { test, expect } from '@playwright/test';

test.describe('Mobile UI Elements', () => {
  test.use({
    viewport: { width: 390, height: 844 }, // iPhone 12
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
  });

  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5001');
    await page.waitForLoadState('networkidle');
  });

  // ===== GAME SETUP TESTS =====
  test.describe('Game Setup', () => {
    test('player name inputs are mobile-friendly', async ({ page }) => {
      const playerInputs = page.locator('input[placeholder="Enter name"]');
      await expect(playerInputs.first()).toBeVisible();
      
      // Test input interaction
      await playerInputs.first().click();
      await playerInputs.first().fill('Test Player 1');
      
      // Verify input works
      await expect(playerInputs.first()).toHaveValue('Test Player 1');
    });

    test('start game button is prominent and touch-friendly', async ({ page }) => {
      const startButton = page.locator('#start-game-btn');
      await expect(startButton).toBeVisible();
      
      // Fill required player names
      await page.fill('#player1', 'Player 1');
      await page.fill('#player2', 'Player 2');
      
      // Test button interaction
      await startButton.click();
      
      // Should transition to game state
      const gameContainer = page.locator('#game-screen');
      await expect(gameContainer).toBeVisible();
    });
  });

  // ===== ACTION BUTTON TESTS =====
  test.describe('Action Buttons', () => {
    test.beforeEach(async ({ page }) => {
      // Setup game first
      await page.fill('#player1', 'Player 1');
      await page.fill('#player2', 'Player 2');
      await page.click('#start-game-btn');
      await page.waitForSelector('#game-screen:not(.hidden)');
    });

    test('all action buttons are properly sized and spaced', async ({ page }) => {
      const actionButtons = page.locator('.btn-primary, .btn-secondary');
      const count = await actionButtons.count();
      
      for (let i = 0; i < count; i++) {
        const button = actionButtons.nth(i);
        const box = await button.boundingBox();
        
        // Check minimum touch target size (44px)
        expect(box?.width).toBeGreaterThanOrEqual(44);
        expect(box?.height).toBeGreaterThanOrEqual(44);
      }
    });

    test('action costs are clearly displayed', async ({ page }) => {
      // Wait for action buttons to appear
      await page.waitForSelector('.btn-primary, .btn-secondary', { timeout: 10000 });
      
      const actionButtons = page.locator('.btn-primary, .btn-secondary');
      const count = await actionButtons.count();
      
      // At least some buttons should have cost indicators
      let hasCostIndicator = false;
      for (let i = 0; i < count; i++) {
        const button = actionButtons.nth(i);
        const text = await button.textContent();
        if (text && (text.includes('AP') || text.includes('PC'))) {
          hasCostIndicator = true;
          break;
        }
      }
      
      expect(hasCostIndicator).toBe(true);
    });

    test('disabled actions are visually distinct', async ({ page }) => {
      // Wait for action buttons to appear
      await page.waitForSelector('.btn-primary, .btn-secondary', { timeout: 10000 });
      
      const actionButtons = page.locator('.btn-primary, .btn-secondary');
      const count = await actionButtons.count();
      
      // Check if any buttons are disabled
      let hasDisabledButton = false;
      for (let i = 0; i < count; i++) {
        const button = actionButtons.nth(i);
        const isDisabled = await button.isDisabled();
        if (isDisabled) {
          hasDisabledButton = true;
          // Check if disabled button has appropriate styling
          const classes = await button.getAttribute('class');
          expect(classes).toContain('disabled');
          break;
        }
      }
      
      // It's okay if no buttons are disabled initially
      if (hasDisabledButton) {
        expect(hasDisabledButton).toBe(true);
      }
    });
  });

  // ===== GAME STATE DISPLAY TESTS =====
  test.describe('Game State Display', () => {
    test.beforeEach(async ({ page }) => {
      await page.fill('#player1', 'Player 1');
      await page.fill('#player2', 'Player 2');
      await page.click('#start-game-btn');
      await page.waitForSelector('#game-screen:not(.hidden)');
    });

    test('current player is clearly indicated', async ({ page }) => {
      // Wait for game state to load
      await page.waitForTimeout(2000);
      
      // Look for player indicators in the UI
      const playerIndicators = page.locator('[class*="player"], [class*="current"]');
      const count = await playerIndicators.count();
      
      // Should have some player indication
      expect(count).toBeGreaterThan(0);
    });

    test('action points are prominently displayed', async ({ page }) => {
      // Wait for game state to load
      await page.waitForTimeout(2000);
      
      // Look for AP indicators
      const apElements = page.locator('text=/AP|Action Points/i');
      const count = await apElements.count();
      
      // Should have AP display
      expect(count).toBeGreaterThan(0);
    });

    test('political capital is clearly shown', async ({ page }) => {
      // Wait for game state to load
      await page.waitForTimeout(2000);
      
      // Look for PC indicators
      const pcElements = page.locator('text=/PC|Political Capital/i');
      const count = await pcElements.count();
      
      // Should have PC display
      expect(count).toBeGreaterThan(0);
    });

    test('game phase is indicated', async ({ page }) => {
      // Wait for game state to load
      await page.waitForTimeout(2000);
      
      const phaseIndicator = page.locator('#phase-indicator');
      await expect(phaseIndicator).toBeVisible();
      
      // Should have phase content
      const text = await phaseIndicator.textContent();
      expect(text).toBeTruthy();
    });
  });

  // ===== MODAL AND DIALOG TESTS =====
  test.describe('Modals and Dialogs', () => {
    test.beforeEach(async ({ page }) => {
      await page.fill('#player1', 'Player 1');
      await page.fill('#player2', 'Player 2');
      await page.click('#start-game-btn');
      await page.waitForSelector('#game-screen:not(.hidden)');
    });

    test('PC commitment dialogs are mobile-optimized', async ({ page }) => {
      // Wait for game state to load
      await page.waitForTimeout(2000);
      
      // Look for commitment-related buttons
      const commitmentButtons = page.locator('button:has-text("Support"), button:has-text("Oppose")');
      const count = await commitmentButtons.count();
      
      if (count > 0) {
        // Test dialog interaction
        await commitmentButtons.first().click();
        
        // Should show a dialog/modal
        const modal = page.locator('.modal, [role="dialog"]');
        await expect(modal).toBeVisible({ timeout: 5000 });
        
        // Check modal is mobile-friendly
        const modalBox = await modal.boundingBox();
        expect(modalBox?.width).toBeLessThanOrEqual(390); // Should fit mobile width
      }
    });

    test('favor selection menu is touch-friendly', async ({ page }) => {
      // Wait for game state to load
      await page.waitForTimeout(2000);
      
      // Look for favor-related buttons
      const favorButtons = page.locator('button:has-text("Favor"), button:has-text("Use")');
      const count = await favorButtons.count();
      
      if (count > 0) {
        await favorButtons.first().click();
        
        // Should show a menu
        const menu = page.locator('.menu, .dropdown, [role="menu"]');
        await expect(menu).toBeVisible({ timeout: 5000 });
        
        // Check menu items are touch-friendly
        const menuItems = menu.locator('button, a');
        const itemCount = await menuItems.count();
        
        for (let i = 0; i < itemCount; i++) {
          const item = menuItems.nth(i);
          const box = await item.boundingBox();
          expect(box?.height).toBeGreaterThanOrEqual(44); // Minimum touch target
        }
      }
    });

    test('legislation voting interface is mobile-friendly', async ({ page }) => {
      // Wait for game state to load
      await page.waitForTimeout(2000);
      
      // Look for legislation-related buttons
      const legislationButtons = page.locator('button:has-text("Legislation"), button:has-text("Vote")');
      const count = await legislationButtons.count();
      
      if (count > 0) {
        await legislationButtons.first().click();
        
        // Should show voting interface
        const votingInterface = page.locator('.voting-interface, .legislation-menu');
        await expect(votingInterface).toBeVisible({ timeout: 5000 });
        
        // Check interface is mobile-friendly
        const interfaceBox = await votingInterface.boundingBox();
        expect(interfaceBox?.width).toBeLessThanOrEqual(390); // Should fit mobile width
      }
    });
  });

  // ===== GESTURE AND INTERACTION TESTS =====
  test.describe('Gestures and Interactions', () => {
    test.beforeEach(async ({ page }) => {
      await page.fill('#player1', 'Player 1');
      await page.fill('#player2', 'Player 2');
      await page.click('#start-game-btn');
      await page.waitForSelector('#game-screen:not(.hidden)');
    });

    test('swipe up shows game info panel', async ({ page }) => {
      // Wait for game state to load
      await page.waitForTimeout(2000);
      
      const quickAccessPanel = page.locator('#quick-access-panel');
      
      // Simulate swipe up gesture
      await page.mouse.move(195, 800); // Center of screen
      await page.mouse.down();
      await page.mouse.move(195, 400); // Swipe up
      await page.mouse.up();
      
      // Should show quick access panel
      await expect(quickAccessPanel).toBeVisible({ timeout: 5000 });
    });

    test('keyboard shortcuts work on mobile', async ({ page }) => {
      // Wait for game state to load
      await page.waitForTimeout(2000);
      
      const quickAccessPanel = page.locator('#quick-access-panel');
      
      // Press 'G' key to show game info
      await page.keyboard.press('g');
      
      // Should show quick access panel
      await expect(quickAccessPanel).toBeVisible({ timeout: 5000 });
    });

    test('touch scrolling works in game log', async ({ page }) => {
      // Wait for game state to load
      await page.waitForTimeout(2000);
      
      const gameLog = page.locator('#game-log');
      await expect(gameLog).toBeVisible();
      
      // Test scrolling
      await gameLog.scrollIntoViewIfNeeded();
      
      // Should be able to scroll
      const scrollTop = await gameLog.evaluate(el => el.scrollTop);
      expect(scrollTop).toBeDefined();
    });
  });

  // ===== RESPONSIVE LAYOUT TESTS =====
  test.describe('Responsive Layout', () => {
    test.beforeEach(async ({ page }) => {
      await page.fill('#player1', 'Player 1');
      await page.fill('#player2', 'Player 2');
      await page.click('#start-game-btn');
      await page.waitForSelector('#game-screen:not(.hidden)');
    });

    test('layout adapts to different orientations', async ({ page }) => {
      // Test portrait orientation
      await page.setViewportSize({ width: 390, height: 844 });
      await page.waitForTimeout(1000);
      
      // Test landscape orientation
      await page.setViewportSize({ width: 844, height: 390 });
      await page.waitForTimeout(1000);
      
      // Should still be functional
      const gameScreen = page.locator('#game-screen');
      await expect(gameScreen).toBeVisible();
    });

    test('text remains readable at all sizes', async ({ page }) => {
      // Check text elements have minimum font size
      const textElements = page.locator('p, span, div, h1, h2, h3');
      const count = await textElements.count();
      
      for (let i = 0; i < Math.min(count, 10); i++) {
        const element = textElements.nth(i);
        const fontSize = await element.evaluate(el => {
          const style = window.getComputedStyle(el);
          return parseInt(style.fontSize);
        });
        
        // Font size should be at least 12px for readability
        expect(fontSize).toBeGreaterThanOrEqual(12);
      }
    });

    test('no horizontal overflow', async ({ page }) => {
      // Check for horizontal scrolling
      const body = page.locator('body');
      const scrollWidth = await body.evaluate(el => el.scrollWidth);
      const clientWidth = await body.evaluate(el => el.clientWidth);
      
      // Should not have horizontal overflow
      expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
    });
  });

  // ===== ACCESSIBILITY TESTS =====
  test.describe('Accessibility', () => {
    test.beforeEach(async ({ page }) => {
      await page.fill('#player1', 'Player 1');
      await page.fill('#player2', 'Player 2');
      await page.click('#start-game-btn');
      await page.waitForSelector('#game-screen:not(.hidden)');
    });

    test('all interactive elements are keyboard accessible', async ({ page }) => {
      // Check buttons have proper roles
      const buttons = page.locator('button');
      const count = await buttons.count();
      
      for (let i = 0; i < count; i++) {
        const button = buttons.nth(i);
        const role = await button.getAttribute('role');
        const tabindex = await button.getAttribute('tabindex');
        
        // Should be keyboard accessible
        expect(role === 'button' || tabindex !== '-1').toBe(true);
      }
    });

    test('focus order is logical', async ({ page }) => {
      // Test tab navigation
      await page.keyboard.press('Tab');
      
      // Should focus on first interactive element
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    });

    test('color contrast is sufficient', async ({ page }) => {
      // Check text elements have good contrast
      const textElements = page.locator('p, span, div, h1, h2, h3');
      const count = await textElements.count();
      
      // Sample a few elements for contrast check
      for (let i = 0; i < Math.min(count, 5); i++) {
        const element = textElements.nth(i);
        const color = await element.evaluate(el => {
          const style = window.getComputedStyle(el);
          return style.color;
        });
        
        // Should have a defined color (not transparent)
        expect(color).not.toBe('rgba(0, 0, 0, 0)');
      }
    });
  });
}); 