/**
 * @jest-environment jsdom
 */

const { Terminal } = require('xterm');
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

// Read the HTML file to set up the DOM
const html = fs.readFileSync(path.resolve(__dirname, './index.html'), 'utf8');
const dom = new JSDOM(html, { runScripts: "dangerously" });
global.document = dom.window.document;
global.window = dom.window;

const { TerminalUI } = require('./app');

// Mock the Terminal class from xterm.js
jest.mock('xterm', () => ({
    Terminal: jest.fn().mockImplementation(() => ({
        open: jest.fn(),
        writeln: jest.fn(),
        write: jest.fn(),
        onKey: jest.fn(),
    })),
}));

describe('TerminalUI', () => {
    let ui;

    beforeEach(() => {
        ui = new TerminalUI();
    });

    test('should initialize and display welcome message', () => {
        expect(ui.term.open).toHaveBeenCalledWith(document.getElementById('terminal-container'));
        expect(ui.term.writeln).toHaveBeenCalledWith('Welcome to Election: The Game!');
        expect(ui.term.writeln).toHaveBeenCalledWith('Connecting to server...');
    });

    test('should handle key events', () => {
        // Simulate typing 'abc'
        ui.onKey({ key: 'a', domEvent: { keyCode: 65 } });
        ui.onKey({ key: 'b', domEvent: { keyCode: 66 } });
        ui.onKey({ key: 'c', domEvent: { keyCode: 67 } });
        expect(ui.inputBuffer).toBe('abc');
        expect(ui.term.write).toHaveBeenCalledWith('a');
        expect(ui.term.write).toHaveBeenCalledWith('b');
        expect(ui.term.write).toHaveBeenCalledWith('c');

        // Simulate backspace
        ui.onKey({ key: '', domEvent: { keyCode: 8 } });
        expect(ui.inputBuffer).toBe('ab');
        expect(ui.term.write).toHaveBeenCalledWith('\b \b');

        // Simulate Enter
        const onEnterMock = jest.fn();
        ui.onEnter = onEnterMock;
        ui.onKey({ key: '', domEvent: { keyCode: 13 } });
        expect(onEnterMock).toHaveBeenCalledWith('ab');
        expect(ui.inputBuffer).toBe('');
    });

    test('should display game state', () => {
        const mockState = {
            round_marker: 1,
            current_phase: 'ACTION_PHASE',
            public_mood: 0,
            log: ['Test log message'],
            players: [
                { id: 0, name: 'Human', archetype: { title: 'The Populist' }, pc: 25, current_office: null },
                { id: 1, name: 'AI-1', archetype: { title: 'The Fundraiser' }, pc: 25, current_office: null }
            ],
            current_player: 'Human',
            action_points: { 0: 2, 1: 2 }
        };
        ui.displayGameState(mockState);
        expect(ui.term.writeln).toHaveBeenCalledWith(expect.stringContaining('ELECTION: THE GAME'));
        expect(ui.term.writeln).toHaveBeenCalledWith(expect.stringContaining('Game Progress'));
        expect(ui.term.writeln).toHaveBeenCalledWith(expect.stringContaining('Test log message'));
        expect(ui.term.writeln).toHaveBeenCalledWith(expect.stringContaining('Human (The Populist)'));
        expect(ui.term.writeln).toHaveBeenCalledWith(expect.stringContaining("Human's Turn"));
    });

    test('should display available actions', () => {
        const mockActions = [
            { action_type: 'ActionFundraise' },
            { action_type: 'ActionPassTurn' }
        ];
        ui.promptForAction(mockActions);
        expect(ui.term.writeln).toHaveBeenCalledWith(expect.stringContaining('Available Actions'));
        expect(ui.term.writeln).toHaveBeenCalledWith(expect.stringContaining('Fundraise'));
        expect(ui.term.writeln).toHaveBeenCalledWith(expect.stringContaining('Pass Turn'));
        expect(ui.term.write).toHaveBeenCalledWith(expect.stringContaining('Enter your choice:'));
    });
}); 