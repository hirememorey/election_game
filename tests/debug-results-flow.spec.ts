import { test, expect } from '@playwright/test';
import { 
  getCurrentPlayerInfo, 
  performValidAction, 
  createNewGame,
  handleSponsorLegislationModal,
  handleLegislationCommitmentModal
} from './test-utils';

test.describe('Debug Results Flow', () => {
  test('debug legislation flow step by step', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    
    // Create new game
    await createNewGame(page);
    
    console.log('=== Debug: Legislation Flow Step by Step ===');
    
    // Step 1: Alice sponsors legislation
    console.log('\n--- Step 1: Alice sponsors legislation ---');
    const aliceInfo = await getCurrentPlayerInfo(page);
    console.log('Alice info:', aliceInfo);
    
    await expect(page.locator('#phase-indicator .player-name').getByText('Alice')).toBeVisible();
    await performValidAction(page, 'sponsor legislation', 2);
    await handleSponsorLegislationModal(page);
    
    // Check what happened after Alice's action
    console.log('\n--- After Alice\'s action ---');
    const afterAliceInfo = await getCurrentPlayerInfo(page);
    console.log('Current player after Alice:', afterAliceInfo);
    
    // Check game log
    const gameLog = page.locator('#game-log');
    const logContent = await gameLog.textContent();
    console.log('Game log after Alice:', logContent);
    
    // Check if resolve button appeared
    const resolveButton = page.getByRole('button', { name: /resolve legislation/i });
    console.log('Resolve button visible:', await resolveButton.isVisible());
    
    // Step 2: Bob's turn
    console.log('\n--- Step 2: Bob\'s turn ---');
    const bobInfo = await getCurrentPlayerInfo(page);
    console.log('Bob info:', bobInfo);
    
    if (bobInfo.playerName === 'Bob') {
      console.log('✅ Bob is current player');
      
      // Try to support legislation
      await performValidAction(page, 'support', 1, 5);
      await handleLegislationCommitmentModal(page, 'support', 5);
      
      // Check what happened after Bob's action
      console.log('\n--- After Bob\'s action ---');
      const afterBobInfo = await getCurrentPlayerInfo(page);
      console.log('Current player after Bob:', afterBobInfo);
      
      // Check game log
      const logContent2 = await gameLog.textContent();
      console.log('Game log after Bob:', logContent2);
      
      // Check if resolve button appeared
      console.log('Resolve button visible after Bob:', await resolveButton.isVisible());
      
      // Step 3: Charlie's turn
      console.log('\n--- Step 3: Charlie\'s turn ---');
      const charlieInfo = await getCurrentPlayerInfo(page);
      console.log('Charlie info:', charlieInfo);
      
      if (charlieInfo.playerName === 'Charlie') {
        console.log('✅ Charlie is current player');
        
        // Try to oppose legislation
        await performValidAction(page, 'oppose', 1, 3);
        await handleLegislationCommitmentModal(page, 'oppose', 3);
        
        // Check what happened after Charlie's action
        console.log('\n--- After Charlie\'s action ---');
        const afterCharlieInfo = await getCurrentPlayerInfo(page);
        console.log('Current player after Charlie:', afterCharlieInfo);
        
        // Check game log
        const logContent3 = await gameLog.textContent();
        console.log('Game log after Charlie:', logContent3);
        
        // Check if resolve button appeared
        console.log('Resolve button visible after Charlie:', await resolveButton.isVisible());
        
        // If resolve button is visible, try to click it
        if (await resolveButton.isVisible()) {
          console.log('✅ Resolve button is visible, clicking...');
          await resolveButton.click();
          
          // Wait for results overlay
          const resultsOverlay = page.locator('#results-overlay');
          try {
            await expect(resultsOverlay).toBeVisible({ timeout: 10000 });
            console.log('✅ Results overlay appeared!');
            
            // Check results content
            const resultsContent = page.locator('#results-content');
            const content = await resultsContent.textContent();
            console.log('Results content:', content);
            
          } catch (error) {
            console.log('❌ Results overlay did not appear:', error.message);
          }
        } else {
          console.log('❌ Resolve button still not visible');
          
          // Check if we're in the right phase
          const phaseIndicator = page.locator('#phase-indicator');
          const phaseText = await phaseIndicator.textContent();
          console.log('Current phase:', phaseText);
        }
      } else {
        console.log('❌ Charlie is not current player, got:', charlieInfo.playerName);
      }
    } else {
      console.log('❌ Bob is not current player, got:', bobInfo.playerName);
    }
  });

  test('debug why resolve button doesn\'t appear', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    
    // Create new game
    await createNewGame(page);
    
    console.log('=== Debug: Why Resolve Button Doesn\'t Appear ===');
    
    // Alice sponsors legislation
    await expect(page.locator('#phase-indicator .player-name').getByText('Alice')).toBeVisible();
    await performValidAction(page, 'sponsor legislation', 2);
    await handleSponsorLegislationModal(page);
    
    // Check game state
    console.log('\n--- Checking Game State ---');
    
    // Check if there's pending legislation
    const gameLog = page.locator('#game-log');
    const logContent = await gameLog.textContent();
    console.log('Game log:', logContent);
    
    // Check if we're in legislation phase
    const phaseIndicator = page.locator('#phase-indicator');
    const phaseText = await phaseIndicator.textContent();
    console.log('Phase indicator:', phaseText);
    
    // Check if resolve controls are visible
    const resolutionControls = page.locator('#resolution-controls');
    const controlsVisible = await resolutionControls.isVisible();
    console.log('Resolution controls visible:', controlsVisible);
    
    if (controlsVisible) {
      const controlsText = await resolutionControls.textContent();
      console.log('Resolution controls text:', controlsText);
    }
    
    // Check if there are any buttons in the action area
    const actionArea = page.locator('#action-area');
    const buttons = await actionArea.locator('button').all();
    console.log(`Found ${buttons.length} buttons in action area`);
    
    for (let i = 0; i < buttons.length; i++) {
      const buttonText = await buttons[i].textContent();
      const buttonVisible = await buttons[i].isVisible();
      console.log(`Button ${i}: "${buttonText}" (visible: ${buttonVisible})`);
    }
    
    // Check if we need to advance to legislation phase
    console.log('\n--- Checking if we need to advance phases ---');
    
    // Try to pass turns to get to legislation phase
    for (let i = 0; i < 3; i++) {
      const currentInfo = await getCurrentPlayerInfo(page);
      console.log(`Turn ${i + 1}: ${currentInfo.playerName} (AP: ${currentInfo.ap})`);
      
      if (currentInfo.ap > 0) {
        await performValidAction(page, 'pass turn', 0);
        await page.waitForTimeout(1000);
      } else {
        console.log('No AP left, turn should advance automatically');
        await page.waitForTimeout(1000);
      }
    }
    
    // Check final state
    const finalInfo = await getCurrentPlayerInfo(page);
    console.log('Final player:', finalInfo);
    
    const finalPhase = await phaseIndicator.textContent();
    console.log('Final phase:', finalPhase);
    
    const finalLog = await gameLog.textContent();
    console.log('Final game log:', finalLog);
  });
}); 