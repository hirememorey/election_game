import { test, expect } from '@playwright/test';

test('Debug sponsor legislation with detailed logging', async ({ page }) => {
  await page.goto('http://localhost:5001');

  // Create game
  await page.getByLabel('Player 1').fill('Alice');
  await page.getByLabel('Player 2').fill('Bob');
  await page.getByRole('button', { name: /start game/i }).click();

  // Wait for game to start
  await expect(page.locator('#phase-indicator').getByText(/Action Phase/i)).toBeVisible();

  // Log the current game state
  console.log('=== Current Game State ===');
  const phaseText = await page.locator('#phase-indicator').textContent();
  console.log('Phase:', phaseText);
  
  const logText = await page.locator('#game-log').textContent();
  console.log('Game Log:', logText);
  
  const actionButtons = await page.locator('.action-btn').all();
  console.log('Available Actions:', actionButtons.length);
  for (const button of actionButtons) {
    const buttonText = await button.textContent();
    console.log('  -', buttonText);
  }

  // Click sponsor legislation button
  console.log('\n=== Clicking Sponsor Legislation ===');
  const sponsorBtn = page.getByRole('button', { name: /sponsor legislation/i });
  console.log('Sponsor button visible:', await sponsorBtn.isVisible());
  await sponsorBtn.click();
  
  // Wait for modal to appear
  console.log('\n=== Waiting for Modal ===');
  await expect(page.getByText('Choose legislation to sponsor:')).toBeVisible();
  
  // Log available legislation options
  const legislationButtons = await page.locator('.action-btn').all();
  console.log('Legislation Options:', legislationButtons.length);
  for (const button of legislationButtons) {
    const buttonText = await button.textContent();
    console.log('  -', buttonText);
  }
  
  // Click infrastructure button
  console.log('\n=== Clicking Infrastructure ===');
  const infrastructureBtn = page.getByRole('button', { name: /infrastructure/i });
  console.log('Infrastructure button visible:', await infrastructureBtn.isVisible());
  await infrastructureBtn.click();
  
  // Wait for log to update
  console.log('\n=== Waiting for Log Update ===');
  await expect(page.locator('#game-log').getByText(/sponsored/i)).toBeVisible();
  
  // Log final state
  console.log('\n=== Final Game State ===');
  const finalLogText = await page.locator('#game-log').textContent();
  console.log('Final Game Log:', finalLogText);
  
  console.log('Test completed successfully!');
}); 