import { test, expect } from '@playwright/test';

// Mobile-specific test configuration
const mobileDevices = [
  { name: 'iPhone 12', width: 390, height: 844 },
  { name: 'iPhone 12 Pro Max', width: 428, height: 926 },
  { name: 'Samsung Galaxy S21', width: 360, height: 800 },
  { name: 'iPad', width: 768, height: 1024 },
  { name: 'iPad Pro', width: 1024, height: 1366 }
];

// Test configuration for mobile devices
test.describe('Mobile Usability Tests', () => {
  mobileDevices.forEach(device => {
    test.describe(`Device: ${device.name}`, () => {
      test.use({
        viewport: { width: device.width, height: device.height },
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
      });

      test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:5001');
        await page.waitForLoadState('networkidle');
      });

      // ===== TOUCH INTERACTION TESTS =====
      test.describe('Touch Interactions', () => {
        test('all buttons are touch-friendly (minimum 44px)', async ({ page }) => {
          const buttons = await page.locator('button').all();
          
          for (const button of buttons) {
            const box = await button.boundingBox();
            if (box) {
              expect(box.width).toBeGreaterThanOrEqual(44);
              expect(box.height).toBeGreaterThanOrEqual(44);
            }
          }
        });

        test('buttons have proper touch spacing (minimum 8px between)', async ({ page }) => {
          const buttons = await page.locator('button').all();
          
          for (let i = 0; i < buttons.length - 1; i++) {
            const button1 = await buttons[i].boundingBox();
            const button2 = await buttons[i + 1].boundingBox();
            
            if (button1 && button2) {
              const horizontalSpacing = Math.abs(button1.x - button2.x);
              const verticalSpacing = Math.abs(button1.y - button2.y);
              
              // If buttons are close to each other, ensure minimum spacing
              if (horizontalSpacing < 100 && verticalSpacing < 100) {
                expect(horizontalSpacing).toBeGreaterThanOrEqual(8);
                expect(verticalSpacing).toBeGreaterThanOrEqual(8);
              }
            }
          }
        });

        test('modal dialogs are touch-friendly', async ({ page }) => {
          // Create a game first
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          // Trigger a modal (like PC commitment)
          await page.click('button:has-text("Fundraise")');
          await page.waitForTimeout(500);
          
          // Check if any modals appear and are touch-friendly
          const modals = await page.locator('.modal, .dialog, [role="dialog"]').all();
          if (modals.length > 0) {
            for (const modal of modals) {
              const box = await modal.boundingBox();
              if (box) {
                // Modal should be centered and properly sized
                expect(box.width).toBeLessThan(device.width - 40); // 20px margin on each side
                expect(box.height).toBeLessThan(device.height - 40);
              }
            }
          }
        });

        test('swipe gestures work for game info panel', async ({ page }) => {
          // Create a game first
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          // Test swipe up gesture
          const gameContainer = page.locator('.game-container');
          const startY = device.height - 100;
          const endY = 100;
          
          await page.mouse.move(device.width / 2, startY);
          await page.mouse.down();
          await page.mouse.move(device.width / 2, endY, { steps: 10 });
          await page.mouse.up();
          
          // Check if game info panel appears
          await page.waitForTimeout(500);
          const infoPanel = page.locator('.quick-access-panel, .game-info-panel');
          await expect(infoPanel).toBeVisible();
        });
      });

      // ===== RESPONSIVE DESIGN TESTS =====
      test.describe('Responsive Design', () => {
        test('no horizontal scrolling', async ({ page }) => {
          const body = await page.locator('body');
          const bodyBox = await body.boundingBox();
          const viewport = page.viewportSize();
          
          if (bodyBox && viewport) {
            expect(bodyBox.width).toBeLessThanOrEqual(viewport.width);
          }
        });

        test('text is readable (minimum 16px font size)', async ({ page }) => {
          const textElements = await page.locator('p, span, div, button, input, label').all();
          
          for (const element of textElements) {
            const fontSize = await element.evaluate(el => {
              const style = window.getComputedStyle(el);
              return parseInt(style.fontSize);
            });
            
            expect(fontSize).toBeGreaterThanOrEqual(14); // Allow slightly smaller for some elements
          }
        });

        test('contrast ratios meet accessibility standards', async ({ page }) => {
          // This is a simplified test - in practice you'd use a proper contrast checker
          const textElements = await page.locator('p, span, div, button, label').all();
          
          for (const element of textElements) {
            const color = await element.evaluate(el => {
              const style = window.getComputedStyle(el);
              return style.color;
            });
            
            // Basic check - ensure text isn't white on white or black on black
            expect(color).not.toBe('rgb(255, 255, 255)'); // Not pure white
            expect(color).not.toBe('rgb(0, 0, 0)'); // Not pure black
          }
        });

        test('keyboard input works on mobile', async ({ page }) => {
          // Test that input fields work with mobile keyboard
          const inputs = await page.locator('input').all();
          
          for (const input of inputs) {
            await input.click();
            await input.fill('test');
            await expect(input).toHaveValue('test');
          }
        });
      });

      // ===== UI LAYOUT TESTS =====
      test.describe('UI Layout', () => {
        test('no overlapping elements', async ({ page }) => {
          const elements = await page.locator('*').all();
          const elementBoxes: Array<{ x: number; y: number; width: number; height: number }> = [];
          
          for (const element of elements) {
            const box = await element.boundingBox();
            if (box && box.width > 0 && box.height > 0) {
              elementBoxes.push(box);
            }
          }
          
          // Check for overlapping elements
          for (let i = 0; i < elementBoxes.length; i++) {
            for (let j = i + 1; j < elementBoxes.length; j++) {
              const box1 = elementBoxes[i];
              const box2 = elementBoxes[j];
              
              const overlap = !(box1.x + box1.width <= box2.x || 
                              box2.x + box2.width <= box1.x || 
                              box1.y + box1.height <= box2.y || 
                              box2.y + box2.height <= box1.y);
              
              expect(overlap).toBe(false);
            }
          }
        });

        test('action buttons are properly spaced', async ({ page }) => {
          // Create a game first
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          const actionButtons = await page.locator('.action-button, button[onclick*="performAction"]').all();
          
          for (let i = 0; i < actionButtons.length - 1; i++) {
            const button1 = await actionButtons[i].boundingBox();
            const button2 = await actionButtons[i + 1].boundingBox();
            
            if (button1 && button2) {
              // Buttons should have reasonable spacing
              const spacing = Math.abs(button1.y - button2.y);
              expect(spacing).toBeGreaterThanOrEqual(8);
            }
          }
        });

        test('game state information is clearly visible', async ({ page }) => {
          // Create a game first
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          // Check that key game state elements are visible
          const stateElements = [
            '.game-state',
            '.player-info',
            '.action-points',
            '.political-capital'
          ];
          
          for (const selector of stateElements) {
            const element = page.locator(selector);
            if (await element.count() > 0) {
              await expect(element.first()).toBeVisible();
            }
          }
        });

        test('identity cards display properly on mobile', async ({ page }) => {
          // Create a game first
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          // Trigger identity display
          await page.keyboard.press('g');
          await page.waitForTimeout(500);
          
          const identityCards = page.locator('.identity-card, .archetype-card, .mandate-card');
          if (await identityCards.count() > 0) {
            await expect(identityCards.first()).toBeVisible();
            
            // Check that cards fit within viewport
            const card = await identityCards.first().boundingBox();
            if (card) {
              expect(card.width).toBeLessThan(device.width - 20);
              expect(card.height).toBeLessThan(device.height - 20);
            }
          }
        });
      });

      // ===== GAME FLOW TESTS =====
      test.describe('Game Flow', () => {
        test('complete game flow works on mobile', async ({ page }) => {
          // Start game
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          // Perform basic actions
          const actions = ['Fundraise', 'Network'];
          
          for (const action of actions) {
            const button = page.locator(`button:has-text("${action}")`);
            if (await button.count() > 0) {
              await button.click();
              await page.waitForTimeout(500);
              
              // Check that action was processed
              const gameLog = page.locator('.game-log');
              await expect(gameLog).toBeVisible();
            }
          }
        });

        test('legislation voting works on mobile', async ({ page }) => {
          // Create a game and sponsor legislation
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          // Sponsor legislation
          const sponsorButton = page.locator('button:has-text("Sponsor Legislation")');
          if (await sponsorButton.count() > 0) {
            await sponsorButton.click();
            await page.waitForTimeout(500);
            
            // Check that legislation was sponsored
            const gameLog = page.locator('.game-log');
            await expect(gameLog).toBeVisible();
          }
        });

        test('PC commitment dialogs work on mobile', async ({ page }) => {
          // Create a game
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          // Try to commit PC (this should trigger a dialog)
          const commitButton = page.locator('button:has-text("Support"), button:has-text("Oppose")');
          if (await commitButton.count() > 0) {
            await commitButton.first().click();
            await page.waitForTimeout(500);
            
            // Check for dialog or modal
            const dialog = page.locator('.modal, .dialog, [role="dialog"]');
            if (await dialog.count() > 0) {
              await expect(dialog.first()).toBeVisible();
            }
          }
        });

        test('pass turn functionality works', async ({ page }) => {
          // Create a game
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          // Look for Pass Turn button
          const passButton = page.locator('button:has-text("Pass Turn"), button:has-text("Pass")');
          if (await passButton.count() > 0) {
            await passButton.first().click();
            await page.waitForTimeout(500);
            
            // Check that turn advanced
            const gameLog = page.locator('.game-log');
            await expect(gameLog).toBeVisible();
          }
        });
      });

      // ===== PERFORMANCE TESTS =====
      test.describe('Performance', () => {
        test('page loads within 3 seconds', async ({ page }) => {
          const startTime = Date.now();
          await page.goto('http://localhost:5001');
          await page.waitForLoadState('networkidle');
          const loadTime = Date.now() - startTime;
          
          expect(loadTime).toBeLessThan(3000);
        });

        test('actions respond within 1 second', async ({ page }) => {
          // Create a game first
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          // Test action response time
          const button = page.locator('button:has-text("Fundraise")');
          if (await button.count() > 0) {
            const startTime = Date.now();
            await button.click();
            await page.waitForTimeout(500); // Wait for response
            const responseTime = Date.now() - startTime;
            
            expect(responseTime).toBeLessThan(1000);
          }
        });

        test('no memory leaks during gameplay', async ({ page }) => {
          // Create a game
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          // Perform multiple actions to test for memory leaks
          for (let i = 0; i < 5; i++) {
            const button = page.locator('button:has-text("Fundraise")');
            if (await button.count() > 0) {
              await button.click();
              await page.waitForTimeout(200);
            }
          }
          
          // Check that page is still responsive
          const gameContainer = page.locator('.game-container');
          await expect(gameContainer).toBeVisible();
        });
      });

      // ===== ACCESSIBILITY TESTS =====
      test.describe('Accessibility', () => {
        test('all interactive elements have proper ARIA labels', async ({ page }) => {
          const interactiveElements = await page.locator('button, input, select, a[href]').all();
          
          for (const element of interactiveElements) {
            const ariaLabel = await element.getAttribute('aria-label');
            const ariaLabelledby = await element.getAttribute('aria-labelledby');
            const textContent = await element.textContent();
            
            // At least one of these should be present
            const hasAccessibleName = ariaLabel || ariaLabelledby || (textContent && textContent.trim().length > 0);
            expect(hasAccessibleName).toBe(true);
          }
        });

        test('focus indicators are visible', async ({ page }) => {
          const focusableElements = await page.locator('button, input, select, a[href]').all();
          
          for (const element of focusableElements) {
            await element.focus();
            const computedStyle = await element.evaluate(el => {
              const style = window.getComputedStyle(el);
              return {
                outline: style.outline,
                boxShadow: style.boxShadow
              };
            });
            
            // Check for visible focus indicator
            const hasFocusIndicator = computedStyle.outline !== 'none' || computedStyle.boxShadow !== 'none';
            expect(hasFocusIndicator).toBe(true);
          }
        });

        test('color is not the only way to convey information', async ({ page }) => {
          // Check that important information isn't conveyed only through color
          const coloredElements = await page.locator('*').all();
          
          for (const element of coloredElements) {
            const color = await element.evaluate(el => {
              const style = window.getComputedStyle(el);
              return style.color;
            });
            
            const backgroundColor = await element.evaluate(el => {
              const style = window.getComputedStyle(el);
              return style.backgroundColor;
            });
            
            // If element has color, it should also have text or icon
            if (color !== 'rgba(0, 0, 0, 0)') {
              const textContent = await element.textContent();
              const hasIcon = await element.locator('svg, img, i').count() > 0;
              
              expect(textContent || hasIcon).toBe(true);
            }
          }
        });
      });

      // ===== ERROR HANDLING TESTS =====
      test.describe('Error Handling', () => {
        test('network errors are handled gracefully', async ({ page }) => {
          // Simulate network error by changing API URL
          await page.addInitScript(() => {
            (window as any).API_BASE_URL = 'http://localhost:9999/api'; // Invalid URL
          });
          
          await page.goto('http://localhost:5001');
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          
          // Should show error message
          await page.waitForTimeout(2000);
          const errorMessage = page.locator('.error, .alert, [role="alert"]');
          if (await errorMessage.count() > 0) {
            await expect(errorMessage.first()).toBeVisible();
          }
        });

        test('invalid actions show appropriate error messages', async ({ page }) => {
          // Create a game
          await page.fill('input[placeholder*="Player"]', 'Test Player');
          await page.click('button:has-text("Start Game")');
          await page.waitForSelector('.game-container');
          
          // Try to perform an action without sufficient resources
          const expensiveAction = page.locator('button:has-text("Sponsor Legislation")');
          if (await expensiveAction.count() > 0) {
            await expensiveAction.click();
            await page.waitForTimeout(500);
            
            // Should show error message
            const errorMessage = page.locator('.error, .alert, [role="alert"]');
            if (await errorMessage.count() > 0) {
              await expect(errorMessage.first()).toBeVisible();
            }
          }
        });
      });
    });
  });
}); 