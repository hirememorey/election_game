import { Page, expect } from '@playwright/test';

// Helper function to get current player info
export async function getCurrentPlayerInfo(page: Page) {
  const phaseIndicator = page.locator('#phase-indicator');
  const playerName = await phaseIndicator.locator('.player-name').textContent();
  const apText = await phaseIndicator.locator('.action-points').textContent();
  const apMatch = apText?.match(/(\d+) AP/);
  const ap = apMatch ? parseInt(apMatch[1], 10) : 0;
  
  // Get PC from player stats
  const playerStats = await phaseIndicator.locator('.player-stats').textContent();
  const pcMatch = playerStats?.match(/PC: (\d+)/);
  const pc = pcMatch ? parseInt(pcMatch[1], 10) : 0;
  
  return { playerName, ap, pc };
}

// Helper function to check if an action is available and valid
export async function isActionValid(page: Page, actionName: string, requiredAP = 1, requiredPC = 0) {
  const { ap, pc } = await getCurrentPlayerInfo(page);
  
  // Check if we have enough AP
  if (ap < requiredAP) {
    console.log(`❌ Action ${actionName} requires ${requiredAP} AP but player has ${ap} AP`);
    return false;
  }
  
  // Check if we have enough PC (for actions that cost PC)
  if (requiredPC > 0 && pc < requiredPC) {
    console.log(`❌ Action ${actionName} requires ${requiredPC} PC but player has ${pc} PC`);
    return false;
  }
  
  // Check if the button is visible
  const actionBtn = page.getByRole('button', { name: new RegExp(actionName, 'i') });
  if (!(await actionBtn.isVisible())) {
    console.log(`❌ Action ${actionName} button is not visible`);
    return false;
  }
  
  console.log(`✅ Action ${actionName} is valid - AP: ${ap}, PC: ${pc}`);
  return true;
}

// Helper function to wait for player change
export async function waitForPlayerChange(page: Page, expectedPlayer: string) {
  console.log(`Waiting for player to change to ${expectedPlayer}...`);
  await expect(page.locator('#phase-indicator .player-name').getByText(expectedPlayer)).toBeVisible();
  console.log(`✅ Player changed to ${expectedPlayer}`);
}

// Helper function to perform action with validation
export async function performValidAction(page: Page, actionName: string, requiredAP = 1, requiredPC = 0) {
  const { playerName, ap, pc } = await getCurrentPlayerInfo(page);
  console.log(`\n--- Attempting ${actionName} for ${playerName} (AP: ${ap}, PC: ${pc}) ---`);
  
  if (!(await isActionValid(page, actionName, requiredAP, requiredPC))) {
    console.log(`❌ Skipping ${actionName} - not valid`);
    return false;
  }
  
  const actionBtn = page.getByRole('button', { name: new RegExp(actionName, 'i') });
  await actionBtn.click();
  console.log(`✅ Performed ${actionName}`);
  
  // Wait for action to complete and check for log entry
  try {
    await expect(page.locator('#game-log').getByText(new RegExp(actionName, 'i'))).toBeVisible({ timeout: 5000 });
    console.log(`✅ Log entry for ${actionName} found`);
  } catch (error) {
    console.log(`⚠️ No log entry found for ${actionName} - this might be expected for some actions`);
  }
  
  return true;
}

// Helper function to create a new game
export async function createNewGame(page: Page, players: string[] = ['Alice', 'Bob', 'Charlie']) {
  await page.goto('http://localhost:5001');
  
  // Fill in player names
  for (let i = 0; i < players.length; i++) {
    await page.getByLabel(`Player ${i + 1}`).fill(players[i]);
  }
  
  await page.getByRole('button', { name: /start game/i }).click();
  
  // Wait for game to start
  await expect(page.locator('#phase-indicator').getByText(/Action Phase/i)).toBeVisible();
  
  console.log('✅ New game created with players:', players);
}

// Helper function to handle sponsor legislation modal
export async function handleSponsorLegislationModal(page: Page) {
  const sponsorModal = page.getByText('Choose legislation to sponsor:');
  if (await sponsorModal.isVisible()) {
    const { pc } = await getCurrentPlayerInfo(page);
    console.log(`Player has ${pc} PC available for sponsoring`);
    
    // Find affordable legislation
    const billButtons = await page.locator('.action-btn').all();
    let clicked = false;
    for (const btn of billButtons) {
      const text = await btn.textContent();
      const costMatch = text && text.match(/Cost: (\d+) PC/);
      if (costMatch) {
        const cost = parseInt(costMatch[1], 10);
        if (pc >= cost) {
          await btn.click();
          clicked = true;
          console.log(`✅ Sponsored legislation costing ${cost} PC`);
          break;
        }
      }
    }
    if (!clicked) {
      console.log(`❌ No affordable legislation found, closing modal`);
      await page.keyboard.press('Escape');
    }
    return clicked;
  }
  return false;
}

// Helper function to handle support/oppose legislation modal
export async function handleLegislationCommitmentModal(page: Page, actionType: 'support' | 'oppose', pcToCommit: number) {
  const modal = page.getByText(/choose legislation/i);
  if (await modal.isVisible()) {
    await page.getByLabel(/choose legislation/i).selectOption({ index: 1 });
    await page.getByLabel(/PC to Commit/i).fill(pcToCommit.toString());
    
    const buttonName = actionType === 'support' ? /secretly support/i : /secretly oppose/i;
    await page.getByRole('button', { name: buttonName }).click();
    
    console.log(`✅ ${actionType}ed legislation with ${pcToCommit} PC`);
    return true;
  }
  return false;
} 