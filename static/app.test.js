/**
 * @jest-environment jsdom
 */

const { JSDOM } = require('jsdom');
const { Terminal } = require('xterm');
const { TerminalUI } = require('./app');

// Mock the Terminal class
jest.mock('xterm', () => {
    const mockTerminal = {
        loadAddon: jest.fn(),
        open: jest.fn(),
        writeln: jest.fn(),
        write: jest.fn(),
        onData: jest.fn(),
        onKey: jest.fn(),
    };
    return {
        Terminal: jest.fn(() => mockTerminal),
    };
});

// Mock the FitAddon class
class FitAddon {
    fit = jest.fn();
}

global.window = new JSDOM().window;
global.document = window.document;
global.HTMLElement = window.HTMLElement;
const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;
require('jest-fetch-mock').enableMocks();


describe('TerminalUI', () => {
    let ui;

    beforeEach(() => {
        document.body.innerHTML = '<div id="terminal-container"></div>';
        ui = new TerminalUI();
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('should initialize the terminal', () => {
        expect(Terminal).toHaveBeenCalledTimes(2);
        expect(ui.term.loadAddon).toHaveBeenCalledTimes(2);
        expect(ui.term.open).toHaveBeenCalledWith(document.getElementById('terminal-container'));
    });

    test('should write to the terminal', () => {
        ui.term.writeln('Hello, world!');
        expect(ui.term.writeln).toHaveBeenCalledWith('Hello, world!');
    });
}); 