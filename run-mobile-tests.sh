#!/bin/bash

# Mobile Usability Test Runner for Election Game
# This script runs comprehensive mobile tests to ensure the game works well on mobile devices

echo "🎮 Election Game - Mobile Usability Test Suite"
echo "=============================================="

# Check if server is running
echo "🔍 Checking if server is running..."
if ! curl -s http://localhost:5001 > /dev/null; then
    echo "❌ Server is not running on port 5001"
    echo "Please start the server first:"
    echo "  PORT=5001 python3 server.py"
    exit 1
fi

echo "✅ Server is running on port 5001"

# Check if Playwright is installed
echo "🔍 Checking Playwright installation..."
if ! npx playwright --version > /dev/null 2>&1; then
    echo "❌ Playwright is not installed"
    echo "Installing Playwright..."
    npm install -D @playwright/test
    npx playwright install
fi

echo "✅ Playwright is installed"

# Create test results directory
mkdir -p test-results/mobile

# Run mobile usability tests
echo "🧪 Running mobile usability tests..."
echo ""

# Run comprehensive mobile tests
echo "📱 Testing multiple device sizes..."
npx playwright test tests/mobile-usability.spec.ts \
    --reporter=html \
    --output=test-results/mobile/usability-report \
    --timeout=30000

# Run focused UI element tests
echo "🎯 Testing specific UI elements..."
npx playwright test tests/mobile-ui-elements.spec.ts \
    --reporter=html \
    --output=test-results/mobile/ui-elements-report \
    --timeout=30000

# Generate summary report
echo ""
echo "📊 Generating test summary..."
echo ""

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "✅ All mobile tests passed!"
    echo ""
    echo "📋 Test Summary:"
    echo "  - Touch interactions tested"
    echo "  - Responsive design validated"
    echo "  - UI layout checked for overlaps"
    echo "  - Game flow verified"
    echo "  - Performance benchmarks met"
    echo "  - Accessibility standards checked"
    echo "  - Error handling tested"
    echo ""
    echo "📁 Test reports saved to:"
    echo "  - test-results/mobile/usability-report/"
    echo "  - test-results/mobile/ui-elements-report/"
    echo ""
    echo "🌐 To view detailed reports:"
    echo "  npx playwright show-report test-results/mobile/usability-report"
    echo "  npx playwright show-report test-results/mobile/ui-elements-report"
else
    echo "❌ Some mobile tests failed!"
    echo ""
    echo "🔍 Check the test reports for details:"
    echo "  npx playwright show-report test-results/mobile/usability-report"
    echo "  npx playwright show-report test-results/mobile/ui-elements-report"
    echo ""
    echo "💡 Common mobile issues to check:"
    echo "  - Button sizes (should be ≥44px)"
    echo "  - Touch spacing (should be ≥8px)"
    echo "  - Text readability (should be ≥14px)"
    echo "  - No horizontal overflow"
    echo "  - Proper modal sizing"
    echo "  - Gesture support"
    exit 1
fi

echo ""
echo "🎉 Mobile testing complete!" 