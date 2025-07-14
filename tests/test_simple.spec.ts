import { test, expect } from '@playwright/test';

test('Simple page load test', async ({ page }) => {
  console.log('Starting simple test...');
  
  console.log('Navigating to game...');
  await page.goto('http://localhost:5001');
  
  console.log('Waiting for setup screen...');
  await page.waitForSelector('#setup-screen', { timeout: 10000 });
  console.log('Setup screen found!');
  
  console.log('Checking if player inputs exist...');
  const player1Input = await page.locator('#player1');
  expect(await player1Input.isVisible()).toBe(true);
  console.log('Player inputs found!');
  
  console.log('Filling player names...');
  await page.fill('#player1', 'Alice');
  await page.fill('#player2', 'Bob');
  await page.fill('#player3', 'Charlie');
  console.log('Names filled!');
  
  console.log('Clicking start game...');
  await page.click('#start-game-btn');
  console.log('Start button clicked!');
  
  console.log('Waiting for game screen...');
  await page.waitForSelector('#game-screen', { timeout: 10000 });
  console.log('Game screen found!');
  
  console.log('Waiting for Action Phase text...');
  await page.waitForSelector('text=Action Phase', { timeout: 10000 });
  console.log('Action Phase found!');
  
  console.log('Test completed successfully!');
}); 