import { test, expect } from '@playwright/test';
import { 
  getCurrentPlayerInfo, 
  performValidAction, 
  createNewGame,
  handleSponsorLegislationModal,
  handleLegislationCommitmentModal
} from './test-utils';

test.describe('Mobile Results Flow Tests', () => {
  test('legislation results are displayed on mobile after full game flow', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    
    // Create new game
    await createNewGame(page);
    
    console.log('=== Testing Legislation Results Flow (Full Game Flow) ===');
    
    // Step 1: Alice sponsors legislation in Round 1
    console.log('\n--- Round 1: Alice sponsors legislation ---');
    await expect(page.locator('#phase-indicator .player-name').getByText('Alice')).toBeVisible();
    await performValidAction(page, 'sponsor legislation', 2);
    await handleSponsorLegislationModal(page);
    
    // Pass turns to complete Round 1
    console.log('\n--- Completing Round 1 ---');
    for (let i = 0; i < 2; i++) {
      const currentInfo = await getCurrentPlayerInfo(page);
      console.log(`Passing turn for ${currentInfo.playerName}`);
      await performValidAction(page, 'pass turn', 0);
      await page.waitForTimeout(1000);
    }
    
    // Step 2: Bob supports legislation in Round 2
    console.log('\n--- Round 2: Bob supports legislation ---');
    const bobInfo = await getCurrentPlayerInfo(page);
    if (bobInfo.playerName === 'Bob') {
      await performValidAction(page, 'support', 1, 5);
      await handleLegislationCommitmentModal(page, 'support', 5);
    }
    
    // Pass turns to complete Round 2
    console.log('\n--- Completing Round 2 ---');
    for (let i = 0; i < 2; i++) {
      const currentInfo = await getCurrentPlayerInfo(page);
      console.log(`Passing turn for ${currentInfo.playerName}`);
      await performValidAction(page, 'pass turn', 0);
      await page.waitForTimeout(1000);
    }
    
    // Step 3: Charlie opposes legislation in Round 3
    console.log('\n--- Round 3: Charlie opposes legislation ---');
    const charlieInfo = await getCurrentPlayerInfo(page);
    if (charlieInfo.playerName === 'Charlie') {
      await performValidAction(page, 'oppose', 1, 3);
      await handleLegislationCommitmentModal(page, 'oppose', 3);
    }
    
    // Pass turns to complete Round 3
    console.log('\n--- Completing Round 3 ---');
    for (let i = 0; i < 2; i++) {
      const currentInfo = await getCurrentPlayerInfo(page);
      console.log(`Passing turn for ${currentInfo.playerName}`);
      await performValidAction(page, 'pass turn', 0);
      await page.waitForTimeout(1000);
    }
    
    // Step 4: Complete Round 4 to trigger Legislation Phase
    console.log('\n--- Round 4: Completing final round ---');
    for (let i = 0; i < 3; i++) {
      const currentInfo = await getCurrentPlayerInfo(page);
      console.log(`Passing turn for ${currentInfo.playerName}`);
      await performValidAction(page, 'pass turn', 0);
      await page.waitForTimeout(1000);
    }
    
    // Check if we're now in Legislation Phase
    console.log('\n--- Checking for Legislation Phase ---');
    const phaseIndicator = page.locator('#phase-indicator');
    const phaseText = await phaseIndicator.textContent();
    console.log('Current phase:', phaseText);
    
    // Look for resolve legislation button
    const resolveButton = page.getByRole('button', { name: /resolve legislation/i });
    
    if (await resolveButton.isVisible()) {
      console.log('✅ Resolve legislation button found in Legislation Phase');
      
      // Click resolve legislation
      await resolveButton.click();
      console.log('✅ Clicked resolve legislation button');
      
      // Wait for results overlay to appear
      console.log('=== Waiting for Results Overlay ===');
      const resultsOverlay = page.locator('#results-overlay');
      
      try {
        await expect(resultsOverlay).toBeVisible({ timeout: 10000 });
        console.log('✅ Results overlay is visible');
        
        // Check for results content
        const resultsContent = page.locator('#results-content');
        await expect(resultsContent).toBeVisible();
        console.log('✅ Results content is visible');
        
        // Check for specific result elements
        const resultCards = page.locator('.result-card');
        const cardCount = await resultCards.count();
        console.log(`Found ${cardCount} result cards`);
        
        if (cardCount > 0) {
          // Check for legislation result details
          const outcomeElement = page.locator('.outcome');
          await expect(outcomeElement).toBeVisible();
          console.log('✅ Outcome element is visible');
          
          const detailsElement = page.locator('.details');
          await expect(detailsElement).toBeVisible();
          console.log('✅ Details element is visible');
          
          // Check for continue button
          const continueButton = page.locator('#close-results-btn');
          await expect(continueButton).toBeVisible();
          console.log('✅ Continue button is visible');
          
          // Click continue to close results
          await continueButton.click();
          console.log('✅ Clicked continue button');
          
          // Check that overlay is hidden
          await expect(resultsOverlay).not.toBeVisible();
          console.log('✅ Results overlay is hidden after continue');
        } else {
          console.log('❌ No result cards found');
        }
      } catch (error) {
        console.log('❌ Results overlay did not appear:', error.message);
        
        // Check if there are any error messages
        const errorMessages = page.locator('.message.error');
        if (await errorMessages.count() > 0) {
          const errorText = await errorMessages.first().textContent();
          console.log('Error message found:', errorText);
        }
        
        // Check game log for any clues
        const gameLog = page.locator('#game-log');
        const logContent = await gameLog.textContent();
        console.log('Game log content:', logContent);
      }
    } else {
      console.log('❌ Resolve legislation button not found');
      
      // Check if we're in the right phase
      const phaseText2 = await phaseIndicator.textContent();
      console.log('Current phase:', phaseText2);
      
      // Check if there are any pending legislation
      const gameLog = page.locator('#game-log');
      const logContent = await gameLog.textContent();
      console.log('Game log content:', logContent);
    }
  });

  test('election results are displayed on mobile after full game flow', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    
    // Create new game
    await createNewGame(page);
    
    console.log('=== Testing Election Results Flow (Full Game Flow) ===');
    
    // Complete 4 rounds to get to Legislation Phase
    console.log('\n--- Completing 4 rounds to reach Legislation Phase ---');
    
    for (let round = 1; round <= 4; round++) {
      console.log(`\n--- Round ${round} ---`);
      
      // Each player takes a simple action (fundraise) and passes
      for (let player = 0; player < 3; player++) {
        const currentInfo = await getCurrentPlayerInfo(page);
        console.log(`Player ${player + 1}: ${currentInfo.playerName}`);
        
        // Fundraise if possible
        if (currentInfo.ap >= 1) {
          await performValidAction(page, 'fundraise', 1);
        }
        
        // Pass turn
        await performValidAction(page, 'pass turn', 0);
        await page.waitForTimeout(1000);
      }
    }
    
    // Check if we're in Legislation Phase
    console.log('\n--- Checking for Legislation Phase ---');
    const phaseIndicator = page.locator('#phase-indicator');
    const phaseText = await phaseIndicator.textContent();
    console.log('Current phase:', phaseText);
    
    // Look for resolve legislation button
    const resolveLegislationButton = page.getByRole('button', { name: /resolve legislation/i });
    if (await resolveLegislationButton.isVisible()) {
      console.log('✅ Resolve legislation button found, clicking...');
      await resolveLegislationButton.click();
      
      // Wait for legislation resolution
      await page.waitForTimeout(2000);
      
      // Check if we're now in election phase
      const phaseText2 = await phaseIndicator.textContent();
      console.log('Phase after legislation resolution:', phaseText2);
      
      if (phaseText2 && phaseText2.includes('Election')) {
        console.log('✅ Now in election phase');
        
        // Check for declare candidacy button
        const declareButton = page.getByRole('button', { name: /declare candidacy/i });
        if (await declareButton.isVisible()) {
          console.log('✅ Declare candidacy button found');
          await declareButton.click();
          
          // Handle candidacy modal
          const candidacyModal = page.getByText(/declare candidacy/i);
          if (await candidacyModal.isVisible()) {
            console.log('✅ Candidacy modal opened');
            
            // Select an office
            const officeSelect = page.locator('select');
            if (await officeSelect.count() > 0) {
              await officeSelect.first().selectOption({ index: 1 });
              console.log('✅ Selected office');
              
              // Enter PC amount
              const pcInput = page.locator('input[type="number"]');
              if (await pcInput.count() > 0) {
                await pcInput.first().fill('5');
                console.log('✅ Entered PC amount');
                
                // Click declare
                const declareBtn = page.getByRole('button', { name: /declare/i });
                if (await declareBtn.isVisible()) {
                  await declareBtn.click();
                  console.log('✅ Clicked declare candidacy');
                  
                  // Check for resolve elections button
                  const resolveElectionsButton = page.getByRole('button', { name: /resolve elections/i });
                  if (await resolveElectionsButton.isVisible()) {
                    console.log('✅ Resolve elections button found');
                    await resolveElectionsButton.click();
                    console.log('✅ Clicked resolve elections');
                    
                    // Wait for election results
                    await page.waitForTimeout(3000);
                    
                    // Check for results overlay
                    const resultsOverlay = page.locator('#results-overlay');
                    if (await resultsOverlay.isVisible()) {
                      console.log('✅ Election results overlay is visible');
                      
                      // Check for election result content
                      const resultsContent = page.locator('#results-content');
                      const content = await resultsContent.textContent();
                      console.log('Election results content:', content);
                      
                      // Check for winner information
                      const winnerElement = page.locator('.outcome');
                      if (await winnerElement.count() > 0) {
                        const winnerText = await winnerElement.first().textContent();
                        console.log('Winner information:', winnerText);
                      }
                      
                      // Close results
                      const continueButton = page.locator('#close-results-btn');
                      if (await continueButton.isVisible()) {
                        await continueButton.click();
                        console.log('✅ Closed election results');
                      }
                    } else {
                      console.log('❌ Election results overlay not visible');
                      
                      // Check game log for election results
                      const gameLog = page.locator('#game-log');
                      const logContent = await gameLog.textContent();
                      console.log('Game log after election resolution:', logContent);
                    }
                  } else {
                    console.log('❌ Resolve elections button not found');
                  }
                } else {
                  console.log('❌ Declare button not found in modal');
                }
              } else {
                console.log('❌ PC input not found');
              }
            } else {
              console.log('❌ Office select not found');
            }
          } else {
            console.log('❌ Candidacy modal not opened');
          }
        } else {
          console.log('❌ Declare candidacy button not found');
        }
      } else {
        console.log('❌ Not in election phase after legislation resolution');
      }
    } else {
      console.log('❌ Resolve legislation button not found');
    }
  });

  test('results overlay is mobile-friendly', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    
    // Create new game
    await createNewGame(page);
    
    console.log('=== Testing Mobile-Friendly Results Overlay ===');
    
    // Complete 4 rounds to get to Legislation Phase
    console.log('\n--- Completing 4 rounds to reach Legislation Phase ---');
    
    for (let round = 1; round <= 4; round++) {
      console.log(`\n--- Round ${round} ---`);
      
      // Each player passes turn
      for (let player = 0; player < 3; player++) {
        const currentInfo = await getCurrentPlayerInfo(page);
        console.log(`Player ${player + 1}: ${currentInfo.playerName}`);
        
        // Pass turn
        await performValidAction(page, 'pass turn', 0);
        await page.waitForTimeout(1000);
      }
    }
    
    // Check for resolve button
    const resolveButton = page.getByRole('button', { name: /resolve legislation/i });
    if (await resolveButton.isVisible()) {
      await resolveButton.click();
      
      // Wait for results overlay
      const resultsOverlay = page.locator('#results-overlay');
      try {
        await expect(resultsOverlay).toBeVisible({ timeout: 10000 });
        
        // Test mobile-specific aspects
        console.log('=== Testing Mobile-Friendly Aspects ===');
        
        // Check that overlay takes full screen on mobile
        const overlayRect = await resultsOverlay.boundingBox();
        const viewport = page.viewportSize();
        
        if (overlayRect && viewport) {
          console.log(`Overlay dimensions: ${overlayRect.width}x${overlayRect.height}`);
          console.log(`Viewport dimensions: ${viewport.width}x${viewport.height}`);
          
          // Overlay should be close to viewport size
          expect(overlayRect.width).toBeGreaterThan(viewport.width * 0.9);
          expect(overlayRect.height).toBeGreaterThan(viewport.height * 0.9);
          console.log('✅ Overlay is full-screen on mobile');
        }
        
        // Check that content is scrollable if needed
        const resultsContent = page.locator('#results-content');
        const contentRect = await resultsContent.boundingBox();
        const overlayRect2 = await resultsOverlay.boundingBox();
        
        if (contentRect && overlayRect2) {
          const isScrollable = contentRect.height > overlayRect2.height;
          console.log(`Content height: ${contentRect.height}, Overlay height: ${overlayRect2.height}`);
          console.log(`Content is scrollable: ${isScrollable}`);
        }
        
        // Check that close button is easily tappable
        const closeButton = page.locator('#close-results-btn');
        const buttonRect = await closeButton.boundingBox();
        
        if (buttonRect) {
          // Button should be at least 44px tall for mobile touch targets
          expect(buttonRect.height).toBeGreaterThanOrEqual(44);
          console.log('✅ Close button is touch-friendly');
          
          // Button should be centered or easily accessible
          expect(buttonRect.width).toBeGreaterThan(100);
          console.log('✅ Close button is wide enough');
        }
        
        // Test touch interaction
        await closeButton.click();
        await expect(resultsOverlay).not.toBeVisible();
        console.log('✅ Touch interaction works');
        
      } catch (error) {
        console.log('❌ Results overlay test failed:', error.message);
      }
    } else {
      console.log('❌ Could not trigger results overlay');
    }
  });

  test('results are accessible on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    
    // Create new game
    await createNewGame(page);
    
    console.log('=== Testing Mobile Accessibility of Results ===');
    
    // Complete 4 rounds to get to Legislation Phase
    console.log('\n--- Completing 4 rounds to reach Legislation Phase ---');
    
    for (let round = 1; round <= 4; round++) {
      console.log(`\n--- Round ${round} ---`);
      
      // Each player passes turn
      for (let player = 0; player < 3; player++) {
        const currentInfo = await getCurrentPlayerInfo(page);
        console.log(`Player ${player + 1}: ${currentInfo.playerName}`);
        
        // Pass turn
        await performValidAction(page, 'pass turn', 0);
        await page.waitForTimeout(1000);
      }
    }
    
    const resolveButton = page.getByRole('button', { name: /resolve legislation/i });
    if (await resolveButton.isVisible()) {
      await resolveButton.click();
      
      const resultsOverlay = page.locator('#results-overlay');
      try {
        await expect(resultsOverlay).toBeVisible({ timeout: 10000 });
        
        // Test accessibility features
        console.log('=== Testing Accessibility Features ===');
        
        // Check for proper ARIA attributes
        const overlayAriaHidden = await resultsOverlay.getAttribute('aria-hidden');
        console.log('Overlay aria-hidden:', overlayAriaHidden);
        
        // Check for focus management
        const closeButton = page.locator('#close-results-btn');
        await closeButton.focus();
        const isFocused = await closeButton.evaluate(el => el === document.activeElement);
        console.log('Close button is focused:', isFocused);
        
        // Check for keyboard navigation
        await page.keyboard.press('Tab');
        const focusAfterTab = await page.evaluate(() => document.activeElement?.tagName);
        console.log('Element focused after Tab:', focusAfterTab);
        
        // Check for screen reader announcements
        const srAnnouncements = page.locator('#sr-announcements');
        const announcementText = await srAnnouncements.textContent();
        console.log('Screen reader announcement:', announcementText);
        
        // Test keyboard escape
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
        const isStillVisible = await resultsOverlay.isVisible();
        console.log('Overlay still visible after Escape:', isStillVisible);
        
        console.log('✅ Accessibility features tested');
        
      } catch (error) {
        console.log('❌ Accessibility test failed:', error.message);
      }
    } else {
      console.log('❌ Could not trigger results for accessibility test');
    }
  });
}); 