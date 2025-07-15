import { test, expect } from '@playwright/test';

test.describe('Election Game - Full Playability', () => {
  test('Full game flow is playable and never gets stuck', async ({ page }) => {
    // Visit the game
    await page.goto('http://localhost:5001');

    // --- Game Creation ---
    // Fill in player names directly (no "Create Game" button)
    await page.getByLabel('Player 1').fill('Alice');
    await page.getByLabel('Player 2').fill('Bob');
    await page.getByLabel('Player 3').fill('Charlie');
    await page.getByRole('button', { name: /start game/i }).click();

    // Wait for game to start (game starts in Action Phase after automatic Event Phase)
    await expect(page.locator('#phase-indicator').getByText(/Action Phase/i)).toBeVisible();

    // --- Action Phase: Each player takes actions ---
    for (let round = 1; round <= 2; round++) {
      for (const player of ['Alice', 'Bob', 'Charlie']) {
        // Wait for correct player turn
        await expect(page.locator('#phase-indicator .player-name').getByText(player)).toBeVisible();

        // Try Fundraise
        const fundraiseBtn = page.getByRole('button', { name: /fundraise/i });
        if (await fundraiseBtn.isVisible()) {
          await fundraiseBtn.click();
          await expect(page.locator('#game-log').getByText(/takes the Fundraise action and gains/i)).toBeVisible();
        }

        // Try Network
        const networkBtn = page.getByRole('button', { name: /network/i });
        if (await networkBtn.isVisible()) {
          await networkBtn.click();
          await expect(page.locator('#game-log').getByText(/network/i)).toBeVisible();
        }

        // Try Sponsor Legislation (only once per round)
        const sponsorBtn = page.getByRole('button', { name: /sponsor legislation/i });
        if (await sponsorBtn.isVisible()) {
          await sponsorBtn.click();
          // Wait for modal
          await expect(page.getByText('Choose legislation to sponsor:')).toBeVisible();

          // Parse available PC from the phase indicator
          const phaseText = await page.locator('#phase-indicator').textContent();
          const pcMatch = phaseText && phaseText.match(/PC: (\d+)/);
          const availablePC = pcMatch ? parseInt(pcMatch[1], 10) : 0;

          // Find all sponsorable bills and their costs
          const billButtons = await page.locator('.action-btn').all();
          let clicked = false;
          for (const btn of billButtons) {
            const text = await btn.textContent();
            const costMatch = text && text.match(/Cost: (\d+) PC/);
            if (costMatch) {
              const cost = parseInt(costMatch[1], 10);
              if (availablePC >= cost) {
                await btn.click();
                clicked = true;
                break;
              }
            }
          }
          if (clicked) {
            await expect(page.locator('#game-log').getByText(/sponsored/i)).toBeVisible();
          } else {
            // Close modal if nothing affordable
            await page.keyboard.press('Escape');
          }
        }

        // Try Support/Oppose (if available)
        const supportBtn = page.getByRole('button', { name: /support/i });
        if (await supportBtn.isVisible()) {
          await supportBtn.click();
          await page.getByLabel(/choose legislation/i).selectOption({ index: 1 });
          await page.getByLabel(/PC to Commit/i).fill('3');
          await page.getByRole('button', { name: /secretly support/i }).click();
          await expect(page.locator('#game-log').getByText(/secret commitment/i)).toBeVisible();
        }

        const opposeBtn = page.getByRole('button', { name: /oppose/i });
        if (await opposeBtn.isVisible()) {
          await opposeBtn.click();
          await page.getByLabel(/choose legislation/i).selectOption({ index: 1 });
          await page.getByLabel(/PC to Commit/i).fill('2');
          await page.getByRole('button', { name: /secretly oppose/i }).click();
          await expect(page.locator('#game-log').getByText(/secret commitment/i)).toBeVisible();
        }

        // Pass Turn if no actions left
        const passBtn = page.getByRole('button', { name: /pass turn/i });
        if (await passBtn.isVisible()) {
          await passBtn.click();
        }
      }
    }

    // --- End of Term: Legislation Session ---
    // Wait for resolve legislation button
    await expect(page.getByRole('button', { name: /resolve legislation/i })).toBeVisible();
    await page.getByRole('button', { name: /resolve legislation/i }).click();

    // Dramatic reveal in log
    await expect(page.getByText(/reveal/i)).toBeVisible();

    // --- Election Phase ---
    // Declare candidacy if possible
    const declareBtn = page.getByRole('button', { name: /declare candidacy/i });
    if (await declareBtn.isVisible()) {
      await declareBtn.click();
      await page.getByLabel(/choose office/i).selectOption({ index: 1 });
      await page.getByLabel(/PC to Commit/i).fill('5');
      await page.getByRole('button', { name: /declare/i }).click();
    }

    // Resolve elections
    await expect(page.getByRole('button', { name: /resolve elections/i })).toBeVisible();
    await page.getByRole('button', { name: /resolve elections/i }).click();

    // --- Next Term Starts ---
    await expect(page.getByText(/a new term begins/i)).toBeVisible();

    // --- Game End ---
    // (Optional) Simulate until a player wins presidency and check for winner message
  });

  test('Secret commitment system works correctly', async ({ page }) => {
    await page.goto('http://localhost:5001');

    // Create game
    await page.getByLabel('Player 1').fill('Alice');
    await page.getByLabel('Player 2').fill('Bob');
    await page.getByRole('button', { name: /start game/i }).click();

    // Wait for game to start (game starts in Action Phase after automatic Event Phase)
    await expect(page.locator('#phase-indicator').getByText(/Action Phase/i)).toBeVisible();

    // Alice sponsors legislation
    await page.getByRole('button', { name: /sponsor legislation/i }).click();
    await page.getByRole('button', { name: /infrastructure/i }).click();

    // Bob secretly supports
    await expect(page.locator('#phase-indicator .player-name').getByText('Bob')).toBeVisible();
    await page.getByRole('button', { name: /support/i }).click();
    await page.getByLabel(/choose legislation/i).selectOption({ index: 1 });
    await page.getByLabel(/PC to Commit/i).fill('5');
    await page.getByRole('button', { name: /secretly support/i }).click();
    
    // Check for secret commitment confirmation
    await expect(page.locator('#game-log').getByText(/secret commitment/i)).toBeVisible();
    await expect(page.locator('#game-log').getByText(/has been registered/i)).toBeVisible();

    // Charlie secretly opposes
    await expect(page.locator('#phase-indicator .player-name').getByText('Charlie')).toBeVisible();
    await page.getByRole('button', { name: /oppose/i }).click();
    await page.getByLabel(/choose legislation/i).selectOption({ index: 1 });
    await page.getByLabel(/PC to Commit/i).fill('3');
    await page.getByRole('button', { name: /secretly oppose/i }).click();
    
    // Check for secret commitment confirmation
    await expect(page.locator('#game-log').getByText(/secret commitment/i)).toBeVisible();
    await expect(page.locator('#game-log').getByText(/has been registered/i)).toBeVisible();
  });

  test('Game never gets stuck when players have no valid actions', async ({ page }) => {
    await page.goto('http://localhost:5001');

    // Create game
    await page.getByLabel('Player 1').fill('Alice');
    await page.getByLabel('Player 2').fill('Bob');
    await page.getByRole('button', { name: /start game/i }).click();

    // Wait for game to start (game starts in Action Phase after automatic Event Phase)
    await expect(page.locator('#phase-indicator').getByText(/Action Phase/i)).toBeVisible();

    // Simulate several rounds where players might have no actions
    for (let round = 1; round <= 3; round++) {
      for (const player of ['Alice', 'Bob']) {
        // Wait for player turn
        await expect(page.locator('#phase-indicator .player-name').getByText(player)).toBeVisible();

        // Try to take any available action
        const availableActions = [
          page.getByRole('button', { name: /fundraise/i }),
          page.getByRole('button', { name: /network/i }),
          page.getByRole('button', { name: /sponsor legislation/i }),
          page.getByRole('button', { name: /support/i }),
          page.getByRole('button', { name: /oppose/i }),
          page.getByRole('button', { name: /pass turn/i })
        ];

        let actionTaken = false;
        for (const action of availableActions) {
          if (await action.isVisible()) {
            await action.click();
            actionTaken = true;
            break;
          }
        }

        // If no action was taken, the game should still advance
        if (!actionTaken) {
          // Wait a bit and check if the game has advanced
          await page.waitForTimeout(2000);
          const currentPlayerName = await page.locator('#phase-indicator .player-name').textContent();
          expect(currentPlayerName).not.toBe(player);
        }
      }
    }
  });

  test('Error handling works correctly', async ({ page }) => {
    await page.goto('http://localhost:5001');

    // Create game
    await page.getByLabel('Player 1').fill('Alice');
    await page.getByLabel('Player 2').fill('Bob');
    await page.getByRole('button', { name: /start game/i }).click();

    // Wait for game to start (game starts in Action Phase after automatic Event Phase)
    await expect(page.locator('#phase-indicator').getByText(/Action Phase/i)).toBeVisible();

    // Try to take action with insufficient PC
    await page.getByRole('button', { name: /sponsor legislation/i }).click();
    await page.getByRole('button', { name: /infrastructure/i }).click();
    
    // Check for error message
    await expect(page.getByText(/not enough/i)).toBeVisible();

    // Try to support legislation with insufficient PC
    await page.getByRole('button', { name: /support/i }).click();
    await page.getByLabel(/choose legislation/i).selectOption({ index: 1 });
    await page.getByLabel(/PC to Commit/i).fill('999'); // More PC than player has
    await page.getByRole('button', { name: /secretly support/i }).click();
    
    // Check for error message
    await expect(page.getByText(/not enough/i)).toBeVisible();
  });
}); 