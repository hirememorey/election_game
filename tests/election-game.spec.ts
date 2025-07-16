import { test, expect } from '@playwright/test';
import { 
  getCurrentPlayerInfo, 
  isActionValid, 
  waitForPlayerChange, 
  performValidAction, 
  createNewGame,
  handleSponsorLegislationModal,
  handleLegislationCommitmentModal
} from './test-utils';

test.describe('Election Game - Full Playability', () => {

  test('Full game flow is playable and never gets stuck', async ({ page }) => {
    // Create new game
    await createNewGame(page);

    // --- Action Phase: Each player takes actions ---
    for (let round = 1; round <= 2; round++) {
      console.log(`\n=== Starting Round ${round} ===`);
      
      // Alice's turn
      await waitForPlayerChange(page, 'Alice');
      await performValidAction(page, 'fundraise', 1);
      await performValidAction(page, 'network', 1);
      
      // Bob's turn
      await waitForPlayerChange(page, 'Bob');
      await performValidAction(page, 'sponsor legislation', 2);
      
      // Handle sponsor legislation modal if it appears
      await handleSponsorLegislationModal(page);
      
      // Charlie's turn
      await waitForPlayerChange(page, 'Charlie');
      await performValidAction(page, 'pass turn', 0);
      
      // Back to Alice
      await waitForPlayerChange(page, 'Alice');
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
    // Create new game
    await createNewGame(page);

    // Alice sponsors legislation
    await waitForPlayerChange(page, 'Alice');
    await performValidAction(page, 'sponsor legislation', 2);
    
    // Handle sponsor legislation modal
    await handleSponsorLegislationModal(page);

    // Bob secretly supports
    await waitForPlayerChange(page, 'Bob');
    await performValidAction(page, 'support', 1, 5);
    
    // Handle support modal
    await handleLegislationCommitmentModal(page, 'support', 5);
    
    // Check for secret commitment confirmation
    await expect(page.locator('#game-log').getByText(/secret commitment/i)).toBeVisible();
    await expect(page.locator('#game-log').getByText(/has been registered/i)).toBeVisible();

    // Charlie secretly opposes
    await waitForPlayerChange(page, 'Charlie');
    await performValidAction(page, 'oppose', 1, 3);
    
    // Handle oppose modal
    await handleLegislationCommitmentModal(page, 'oppose', 3);
    
    // Check for secret commitment confirmation
    await expect(page.locator('#game-log').getByText(/secret commitment/i)).toBeVisible();
    await expect(page.locator('#game-log').getByText(/has been registered/i)).toBeVisible();
  });

  test('Game never gets stuck when players have no valid actions', async ({ page }) => {
    // Create new game
    await createNewGame(page);

    // Simulate several rounds where players might have no actions
    for (let round = 1; round <= 3; round++) {
      console.log(`\n=== Round ${round} - Testing no valid actions scenario ===`);
      
      for (const player of ['Alice', 'Bob']) {
        // Wait for player turn
        await waitForPlayerChange(page, player);
        
        // Get current state
        const { ap, pc } = await getCurrentPlayerInfo(page);
        console.log(`${player} has ${ap} AP and ${pc} PC`);

        // Try to take any available action
        const availableActions = [
          { name: 'fundraise', ap: 1, pc: 0 },
          { name: 'network', ap: 1, pc: 0 },
          { name: 'sponsor legislation', ap: 2, pc: 0 },
          { name: 'support', ap: 1, pc: 3 },
          { name: 'oppose', ap: 1, pc: 2 },
          { name: 'pass turn', ap: 0, pc: 0 }
        ];

        let actionTaken = false;
        for (const action of availableActions) {
          if (await isActionValid(page, action.name, action.ap, action.pc)) {
            await performValidAction(page, action.name, action.ap, action.pc);
            actionTaken = true;
            break;
          }
        }

        // If no action was taken, the game should still advance
        if (!actionTaken) {
          console.log(`❌ No valid actions for ${player}, waiting for turn to advance...`);
          // Wait a bit and check if the game has advanced
          await page.waitForTimeout(2000);
          const currentPlayerName = await page.locator('#phase-indicator .player-name').textContent();
          expect(currentPlayerName).not.toBe(player);
          console.log(`✅ Turn advanced from ${player} to ${currentPlayerName}`);
        }
      }
    }
  });

  test('Error handling works correctly', async ({ page }) => {
    // Create new game
    await createNewGame(page);

    // Try to take action with insufficient PC
    await waitForPlayerChange(page, 'Alice');
    await performValidAction(page, 'sponsor legislation', 2);
    
    // Handle sponsor legislation modal
    await handleSponsorLegislationModal(page);
    
    // Check for error message
    await expect(page.getByText(/not enough/i)).toBeVisible();

    // Try to support legislation with insufficient PC
    await waitForPlayerChange(page, 'Bob');
    await performValidAction(page, 'support', 1, 999);
    
    // Handle support modal
    await handleLegislationCommitmentModal(page, 'support', 999);
    
    // Check for error message
    await expect(page.getByText(/not enough/i)).toBeVisible();
  });
}); 