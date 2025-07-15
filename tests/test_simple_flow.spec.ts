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

  // Test each player's turn
  for (const player of ['Alice', 'Bob', 'Charlie']) {
    // Wait for correct player turn
    await expect(page.locator('#phase-indicator .player-name').getByText(player)).toBeVisible();
    console.log(`Current player: ${player}`);

    // Try Fundraise (should always be available)
    const fundraiseBtn = page.getByRole('button', { name: /fundraise/i });
    if (await fundraiseBtn.isVisible()) {
      await fundraiseBtn.click();
      await expect(page.locator('#game-log').getByText(/takes the Fundraise action and gains/i)).toBeVisible();
      console.log(`✅ ${player} fundraised successfully`);
    }

    // Try Network (should always be available)
    const networkBtn = page.getByRole('button', { name: /network/i });
    if (await networkBtn.isVisible()) {
      await networkBtn.click();
      await expect(page.locator('#game-log').getByText(/network/i)).toBeVisible();
      console.log(`✅ ${player} networked successfully`);
    }

    // Try Sponsor Legislation (only if they have enough PC)
    const sponsorBtn = page.getByRole('button', { name: /sponsor legislation/i });
    if (await sponsorBtn.isVisible()) {
      await sponsorBtn.click();
      await expect(page.getByText('Choose legislation to sponsor:')).toBeVisible();

      // Parse available PC from the phase indicator
      const phaseText = await page.locator('#phase-indicator').textContent();
      const pcMatch = phaseText && phaseText.match(/PC: (\d+)/);
      const availablePC = pcMatch ? parseInt(pcMatch[1], 10) : 0;
      console.log(`${player} has ${availablePC} PC`);

      // Try to sponsor Infrastructure Bill (5 PC) if affordable
      const infrastructureBtn = page.getByRole('button', { name: /infrastructure/i });
      if (await infrastructureBtn.isVisible() && availablePC >= 5) {
        await infrastructureBtn.click();
        await expect(page.locator('#game-log').getByText(/sponsored/i)).toBeVisible();
        console.log(`✅ ${player} sponsored Infrastructure Bill`);
      } else {
        // Close modal if nothing affordable
        await page.keyboard.press('Escape');
        console.log(`❌ ${player} couldn't afford to sponsor`);
      }
    }

    // Pass Turn if no actions left
    const passBtn = page.getByRole('button', { name: /pass turn/i });
    if (await passBtn.isVisible()) {
      await passBtn.click();
      console.log(`✅ ${player} passed turn`);
      
      // Wait for the UI to update after passing turn
      await page.waitForTimeout(2000);
      
      // Check what the current player is now
      const currentPlayerName = await page.locator('#phase-indicator .player-name').textContent();
      console.log(`After ${player} passed turn, current player is: ${currentPlayerName}`);
      
      // Wait for the next player to be visible (with a longer timeout)
      if (player === 'Alice') {
        await expect(page.locator('#phase-indicator .player-name').getByText('Bob')).toBeVisible({ timeout: 10000 });
      } else if (player === 'Bob') {
        await expect(page.locator('#phase-indicator .player-name').getByText('Charlie')).toBeVisible({ timeout: 10000 });
      }
    }
  }

  console.log('✅ Simple game flow test completed successfully!');
}); 