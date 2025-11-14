#!/usr/bin/env node
/**
 * Screenshot Capture Script for TidySnap Flutter Web App
 *
 * This script automatically:
 * 1. Finds the running Flutter app port
 * 2. Reads test credentials from .env
 * 3. Logs in to the app
 * 4. Captures screenshots of authenticated pages
 * 5. Saves screenshots to review_screenshots/
 *
 * Usage:
 *     npx playwright install chromium  # One-time setup
 *     node .claude/scripts/capture_screenshots.js
 *
 * Requirements:
 *     - Flutter app must be running (flutter run -d chrome)
 *     - Playwright browsers installed (npx playwright install chromium)
 *     - .env file must contain TEST_EMAIL and TEST_PASSWORD
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/** Read .env file and parse variables */
function readEnv() {
    const envPath = '.env';
    if (!fs.existsSync(envPath)) {
        console.error('❌ ERROR: .env file not found');
        return null;
    }

    const envContent = fs.readFileSync(envPath, 'utf-8');
    const env = {};

    envContent.split('\n').forEach(line => {
        line = line.trim();
        if (line && !line.startsWith('#') && line.includes('=')) {
            const [key, ...valueParts] = line.split('=');
            env[key] = valueParts.join('=');
        }
    });

    return env;
}

/** Find the port of running Flutter web app */
function findFlutterPort() {
    try {
        // Look for flutter run process with port
        const psOutput = execSync('ps aux').toString();
        const portMatch = psOutput.match(/localhost:(\d+)/);

        if (portMatch) {
            return portMatch[1];
        }

        // Try common ports
        for (const port of ['45419', '8080', '3000', '5000']) {
            try {
                execSync(`curl -s http://localhost:${port}`, { timeout: 2000 });
                return port;
            } catch (e) {
                // Port not responding
            }
        }

        return null;
    } catch (error) {
        console.error(`❌ Error finding port: ${error.message}`);
        return null;
    }
}

/** Capture authenticated screenshots using Playwright */
async function captureScreenshots(url, testEmail, testPassword, outputDir = 'review_screenshots') {
    // Create output directory
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    console.log(`📸 Starting screenshot capture...`);
    console.log(`   URL: ${url}`);
    console.log(`   Email: ${testEmail}`);
    console.log(`   Output: ${outputDir}/`);

    let browser;
    try {
        // Launch browser
        browser = await chromium.launch({ headless: true });
        const page = await browser.newPage();

        // Navigate to app
        console.log(`\n1️⃣  Loading app at ${url}...`);
        await page.goto(url, { timeout: 30000 });
        await page.waitForLoadState('networkidle', { timeout: 15000 });

        // Screenshot 1: Login screen
        const loginScreenshot = path.join(outputDir, '01_login_screen.png');
        await page.screenshot({ path: loginScreenshot });
        console.log(`   ✅ Captured: ${loginScreenshot}`);

        // Try to login
        console.log(`\n2️⃣  Attempting login with ${testEmail}...`);

        try {
            // Find and fill email field
            await page.fill('input[type="email"]', testEmail);
            console.log(`   ✓ Filled email`);

            // Find and fill password field
            await page.fill('input[type="password"]', testPassword);
            console.log(`   ✓ Filled password`);

            // Click login button
            await page.click('button[type="submit"]');
            console.log(`   ✓ Clicked login button`);

            // Wait for navigation to home/dashboard
            console.log(`   ⏳ Waiting for navigation...`);
            await page.waitForURL('**/home', { timeout: 15000 });
            await page.waitForLoadState('networkidle', { timeout: 10000 });

            // Screenshot 2: Authenticated dashboard
            const dashboardScreenshot = path.join(outputDir, '02_dashboard_authenticated.png');
            await page.screenshot({ path: dashboardScreenshot });
            console.log(`   ✅ Captured: ${dashboardScreenshot}`);

            // Screenshot 3: Full page
            const fullpageScreenshot = path.join(outputDir, '03_dashboard_fullpage.png');
            await page.screenshot({ path: fullpageScreenshot, fullPage: true });
            console.log(`   ✅ Captured: ${fullpageScreenshot}`);

            console.log(`\n✅ SUCCESS: All screenshots captured!`);
            return true;

        } catch (error) {
            console.log(`\n⚠️  Login failed: ${error.message}`);
            console.log(`   Only login screen captured`);
            return false;
        }

    } catch (error) {
        console.error(`\n❌ ERROR: ${error.message}`);
        return false;
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

/** Main execution */
async function main() {
    console.log('='.repeat(60));
    console.log('🎬 TidySnap Screenshot Capture Tool');
    console.log('='.repeat(60));

    // Read .env
    console.log('\n📋 Reading .env file...');
    const env = readEnv();
    if (!env) {
        process.exit(1);
    }

    const testEmail = env.TEST_EMAIL;
    const testPassword = env.TEST_PASSWORD;

    if (!testEmail || !testPassword) {
        console.error('❌ ERROR: TEST_EMAIL or TEST_PASSWORD not found in .env');
        process.exit(1);
    }

    console.log(`   ✓ TEST_EMAIL: ${testEmail}`);
    console.log(`   ✓ TEST_PASSWORD: ${'*'.repeat(testPassword.length)}`);

    // Find Flutter port
    console.log('\n🔍 Finding Flutter app...');
    const port = findFlutterPort();
    if (!port) {
        console.error('❌ ERROR: Cannot find running Flutter app');
        console.error('   Make sure Flutter app is running: flutter run -d chrome --release');
        process.exit(1);
    }

    const url = `http://localhost:${port}`;
    console.log(`   ✓ Found app at: ${url}`);

    // Capture screenshots
    const success = await captureScreenshots(url, testEmail, testPassword);

    // Summary
    console.log('\n' + '='.repeat(60));
    if (success) {
        console.log('✅ COMPLETE: Screenshots saved to review_screenshots/');
        console.log('\nNext steps:');
        console.log('   1. Review screenshots: ls -lh review_screenshots/');
        console.log('   2. Run spec-implementation-reviewer agent');
    } else {
        console.log('⚠️  PARTIAL: Only login screen captured');
        console.log('\nTroubleshooting:');
        console.log('   - Check if test credentials are correct in .env');
        console.log('   - Check if app login flow has changed');
        console.log('   - Try manual login to verify credentials');
    }
    console.log('='.repeat(60));

    process.exit(success ? 0 : 1);
}

// Run main
main().catch(error => {
    console.error('❌ Fatal error:', error);
    process.exit(1);
});
