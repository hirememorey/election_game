import { test, expect } from '@playwright/test';

test('Simple debug test', async ({ page }) => {
  await page.goto('http://localhost:5001');

  // Create game
  await page.getByLabel('Player 1').fill('Alice');
  await page.getByLabel('Player 2').fill('Bob');
  await page.getByLabel('Player 3').fill('Charlie');
  await page.getByRole('button', { name: /start game/i }).click();

  // Wait for game to start
  await expect(page.locator('#phase-indicator').getByText(/Action Phase/i)).toBeVisible();

  // Check initial state
  console.log('=== Initial State ===');
  const initialPlayerName = await page.locator('#phase-indicator .player-name').textContent();
  console.log('Initial player name:', initialPlayerName);

  // Click pass turn button
  console.log('=== Clicking Pass Turn ===');
  const passBtn = page.getByRole('button', { name: /pass turn/i });
  await expect(passBtn).toBeVisible();
  await passBtn.click();

  // Wait a moment for the action to complete
  await page.waitForTimeout(2000);

  // Check the state after pass turn
  console.log('=== After Pass Turn ===');
  const afterPlayerName = await page.locator('#phase-indicator .player-name').textContent();
  console.log('After pass turn player name:', afterPlayerName);

  // Check if the player changed
  if (afterPlayerName !== initialPlayerName) {
    console.log('✅ Player name changed correctly');
  } else {
    console.log('❌ Player name did not change');
  }

  // Wait for Bob to be visible
  await expect(page.locator('#phase-indicator .player-name').getByText('Bob')).toBeVisible({ timeout: 10000 });
  console.log('✅ Bob is now the current player');
}); 