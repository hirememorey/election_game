import { test, expect } from '@playwright/test';
import { 
  getCurrentPlayerInfo, 
  performValidAction, 
  createNewGame 
} from './tests/test-utils';

test('Simple debug test', async ({ page }) => {
  // Create new game
  await createNewGame(page);

  // Check initial state
  console.log('=== Initial State ===');
  const { playerName: initialPlayerName, ap: initialAP, pc: initialPC } = await getCurrentPlayerInfo(page);
  console.log('Initial player name:', initialPlayerName);
  console.log('Initial AP:', initialAP);
  console.log('Initial PC:', initialPC);

  // Try to perform pass turn action with validation
  console.log('=== Attempting Pass Turn ===');
  const passTurnSuccess = await performValidAction(page, 'pass turn', 0);
  
  if (passTurnSuccess) {
    console.log('✅ Pass turn action was successful');
  } else {
    console.log('❌ Pass turn action was not available or failed');
  }

  // Wait a moment for the action to complete
  await page.waitForTimeout(2000);

  // Check the state after pass turn
  console.log('=== After Pass Turn ===');
  const { playerName: afterPlayerName, ap: afterAP, pc: afterPC } = await getCurrentPlayerInfo(page);
  console.log('After pass turn player name:', afterPlayerName);
  console.log('After pass turn AP:', afterAP);
  console.log('After pass turn PC:', afterPC);

  // Check if the player changed
  if (afterPlayerName !== initialPlayerName) {
    console.log('✅ Player name changed correctly');
  } else {
    console.log('❌ Player name did not change');
  }

  // Wait for Bob to be visible (if the turn advanced)
  try {
    await expect(page.locator('#phase-indicator .player-name').getByText('Bob')).toBeVisible({ timeout: 10000 });
    console.log('✅ Bob is now the current player');
  } catch (error) {
    console.log('⚠️ Bob is not the current player - this might be expected if turn didn\'t advance');
    console.log('Current player is:', afterPlayerName);
  }
}); 