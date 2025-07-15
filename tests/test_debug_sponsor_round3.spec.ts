import { test, expect } from '@playwright/test';

test('Debug sponsor legislation in Round 3 with pending legislation', async ({ page }) => {
  await page.goto('http://localhost:5001');

  // Create game
  await page.getByLabel('Player 1').fill('Alice');
  await page.getByLabel('Player 2').fill('Bob');
  await page.getByRole('button', { name: /start game/i }).click();

  // Wait for game to start
  await expect(page.locator('#phase-indicator').getByText(/Action Phase/i)).toBeVisible();

  // Simulate multiple rounds to get to Round 3 with pending legislation
  console.log('=== Simulating multiple rounds ===');
  
  // Round 1: Alice sponsors legislation
  console.log('Round 1: Alice sponsors legislation');
  await page.getByRole('button', { name: /sponsor legislation/i }).click();
  await page.getByRole('button', { name: /infrastructure/i }).click();
  await expect(page.locator('#game-log').getByText(/sponsored/i)).toBeVisible();
  
  // Wait for Bob's turn
  await expect(page.locator('#phase-indicator .player-name').getByText('Bob')).toBeVisible();
  
  // Bob passes turn
  console.log('Round 1: Bob passes turn');
  await page.getByRole('button', { name: /pass turn/i }).click();
  
  // Wait for Alice's turn again
  await expect(page.locator('#phase-indicator .player-name').getByText('Alice')).toBeVisible();
  
  // Round 2: Alice passes turn
  console.log('Round 2: Alice passes turn');
  await page.getByRole('button', { name: /pass turn/i }).click();
  
  // Wait for Bob's turn
  await expect(page.locator('#phase-indicator .player-name').getByText('Bob')).toBeVisible();
  
  // Bob passes turn
  console.log('Round 2: Bob passes turn');
  await page.getByRole('button', { name: /pass turn/i }).click();
  
  // Wait for Alice's turn in Round 3
  await expect(page.locator('#phase-indicator .player-name').getByText('Alice')).toBeVisible();
  
  // Log the current game state in Round 3
  console.log('\n=== Round 3 Game State ===');
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

  // Try to sponsor legislation in Round 3 (should work even with pending legislation)
  console.log('\n=== Trying Sponsor Legislation in Round 3 ===');
  const sponsorBtn = page.getByRole('button', { name: /sponsor legislation/i });
  console.log('Sponsor button visible:', await sponsorBtn.isVisible());
  
  if (await sponsorBtn.isVisible()) {
    await sponsorBtn.click();
    
    // Wait for modal to appear
    console.log('\n=== Waiting for Modal ===');
    await expect(page.getByText('Choose legislation to sponsor:')).toBeVisible();
    
    // Click infrastructure button (cheaper than healthcare)
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
  } else {
    console.log('Sponsor legislation button not available in Round 3');
  }
}); 