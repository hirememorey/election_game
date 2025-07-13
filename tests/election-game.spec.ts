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
    await expect(page.getByText(/Action Phase/i)).toBeVisible();

    // --- Action Phase: Each player takes actions ---
    for (let round = 1; round <= 2; round++) {
      for (const player of ['Alice', 'Bob', 'Charlie']) {
        // Wait for correct player turn
        await expect(page.getByText(new RegExp(`Current player: ${player}`, 'i'))).toBeVisible();

        // Try Fundraise
        const fundraiseBtn = page.getByRole('button', { name: /fundraise/i });
        if (await fundraiseBtn.isVisible()) {
          await fundraiseBtn.click();
          await expect(page.getByText(/gains/i)).toBeVisible();
        }

        // Try Network
        const networkBtn = page.getByRole('button', { name: /network/i });
        if (await networkBtn.isVisible()) {
          await networkBtn.click();
          await expect(page.getByText(/network/i)).toBeVisible();
        }

        // Try Sponsor Legislation (only once per round)
        const sponsorBtn = page.getByRole('button', { name: /sponsor legislation/i });
        if (await sponsorBtn.isVisible()) {
          await sponsorBtn.click();
          // Pick first available bill
          await page.getByRole('button', { name: /infrastructure/i }).click();
          await expect(page.getByText(/sponsored/i)).toBeVisible();
        }

        // Try Support/Oppose (if available)
        const supportBtn = page.getByRole('button', { name: /support/i });
        if (await supportBtn.isVisible()) {
          await supportBtn.click();
          await page.getByLabel(/choose legislation/i).selectOption({ index: 1 });
          await page.getByLabel(/PC to Commit/i).fill('3');
          await page.getByRole('button', { name: /secretly support/i }).click();
          await expect(page.getByText(/secret commitment/i)).toBeVisible();
        }

        const opposeBtn = page.getByRole('button', { name: /oppose/i });
        if (await opposeBtn.isVisible()) {
          await opposeBtn.click();
          await page.getByLabel(/choose legislation/i).selectOption({ index: 1 });
          await page.getByLabel(/PC to Commit/i).fill('2');
          await page.getByRole('button', { name: /secretly oppose/i }).click();
          await expect(page.getByText(/secret commitment/i)).toBeVisible();
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
    await expect(page.getByText(/Action Phase/i)).toBeVisible();

    // Alice sponsors legislation
    await page.getByRole('button', { name: /sponsor legislation/i }).click();
    await page.getByRole('button', { name: /infrastructure/i }).click();

    // Bob secretly supports
    await expect(page.getByText(/Current player: Bob/i)).toBeVisible();
    await page.getByRole('button', { name: /support/i }).click();
    await page.getByLabel(/choose legislation/i).selectOption({ index: 1 });
    await page.getByLabel(/PC to Commit/i).fill('5');
    await page.getByRole('button', { name: /secretly support/i }).click();
    
    // Check for secret commitment confirmation
    await expect(page.getByText(/secret commitment/i)).toBeVisible();
    await expect(page.getByText(/has been registered/i)).toBeVisible();

    // Charlie secretly opposes
    await expect(page.getByText(/Current player: Charlie/i)).toBeVisible();
    await page.getByRole('button', { name: /oppose/i }).click();
    await page.getByLabel(/choose legislation/i).selectOption({ index: 1 });
    await page.getByLabel(/PC to Commit/i).fill('3');
    await page.getByRole('button', { name: /secretly oppose/i }).click();
    
    // Check for secret commitment confirmation
    await expect(page.getByText(/secret commitment/i)).toBeVisible();
    await expect(page.getByText(/has been registered/i)).toBeVisible();
  });

  test('Game never gets stuck when players have no valid actions', async ({ page }) => {
    await page.goto('http://localhost:5001');

    // Create game
    await page.getByLabel('Player 1').fill('Alice');
    await page.getByLabel('Player 2').fill('Bob');
    await page.getByRole('button', { name: /start game/i }).click();

    // Wait for game to start (game starts in Action Phase after automatic Event Phase)
    await expect(page.getByText(/Action Phase/i)).toBeVisible();

    // Simulate several rounds where players might have no actions
    for (let round = 1; round <= 3; round++) {
      for (const player of ['Alice', 'Bob']) {
        // Wait for player turn
        await expect(page.getByText(new RegExp(`Current player: ${player}`, 'i'))).toBeVisible();

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
          const currentPlayerText = await page.textContent('body');
          expect(currentPlayerText).not.toContain(`Current player: ${player}`);
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
    await expect(page.getByText(/Action Phase/i)).toBeVisible();

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