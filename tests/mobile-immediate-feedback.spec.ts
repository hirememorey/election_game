import { test, expect } from '@playwright/test';
import { 
  getCurrentPlayerInfo, 
  performValidAction, 
  createNewGame,
  handleSponsorLegislationModal
} from './test-utils';

test.describe('Mobile Immediate Feedback Tests', () => {
  test('mobile users expect immediate results after sponsoring legislation', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    
    // Create new game
    await createNewGame(page);
    
    console.log('=== Testing Mobile User Expectations ===');
    
    // Step 1: Alice sponsors legislation
    console.log('\n--- Step 1: Alice sponsors legislation ---');
    await expect(page.locator('#phase-indicator .player-name').getByText('Alice')).toBeVisible();
    await performValidAction(page, 'sponsor legislation', 2);
    await handleSponsorLegislationModal(page);
    
    // Check what the user sees
    console.log('\n--- What the user sees ---');
    const gameLog = page.locator('#game-log');
    const logContent = await gameLog.textContent();
    console.log('Game log after sponsoring:', logContent);
    
    // Check if there are any result indicators
    const resultIndicators = page.locator('.result, .outcome, .legislation-result');
    const indicatorCount = await resultIndicators.count();
    console.log(`Found ${indicatorCount} result indicators`);
    
    // Check if there are any pending legislation displays
    const pendingLegislation = page.locator('.pending-legislation, .legislation-card');
    const pendingCount = await pendingLegislation.count();
    console.log(`Found ${pendingCount} pending legislation displays`);
    
    // Check if there are any vote indicators
    const voteIndicators = page.locator('.vote-count, .support-count, .opposition-count');
    const voteCount = await voteIndicators.count();
    console.log(`Found ${voteCount} vote indicators`);
    
    // Step 2: Check if user can see what they just sponsored
    console.log('\n--- Step 2: Checking for legislation details ---');
    
    // Look for any legislation information
    const legislationInfo = page.locator('*').filter({ hasText: /legislation|bill|sponsored/i });
    const infoCount = await legislationInfo.count();
    console.log(`Found ${infoCount} elements with legislation info`);
    
    if (infoCount > 0) {
      for (let i = 0; i < Math.min(infoCount, 5); i++) {
        const text = await legislationInfo.nth(i).textContent();
        console.log(`Legislation info ${i + 1}:`, text?.substring(0, 100));
      }
    }
    
    // Step 3: Check if there are any action buttons for the sponsored legislation
    console.log('\n--- Step 3: Checking for follow-up actions ---');
    
    const actionButtons = page.locator('button').filter({ hasText: /support|oppose|vote|legislation/i });
    const buttonCount = await actionButtons.count();
    console.log(`Found ${buttonCount} legislation-related action buttons`);
    
    if (buttonCount > 0) {
      for (let i = 0; i < buttonCount; i++) {
        const buttonText = await actionButtons.nth(i).textContent();
        const isVisible = await actionButtons.nth(i).isVisible();
        console.log(`Button ${i + 1}: "${buttonText}" (visible: ${isVisible})`);
      }
    }
    
    // Step 4: Check current player and available actions
    console.log('\n--- Step 4: Current game state ---');
    const currentInfo = await getCurrentPlayerInfo(page);
    console.log('Current player:', currentInfo);
    
    // Check what actions are available
    const allButtons = page.locator('button');
    const visibleButtons = await allButtons.filter({ hasText: /.+/ }).all();
    console.log(`Found ${visibleButtons.length} visible buttons`);
    
    for (let i = 0; i < Math.min(visibleButtons.length, 10); i++) {
      const buttonText = await visibleButtons[i].textContent();
      console.log(`Button ${i + 1}: "${buttonText}"`);
    }
    
    // Analysis: What mobile users expect vs what they get
    console.log('\n=== ANALYSIS: Mobile User Experience ===');
    console.log('❌ PROBLEM: Mobile users expect immediate feedback');
    console.log('✅ EXPECTED: "Legislation sponsored! Current votes: 0 support, 0 oppose"');
    console.log('❌ ACTUAL: Just "Alice sponsored the Protect The Children!"');
    console.log('❌ PROBLEM: No indication of what happens next');
    console.log('✅ EXPECTED: "Other players can now support or oppose this legislation"');
    console.log('❌ ACTUAL: No clear next steps shown');
    console.log('❌ PROBLEM: No visual indication of pending legislation');
    console.log('✅ EXPECTED: Clear display of sponsored legislation with vote status');
    console.log('❌ ACTUAL: Legislation info buried in game log');
  });

  test('mobile users need clear phase indicators', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    
    // Create new game
    await createNewGame(page);
    
    console.log('=== Testing Mobile Phase Indicators ===');
    
    // Check current phase display
    const phaseIndicator = page.locator('#phase-indicator');
    const phaseText = await phaseIndicator.textContent();
    console.log('Current phase display:', phaseText);
    
    // Check if phase is clearly visible on mobile
    const phaseRect = await phaseIndicator.boundingBox();
    const viewport = page.viewportSize();
    
    if (phaseRect && viewport) {
      console.log(`Phase indicator dimensions: ${phaseRect.width}x${phaseRect.height}`);
      console.log(`Viewport dimensions: ${viewport.width}x${viewport.height}`);
      
      // Check if phase indicator is prominent enough
      const isProminent = phaseRect.height > 50 && phaseRect.width > viewport.width * 0.8;
      console.log('Phase indicator is prominent:', isProminent);
    }
    
    // Check for phase-specific styling
    const phaseClasses = await phaseIndicator.getAttribute('class');
    console.log('Phase indicator classes:', phaseClasses);
    
    // Check if there are any phase transition indicators
    const transitionIndicators = page.locator('*').filter({ hasText: /next phase|phase change|round/i });
    const transitionCount = await transitionIndicators.count();
    console.log(`Found ${transitionCount} phase transition indicators`);
    
    // Analysis: Phase indicator issues
    console.log('\n=== ANALYSIS: Phase Indicator Issues ===');
    console.log('❌ PROBLEM: Phase not clearly indicated on mobile');
    console.log('✅ EXPECTED: Large, clear "Action Phase - Round 1" display');
    console.log('❌ ACTUAL: Small text that may be hard to read on mobile');
    console.log('❌ PROBLEM: No indication of when phases will change');
    console.log('✅ EXPECTED: "3 more rounds until Legislation Phase"');
    console.log('❌ ACTUAL: No countdown or progress indicator');
  });

  test('mobile users need touch-friendly result interactions', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    
    // Create new game
    await createNewGame(page);
    
    console.log('=== Testing Mobile Touch Interactions ===');
    
    // Check all interactive elements for mobile-friendliness
    const interactiveElements = page.locator('button, input, select, a[href]');
    const elementCount = await interactiveElements.count();
    console.log(`Found ${elementCount} interactive elements`);
    
    let touchFriendlyCount = 0;
    let smallTouchTargets = 0;
    
    for (let i = 0; i < Math.min(elementCount, 20); i++) {
      const element = interactiveElements.nth(i);
      const rect = await element.boundingBox();
      
      if (rect) {
        const isTouchFriendly = rect.height >= 44 && rect.width >= 44;
        const isSmall = rect.height < 44 || rect.width < 44;
        
        if (isTouchFriendly) touchFriendlyCount++;
        if (isSmall) smallTouchTargets++;
        
        const elementText = await element.textContent();
        console.log(`Element ${i + 1}: "${elementText}" - ${rect.width}x${rect.height} (touch-friendly: ${isTouchFriendly})`);
      }
    }
    
    console.log(`\nTouch-friendly elements: ${touchFriendlyCount}/${Math.min(elementCount, 20)}`);
    console.log(`Small touch targets: ${smallTouchTargets}/${Math.min(elementCount, 20)}`);
    
    // Analysis: Touch interaction issues
    console.log('\n=== ANALYSIS: Touch Interaction Issues ===');
    console.log('❌ PROBLEM: Some touch targets may be too small');
    console.log('✅ EXPECTED: All buttons at least 44x44px for mobile');
    console.log('❌ ACTUAL: Some elements may be smaller than recommended');
    console.log('❌ PROBLEM: No clear indication of tappable elements');
    console.log('✅ EXPECTED: Visual feedback for touchable elements');
    console.log('❌ ACTUAL: May not be obvious what can be tapped');
  });
}); 