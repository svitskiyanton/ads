#!/usr/bin/env python3
"""
Debug script to determine if login redirect is JavaScript or server-side
"""

import asyncio
from playwright.async_api import async_playwright
import logging
from config import CAPTCHA_API_KEY
from twocaptcha import TwoCaptcha

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedirectAnalyzer:
    def __init__(self):
        self.network_logs = []
        self.js_logs = []
        self.redirects = []
        
    def log_request(self, request):
        """Log all network requests"""
        self.network_logs.append({
            'type': 'request',
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers),
            'post_data': request.post_data
        })
        
        if request.method == "POST":
            logger.info(f"📤 POST: {request.url}")
            if request.post_data:
                logger.info(f"   Data: {request.post_data[:200]}...")
    
    def log_response(self, response):
        """Log all responses, especially redirects"""
        self.network_logs.append({
            'type': 'response',
            'status': response.status,
            'url': response.url,
            'headers': dict(response.headers)
        })
        
        # Check for redirects
        if 300 <= response.status < 400:
            location = response.headers.get('location', '')
            logger.info(f"🔄 REDIRECT {response.status}: {response.url} → {location}")
            self.redirects.append({
                'from': response.url,
                'to': location,
                'status': response.status,
                'type': 'server'
            })
        
        if "passport.orbita.co.il" in response.url:
            logger.info(f"🚨 LOGIN PAGE RESPONSE: {response.status} - {response.url}")
    
    def log_console(self, msg):
        """Log console messages for JS errors/redirects"""
        self.js_logs.append({
            'type': msg.type,
            'text': msg.text,
            'location': f"{msg.location.get('url', '')}:{msg.location.get('lineNumber', '')}"
        })
        
        # Look for redirect-related JS
        if any(keyword in msg.text.lower() for keyword in ['redirect', 'location', 'href', 'login']):
            logger.info(f"🔍 JS LOG: {msg.type} - {msg.text}")
    
    async def analyze_submission(self):
        """Analyze what happens during form submission"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            # Setup monitoring
            page.on("request", self.log_request)
            page.on("response", self.log_response)
            page.on("console", self.log_console)
            
            # Monitor page navigation
            page.on("framenavigated", lambda frame: logger.info(f"🧭 NAVIGATION: {frame.url}"))
            
            try:
                logger.info("🔍 Starting redirect analysis...")
                
                # Go to form page
                await page.goto("https://doska.orbita.co.il/my/add/")
                await page.wait_for_load_state('networkidle')
                
                # Fill form quickly (to trigger potential JS security)
                logger.info("📝 Filling form...")
                await page.select_option('select[name="board"]', label="Отдых")
                
                textareas = await page.locator('textarea[name="info"]').all()
                if textareas:
                    await textareas[0].fill("Отдохну")
                
                await page.fill('input[name="email"]', "111@gmail.com")
                await page.check('input[name="terms"]')
                
                # Solve captcha
                logger.info("🤖 Solving captcha...")
                site_key = await page.get_attribute('[data-sitekey]', 'data-sitekey')
                if site_key:
                    solver = TwoCaptcha(CAPTCHA_API_KEY)
                    result = solver.recaptcha(sitekey=site_key, url=page.url, version='v2')
                    if result and 'code' in result:
                        await page.evaluate(f"""
                            document.getElementById('g-recaptcha-response').value = '{result['code']}';
                        """)
                        logger.info("✅ Captcha solved")
                
                # Monitor JavaScript before submission
                logger.info("🔍 Checking for pre-submit JavaScript...")
                js_state = await page.evaluate("""
                    () => {
                        // Check for common redirect functions
                        return {
                            hasWindowLocation: typeof window.location !== 'undefined',
                            hasRedirectFunctions: typeof redirect !== 'undefined' || typeof redirectToLogin !== 'undefined',
                            formValidation: typeof validateForm !== 'undefined',
                            currentUrl: window.location.href,
                            jsErrors: window.jsErrors || []
                        };
                    }
                """)
                logger.info(f"📊 JS State: {js_state}")
                
                # CRITICAL: Monitor what happens during submission
                logger.info("🚨 SUBMITTING FORM - MONITORING CLOSELY...")
                
                # Set up a promise to catch immediate redirects
                redirect_promise = page.wait_for_url(lambda url: "passport.orbita.co.il" in url, timeout=5000)
                
                try:
                    # Submit form
                    await page.click('#submit_but')
                    logger.info("✅ Submit button clicked")
                    
                    # Wait for either redirect or normal response
                    try:
                        await redirect_promise
                        logger.info("🚨 CAUGHT IMMEDIATE REDIRECT TO LOGIN!")
                        
                        # Check if it was JS redirect
                        redirect_info = await page.evaluate("""
                            () => {
                                return {
                                    referrer: document.referrer,
                                    currentUrl: window.location.href,
                                    redirectedBy: window.redirectedBy || 'unknown'
                                };
                            }
                        """)
                        logger.info(f"🔍 Redirect info: {redirect_info}")
                        
                    except:
                        logger.info("⏳ No immediate redirect - waiting for response...")
                        await page.wait_for_timeout(3000)
                
                except Exception as e:
                    logger.warning(f"Submission error: {e}")
                
                # Final analysis
                await self.analyze_results(page)
                
                input("Press ENTER to close browser...")
                
            except Exception as e:
                logger.error(f"Analysis error: {e}")
            finally:
                await browser.close()
    
    async def analyze_results(self, page):
        """Analyze the collected data"""
        logger.info("\n" + "="*50)
        logger.info("📊 REDIRECT ANALYSIS RESULTS")
        logger.info("="*50)
        
        # Check network redirects
        server_redirects = [r for r in self.redirects if r['type'] == 'server']
        if server_redirects:
            logger.info(f"🔧 SERVER REDIRECTS FOUND: {len(server_redirects)}")
            for redirect in server_redirects:
                logger.info(f"   {redirect['from']} → {redirect['to']} (HTTP {redirect['status']})")
        else:
            logger.info("🔧 NO SERVER REDIRECTS FOUND")
        
        # Check for JS redirects
        current_url = page.url
        if "passport.orbita.co.il" in current_url:
            if not server_redirects:
                logger.info("🔍 LIKELY JAVASCRIPT REDIRECT (no server redirect detected)")
            else:
                logger.info("🔍 REDIRECT VIA SERVER RESPONSE")
        
        # Check POST requests
        post_requests = [log for log in self.network_logs if log.get('method') == 'POST' and 'my/add' in log.get('url', '')]
        if post_requests:
            logger.info(f"📤 FORM SUBMISSION DETECTED: {len(post_requests)} POST requests")
            for req in post_requests:
                logger.info(f"   POST to: {req['url']}")
        else:
            logger.info("📤 NO FORM SUBMISSION DETECTED - BLOCKED BY JS?")
        
        logger.info("="*50)

async def main():
    if not CAPTCHA_API_KEY or CAPTCHA_API_KEY == "YOUR_API_KEY_HERE":
        logger.error("Please set your 2captcha API key in config.py!")
        return
    
    analyzer = RedirectAnalyzer()
    await analyzer.analyze_submission()

if __name__ == "__main__":
    asyncio.run(main()) 