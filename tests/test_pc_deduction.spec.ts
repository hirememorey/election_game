import { test, expect } from '@playwright/test';

async function debugPage(page, step) {
  console.log(`[DEBUG] Taking screenshot and saving HTML at step: ${step}`);
  await page.screenshot({ path: `debug-${step}.png`, fullPage: true });
  const html = await page.content();
  require('fs').writeFileSync(`debug-${step}.html`, html);
}

async function closeModalIfPresent(page) {
  // Try to close modal if it exists
  try {
    const closeBtn = await page.$('button:has-text("Cancel")');
    if (closeBtn) {
      await closeBtn.click();
      console.log('[DEBUG] Closed modal with Cancel button.');
    }
  } catch (e) {
    // Ignore
  }
  try {
    const closeBtn2 = await page.$('button:has-text("×")');
    if (closeBtn2) {
      await closeBtn2.click();
      console.log('[DEBUG] Closed modal with × button.');
    }
  } catch (e) {
    // Ignore
  }
}

test.describe('PC Deduction Tests', () => {
  test('PC should be deducted immediately when committing to oppose legislation', async ({ page }) => {
    try {
      console.log('Navigating to game...');
      await page.goto('http://localhost:5001');
      
      console.log('Waiting for setup screen...');
      await page.waitForSelector('#setup-screen', { timeout: 5000 });
      
      console.log('Filling player names...');
      await page.fill('#player1', 'Alice');
      await page.fill('#player2', 'Bob');
      await page.fill('#player3', 'Charlie');
      
      console.log('Clicking start game...');
      await page.click('#start-game-btn');
      
      console.log('Waiting for game screen...');
      await page.waitForSelector('#game-screen', { timeout: 5000 });
      await page.waitForSelector('text=Action Phase', { timeout: 5000 });
      
      console.log('Getting initial PC...');
      const initialPC = await page.locator('text=PC:').first().textContent();
      console.log('Initial PC:', initialPC);
      
      console.log('Clicking Sponsor Legislation...');
      await page.click('button:has-text("Sponsor Legislation")');
      console.log('Waiting for Choose legislation to sponsor...');
      await page.waitForSelector('text=Choose legislation to sponsor', { timeout: 5000 });
      await page.click('text=MILITARY');
      await closeModalIfPresent(page);
      
      console.log('Waiting for Action Phase after sponsor...');
      await page.waitForSelector('text=Action Phase', { timeout: 5000 });
      
      console.log('Getting PC after sponsor...');
      const pcAfterSponsor = await page.locator('text=PC:').first().textContent();
      console.log('PC after sponsor:', pcAfterSponsor);
      
      const initialPCNum = parseInt(initialPC?.match(/PC: (\d+)/)?.[1] || '0');
      const pcAfterSponsorNum = parseInt(pcAfterSponsor?.match(/PC: (\d+)/)?.[1] || '0');
      console.log('Initial PC num:', initialPCNum, 'PC after sponsor num:', pcAfterSponsorNum);
      expect(pcAfterSponsorNum).toBeLessThan(initialPCNum);
      
      console.log('Clicking Oppose Legislation...');
      await page.click('button:has-text("Oppose Legislation")');
      console.log('Waiting for Choose legislation to oppose...');
      await page.waitForSelector('text=Choose legislation to oppose', { timeout: 5000 });
      await page.click('text=INFRASTRUCTURE');
      
      console.log('Filling oppose amount...');
      await page.fill('input[type="number"]', pcAfterSponsorNum.toString());
      await page.click('button:has-text("Commit")');
      await closeModalIfPresent(page);
      
      console.log('Waiting for Action Phase after commit...');
      await page.waitForSelector('text=Action Phase', { timeout: 5000 });
      
      console.log('Getting PC after commit...');
      const pcAfterCommit = await page.locator('text=PC:').first().textContent();
      console.log('PC after commit:', pcAfterCommit);
      
      const pcAfterCommitNum = parseInt(pcAfterCommit?.match(/PC: (\d+)/)?.[1] || '0');
      console.log('PC after commit num:', pcAfterCommitNum);
      expect(pcAfterCommitNum).toBe(0);
    } catch (e) {
      await debugPage(page, 'oppose-legislation-error');
      throw e;
    }
  });
  
  test('PC should be deducted immediately when committing to support legislation', async ({ page }) => {
    try {
      console.log('Navigating to game...');
      await page.goto('http://localhost:5001');
      
      console.log('Waiting for setup screen...');
      await page.waitForSelector('#setup-screen', { timeout: 5000 });
      
      console.log('Filling player names...');
      await page.fill('#player1', 'Alice');
      await page.fill('#player2', 'Bob');
      await page.fill('#player3', 'Charlie');
      
      console.log('Clicking start game...');
      await page.click('#start-game-btn');
      
      console.log('Waiting for game screen...');
      await page.waitForSelector('#game-screen', { timeout: 5000 });
      await page.waitForSelector('text=Action Phase', { timeout: 5000 });
      
      console.log('Getting initial PC...');
      const initialPC = await page.locator('text=PC:').first().textContent();
      console.log('Initial PC:', initialPC);
      
      console.log('Clicking Sponsor Legislation...');
      await page.click('button:has-text("Sponsor Legislation")');
      console.log('Waiting for Choose legislation to sponsor...');
      await page.waitForSelector('text=Choose legislation to sponsor', { timeout: 5000 });
      await page.click('text=MILITARY');
      await closeModalIfPresent(page);
      
      console.log('Waiting for Action Phase after sponsor...');
      await page.waitForSelector('text=Action Phase', { timeout: 5000 });
      
      console.log('Getting PC after sponsor...');
      const pcAfterSponsor = await page.locator('text=PC:').first().textContent();
      console.log('PC after sponsor:', pcAfterSponsor);
      
      const pcAfterSponsorNum = parseInt(pcAfterSponsor?.match(/PC: (\d+)/)?.[1] || '0');
      const initialPCNum = parseInt(initialPC?.match(/PC: (\d+)/)?.[1] || '0');
      console.log('Initial PC num:', initialPCNum, 'PC after sponsor num:', pcAfterSponsorNum);
      expect(pcAfterSponsorNum).toBeLessThan(initialPCNum);
      
      console.log('Clicking Support Legislation...');
      await page.click('button:has-text("Support Legislation")');
      console.log('Waiting for Choose legislation to support...');
      await page.waitForSelector('text=Choose legislation to support', { timeout: 5000 });
      await page.click('text=INFRASTRUCTURE');
      
      const commitAmount = Math.floor(pcAfterSponsorNum / 2);
      console.log('Filling support amount:', commitAmount);
      await page.fill('input[type="number"]', commitAmount.toString());
      await page.click('button:has-text("Commit")');
      await closeModalIfPresent(page);
      
      console.log('Waiting for Action Phase after commit...');
      await page.waitForSelector('text=Action Phase', { timeout: 5000 });
      
      console.log('Getting PC after commit...');
      const pcAfterCommit = await page.locator('text=PC:').first().textContent();
      console.log('PC after commit:', pcAfterCommit);
      
      const pcAfterCommitNum = parseInt(pcAfterCommit?.match(/PC: (\d+)/)?.[1] || '0');
      console.log('PC after commit num:', pcAfterCommitNum);
      expect(pcAfterCommitNum).toBe(pcAfterSponsorNum - commitAmount);
    } catch (e) {
      await debugPage(page, 'support-legislation-error');
      throw e;
    }
  });
  
  test('Should not allow committing more PC than available', async ({ page }) => {
    try {
      console.log('Navigating to game...');
      await page.goto('http://localhost:5001');
      
      console.log('Waiting for setup screen...');
      await page.waitForSelector('#setup-screen', { timeout: 5000 });
      
      console.log('Filling player names...');
      await page.fill('#player1', 'Alice');
      await page.fill('#player2', 'Bob');
      await page.fill('#player3', 'Charlie');
      
      console.log('Clicking start game...');
      await page.click('#start-game-btn');
      
      console.log('Waiting for game screen...');
      await page.waitForSelector('#game-screen', { timeout: 5000 });
      await page.waitForSelector('text=Action Phase', { timeout: 5000 });
      
      console.log('Getting initial PC...');
      const initialPC = await page.locator('text=PC:').first().textContent();
      const initialPCNum = parseInt(initialPC?.match(/PC: (\d+)/)?.[1] || '0');
      console.log('Initial PC:', initialPCNum);
      
      console.log('Clicking Oppose Legislation...');
      await page.click('button:has-text("Oppose Legislation")');
      console.log('Waiting for Choose legislation to oppose...');
      await page.waitForSelector('text=Choose legislation to oppose', { timeout: 5000 });
      await page.click('text=MILITARY');
      
      console.log('Filling oppose amount:', initialPCNum + 10);
      await page.fill('input[type="number"]', (initialPCNum + 10).toString());
      await page.click('button:has-text("Commit")');
      await closeModalIfPresent(page);
      
      console.log('Waiting for 2 seconds for error or no change...');
      await page.waitForTimeout(2000);
      
      console.log('Getting PC after attempt...');
      const pcAfterAttempt = await page.locator('text=PC:').first().textContent();
      const pcAfterAttemptNum = parseInt(pcAfterAttempt?.match(/PC: (\d+)/)?.[1] || '0');
      console.log('PC after attempt:', pcAfterAttemptNum);
      expect(pcAfterAttemptNum).toBe(initialPCNum);
    } catch (e) {
      await debugPage(page, 'overcommit-error');
      throw e;
    }
  });
}); 