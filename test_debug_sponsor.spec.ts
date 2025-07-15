import { test, expect } from '@playwright/test';

test('Debug sponsor legislation flow', async ({ page }) => {
  await page.goto('http://localhost:5001');

  // Create game
  await page.getByLabel('Player 1').fill('Alice');
  await page.getByLabel('Player 2').fill('Bob');
  await page.getByLabel('Player 3').fill('Charlie');
  await page.getByRole('button', { name: /start game/i }).click();

  // Wait for game to start
  await expect(page.locator('#phase-indicator').getByText(/Action Phase/i)).toBeVisible();

  // Check current player
  const currentPlayer = await page.locator('#phase-indicator .player-name').textContent();
  console.log('Current player:', currentPlayer);

  // Wait a bit and check again
  await page.waitForTimeout(2000);
  const currentPlayer2 = await page.locator('#phase-indicator .player-name').textContent();
  console.log('Current player after 2s:', currentPlayer2);

  // Try to sponsor legislation
  const sponsorBtn = page.getByRole('button', { name: /sponsor legislation/i });
  if (await sponsorBtn.isVisible()) {
    console.log('Sponsor button is visible');
    await sponsorBtn.click();
    
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
    console.log('Sponsor button not visible');
  }
}); 