import { test, expect } from '@playwright/test';
import { 
  getCurrentPlayerInfo, 
  performValidAction, 
  createNewGame 
} from './tests/test-utils';

test('Debug sponsor legislation flow', async ({ page }) => {
  // Create new game
  await createNewGame(page);

  // Check current player and state
  console.log('=== Initial State ===');
  const { playerName: currentPlayer, ap: currentAP, pc: currentPC } = await getCurrentPlayerInfo(page);
  console.log('Current player:', currentPlayer);
  console.log('Current AP:', currentAP);
  console.log('Current PC:', currentPC);

  // Wait a bit and check again
  await page.waitForTimeout(2000);
  const { playerName: currentPlayer2, ap: currentAP2, pc: currentPC2 } = await getCurrentPlayerInfo(page);
  console.log('Current player after 2s:', currentPlayer2);
  console.log('Current AP after 2s:', currentAP2);
  console.log('Current PC after 2s:', currentPC2);

  // Try to sponsor legislation with validation
  console.log('=== Attempting Sponsor Legislation ===');
  const sponsorSuccess = await performValidAction(page, 'sponsor legislation', 2);
  
  if (sponsorSuccess) {
    console.log('✅ Sponsor legislation action was successful');
    
    // Wait for modal
    await expect(page.getByText('Choose legislation to sponsor:')).toBeVisible();
    console.log('Modal opened');
    
    // Click on Infrastructure Bill
    await page.getByRole('button', { name: /infrastructure/i }).click();
    console.log('Clicked Infrastructure Bill');
    
    // Check log for sponsored message
    await page.waitForTimeout(2000);
    const logContent = await page.locator('#game-log').textContent();
    console.log('Log content:', logContent);
    
    // Check if sponsored appears in log
    if (logContent && logContent.includes('sponsored')) {
      console.log('✅ Found "sponsored" in log');
    } else {
      console.log('❌ "sponsored" not found in log');
    }
  } else {
    console.log('❌ Sponsor legislation action was not available or failed');
  }
}); 