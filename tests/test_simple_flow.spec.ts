import { test, expect } from '@playwright/test';

test('Simple game flow test', async ({ page }) => {
  await page.goto('http://localhost:5001');

  // Create game
  await page.getByLabel('Player 1').fill('Alice');
  await page.getByLabel('Player 2').fill('Bob');
  await page.getByLabel('Player 3').fill('Charlie');
  await page.getByRole('button', { name: /start game/i }).click();

  // Wait for game to start
  await expect(page.locator('#phase-indicator').getByText(/Action Phase/i)).toBeVisible();

  // Alice's turn: fundraise
  await expect(page.locator('#phase-indicator .player-name').getByText('Alice')).toBeVisible();
  await page.getByRole('button', { name: /fundraise/i }).click();
  await expect(page.locator('#game-log').getByText(/fundraise/i)).toBeVisible();
  // Alice's turn: network
  await expect(page.locator('#phase-indicator .player-name').getByText('Alice')).toBeVisible();
  await page.getByRole('button', { name: /network/i }).click();
  await expect(page.locator('#game-log').getByText(/network/i)).toBeVisible();
  // Should now be Bob's turn
  await expect(page.locator('#phase-indicator .player-name').getByText('Bob')).toBeVisible();
  // Bob's turn: sponsor legislation
  await page.getByRole('button', { name: /sponsor legislation/i }).click();
  await expect(page.getByText('Choose legislation to sponsor:')).toBeVisible();
  const infraBtn = page.getByRole('button', { name: /infrastructure/i });
  if (await infraBtn.isVisible()) {
    await infraBtn.click();
    await expect(page.locator('#game-log').getByText(/sponsored/i)).toBeVisible();
  } else {
    await page.keyboard.press('Escape');
  }
  // Should now be Charlie's turn
  await expect(page.locator('#phase-indicator .player-name').getByText('Charlie')).toBeVisible();
  // Charlie's turn: pass turn
  await page.getByRole('button', { name: /pass turn/i }).click();
  // Should now be Alice's turn again
  await expect(page.locator('#phase-indicator .player-name').getByText('Alice')).toBeVisible();
}); 