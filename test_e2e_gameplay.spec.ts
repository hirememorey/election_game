import { test, expect } from '@playwright/test';
import { spawn, ChildProcess } from 'child_process';

const PORT = 5001;
const URL = `http://localhost:${PORT}`;

test.describe('End-to-End Gameplay Test', () => {
  let serverProcess: ChildProcess;

  test.beforeAll(async () => {
    // Start the server
    serverProcess = spawn('python3', ['server.py'], {
      stdio: 'pipe',
      detached: true,
    });

    serverProcess.stdout?.on('data', (data) => {
      console.log(`Server stdout: ${data}`);
    });

    serverProcess.stderr?.on('data', (data) => {
      console.error(`Server stderr: ${data}`);
    });

    // Wait for the server to be ready by polling the health endpoint
    let retries = 0;
    while (retries < 30) {
      try {
        const response = await fetch(`${URL}/health`);
        if (response.ok) {
          console.log('Server is ready');
          break;
        }
      } catch (error) {
        // Server not ready yet
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
      retries++;
    }
  });

  test.afterAll(async () => {
    // Stop the server
    if (serverProcess) {
      serverProcess.kill();
    }
  });

  test('should load the game and display initial state', async ({ page }) => {
    await page.goto(URL);

    // 1. Wait for the page to load and the terminal to be initialized
    await page.waitForSelector('#terminal-container', { timeout: 10000 });

    // 2. Check that the terminal container exists and has content
    const terminalExists = await page.evaluate(() => {
      const terminal = document.querySelector('#terminal-container');
      return terminal !== null;
    });
    
    expect(terminalExists).toBe(true);

    // 3. Wait for WebSocket connection and game state to load
    await page.waitForFunction(() => {
      const terminal = document.querySelector('#terminal-container');
      return terminal && terminal.textContent && (
        terminal.textContent.includes('Connected to server.') ||
        terminal.textContent.includes('ELECTION: THE GAME') ||
        terminal.textContent.includes("Human's Turn")
      );
    }, { timeout: 15000 });

    // 4. Verify the game shows it's the human's turn
    await page.waitForFunction(() => {
      const terminal = document.querySelector('#terminal-container');
      return terminal && terminal.textContent && terminal.textContent.includes("Human's Turn");
    }, { timeout: 10000 });

    // 5. Verify available actions are displayed
    await page.waitForFunction(() => {
      const terminal = document.querySelector('#terminal-container');
      return terminal && terminal.textContent && terminal.textContent.includes('Available Actions:');
    }, { timeout: 10000 });

    // 6. Take a player action (fundraise)
    await page.keyboard.type('1');
    await page.keyboard.press('Enter');

    // 7. Verify the action was processed (AP should decrease)
    await page.waitForFunction(() => {
      const terminal = document.querySelector('#terminal-container');
      return terminal && terminal.textContent && terminal.textContent.includes("AP: 1");
    }, { timeout: 10000 });

    console.log('✅ Comprehensive E2E test passed: Game loads, displays state, and player can take actions');
  });
}); 