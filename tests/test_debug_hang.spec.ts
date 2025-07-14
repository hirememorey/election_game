import { test, expect } from '@playwright/test';

test('Debug hang test - step by step with more granular debugging', async ({ page }) => {
  console.log('=== Starting debug hang test ===');
  
  console.log('Step 1: Navigating to game...');
  await page.goto('http://localhost:5001');
  
  console.log('Step 2: Waiting for setup screen...');
  await page.waitForSelector('#setup-screen', { timeout: 10000 });
  
  console.log('Step 3: Filling player names...');
  await page.fill('#player1', 'Alice');
  await page.fill('#player2', 'Bob');
  await page.fill('#player3', 'Charlie');
  
  console.log('Step 4: Clicking start game...');
  await page.click('#start-game-btn');
  
  console.log('Step 5: Waiting for game screen...');
  await page.waitForSelector('#game-screen', { timeout: 10000 });
  await page.waitForSelector('text=Action Phase', { timeout: 10000 });
  
  console.log('Step 6: Getting initial PC...');
  const initialPC = await page.locator('text=PC:').first().textContent();
  console.log('Initial PC:', initialPC);
  
  console.log('Step 7: Looking for Sponsor Legislation button...');
  const sponsorButton = page.locator('button:has-text("Sponsor Legislation")');
  await sponsorButton.waitFor({ timeout: 10000 });
  console.log('Sponsor button found!');
  
  console.log('Step 8: Clicking Sponsor Legislation...');
  await sponsorButton.click();
  console.log('Sponsor button clicked!');
  
  console.log('Step 9: Waiting for legislation modal...');
  await page.waitForSelector('text=Choose legislation to sponsor', { timeout: 10000 });
  console.log('Legislation modal opened!');
  
  console.log('Step 10: Looking for MILITARY option...');
  const militaryOption = page.locator('text=MILITARY');
  await militaryOption.waitFor({ timeout: 10000 });
  console.log('MILITARY option found!');
  
  console.log('Step 11: Clicking MILITARY...');
  await militaryOption.click();
  console.log('MILITARY clicked!');
  
  console.log('Step 12: Taking screenshot after MILITARY click...');
  await page.screenshot({ path: 'debug_after_military_click.png' });
  
  console.log('Step 13: Checking if modal is still visible...');
  const modalVisible = await page.locator('text=Choose legislation to sponsor').isVisible();
  console.log('Modal still visible:', modalVisible);
  
  console.log('Step 14: Checking for any error messages...');
  const errorElements = await page.locator('.error, .alert, [class*="error"]').all();
  console.log('Error elements found:', errorElements.length);
  
  console.log('Step 15: Checking page content...');
  const pageContent = await page.content();
  console.log('Page contains "Action Phase":', pageContent.includes('Action Phase'));
  console.log('Page contains "Choose legislation":', pageContent.includes('Choose legislation'));
  
  console.log('Step 16: Trying to wait for Action Phase with shorter timeout...');
  try {
    await page.waitForSelector('text=Action Phase', { timeout: 5000 });
    console.log('Action Phase found after MILITARY click!');
  } catch (error) {
    console.log('Timeout waiting for Action Phase:', error.message);
  }
  
  console.log('Step 17: Final screenshot...');
  await page.screenshot({ path: 'debug_final_state.png' });
  
  console.log('=== Debug test completed ===');
}); 