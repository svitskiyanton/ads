#!/usr/bin/env python3
"""
Test script for 2captcha integration with Orbita classified ads form
Fills a simple ad to test captcha solving before implementing in main script
"""

import asyncio
import time
from playwright.async_api import async_playwright
import logging
from config import CAPTCHA_API_KEY
from twocaptcha import TwoCaptcha
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PageStateRecorder:
    """Records all page states, network requests, and form changes for debugging"""
    
    def __init__(self, session_name="debug_session"):
        self.session_name = session_name
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = f"debug_logs/{session_name}_{self.timestamp}"
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.network_requests = []
        self.form_states = []
        self.page_snapshots = []
        self.console_logs = []
        
        logger.info(f"📋 Recording session data to: {self.log_dir}")
    
    async def setup_page_monitoring(self, page):
        """Setup comprehensive page monitoring"""
        
        # Monitor network requests
        page.on("request", self._on_request)
        page.on("response", self._on_response)
        page.on("requestfailed", self._on_request_failed)
        
        # Monitor console logs
        page.on("console", self._on_console)
        
        # Monitor page errors
        page.on("pageerror", self._on_page_error)
        
        logger.info("🔍 Page monitoring setup complete")
    
    def _on_request(self, request):
        """Record outgoing requests"""
        request_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "request",
            "url": request.url,
            "method": request.method,
            "headers": dict(request.headers),
            "post_data": request.post_data if request.post_data else None
        }
        self.network_requests.append(request_data)
        
        if request.method == "POST":
            logger.info(f"📤 POST Request: {request.url}")
            if request.post_data:
                logger.info(f"   Data: {request.post_data[:200]}...")
    
    def _on_response(self, response):
        """Record responses"""
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "response",
            "url": response.url,
            "status": response.status,
            "headers": dict(response.headers)
        }
        self.network_requests.append(response_data)
        
        if response.status >= 300:
            logger.info(f"📥 Response: {response.url} - Status: {response.status}")
    
    def _on_request_failed(self, request):
        """Record failed requests"""
        logger.warning(f"❌ Request failed: {request.url} - {request.failure}")
    
    def _on_console(self, msg):
        """Record console messages"""
        console_data = {
            "timestamp": datetime.now().isoformat(),
            "type": msg.type,
            "text": msg.text,
            "location": f"{msg.location.get('url', '')}:{msg.location.get('lineNumber', '')}"
        }
        self.console_logs.append(console_data)
        
        if msg.type in ["error", "warning"]:
            logger.info(f"🖥️  Console {msg.type}: {msg.text}")
    
    def _on_page_error(self, error):
        """Record page errors"""
        logger.error(f"💥 Page error: {error}")
    
    async def capture_form_state(self, page, state_name):
        """Capture complete form state at a specific moment"""
        try:
            form_data = await page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form');
                    const formStates = [];
                    
                    forms.forEach((form, formIndex) => {
                        const formData = new FormData(form);
                        const data = {};
                        
                        // Get all form data
                        for (let [key, value] of formData.entries()) {
                            data[key] = value.toString();
                        }
                        
                        // Get all input elements (including unchecked checkboxes)
                        const allInputs = form.querySelectorAll('input, textarea, select');
                        const inputStates = [];
                        
                        allInputs.forEach(input => {
                            inputStates.push({
                                tagName: input.tagName,
                                type: input.type || '',
                                name: input.name || '',
                                id: input.id || '',
                                value: input.value || '',
                                checked: input.checked || false,
                                selected: input.selected || false,
                                disabled: input.disabled || false,
                                className: input.className || '',
                                placeholder: input.placeholder || ''
                            });
                        });
                        
                        formStates.push({
                            formIndex: formIndex,
                            action: form.action || '',
                            method: form.method || 'GET',
                            formData: data,
                            inputStates: inputStates
                        });
                    });
                    
                    return {
                        url: window.location.href,
                        title: document.title,
                        forms: formStates,
                        cookies: document.cookie
                    };
                }
            """)
            
            state_record = {
                "timestamp": datetime.now().isoformat(),
                "state_name": state_name,
                "data": form_data
            }
            
            self.form_states.append(state_record)
            
            # Save to file immediately
            with open(f"{self.log_dir}/form_state_{state_name}.json", "w", encoding="utf-8") as f:
                json.dump(state_record, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📸 Captured form state: {state_name}")
            
            # Log key form data
            for form in form_data['forms']:
                logger.info(f"   Form {form['formIndex']}: {len(form['formData'])} fields")
                for key, value in form['formData'].items():
                    if len(str(value)) > 50:
                        logger.info(f"     {key}: {str(value)[:50]}... ({len(str(value))} chars)")
                    else:
                        logger.info(f"     {key}: {value}")
            
        except Exception as e:
            logger.error(f"Error capturing form state: {e}")
    
    async def capture_page_snapshot(self, page, snapshot_name):
        """Capture full page snapshot"""
        try:
            # Take screenshot
            screenshot_path = f"{self.log_dir}/screenshot_{snapshot_name}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            
            # Save HTML
            html_content = await page.content()
            html_path = f"{self.log_dir}/page_{snapshot_name}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info(f"📷 Page snapshot saved: {snapshot_name}")
            
        except Exception as e:
            logger.error(f"Error taking page snapshot: {e}")
    
    def save_session_summary(self):
        """Save complete session summary"""
        try:
            summary = {
                "session_name": self.session_name,
                "timestamp": self.timestamp,
                "network_requests": len(self.network_requests),
                "form_states": len(self.form_states),
                "console_logs": len(self.console_logs),
                "all_network_requests": self.network_requests,
                "all_console_logs": self.console_logs
            }
            
            with open(f"{self.log_dir}/session_summary.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Session summary saved to: {self.log_dir}/session_summary.json")
            logger.info(f"📊 Summary: {len(self.network_requests)} network requests, {len(self.form_states)} form states")
            
        except Exception as e:
            logger.error(f"Error saving session summary: {e}")

class OrbitaTestFormFiller:
    """Simple form filler for testing 2captcha integration"""
    
    def __init__(self, captcha_api_key):
        self.captcha_api_key = captcha_api_key
        self.site_url = "https://doska.orbita.co.il/my/add/"
        self.recorder = PageStateRecorder("orbita_test")
    
    async def fill_test_form(self):
        """Fill the test form with specified values and solve captcha"""
        async with async_playwright() as p:
            # Launch browser with clean profile (no persistent cookies)
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-first-run',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create new context with clean state
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='ru-RU',
                timezone_id='Europe/Moscow'
            )
            
            page = await context.new_page()
            
            try:
                logger.info("Starting with completely clean browser session...")
                
                # Setup comprehensive monitoring
                await self.recorder.setup_page_monitoring(page)
                
                # Clear any existing cookies/storage
                await context.clear_cookies()
                await context.clear_permissions()
                
                # Try to clear storage (but handle security restrictions)
                try:
                    await page.evaluate("""
                        () => {
                            try {
                                // Clear all storage types
                                localStorage.clear();
                                sessionStorage.clear();
                                console.log('Cleared localStorage and sessionStorage');
                            } catch (e) {
                                console.log('Could not clear storage (security restriction):', e.message);
                            }
                            
                            return true;
                        }
                    """)
                except Exception as e:
                    logger.warning(f"Could not clear localStorage (security restriction): {e}")
                
                logger.info(f"Navigating to {self.site_url}")
                await page.goto(self.site_url)
                await page.wait_for_load_state('networkidle')
                
                # Wait a bit for page to fully load and initialize
                await page.wait_for_timeout(3000)
                
                # 📸 CAPTURE: Initial page state
                await self.recorder.capture_form_state(page, "01_initial_page_load")
                await self.recorder.capture_page_snapshot(page, "01_initial_page_load")
                
                # First, analyze the entire form structure
                logger.info("Analyzing form structure...")
                await self._analyze_form_structure(page)
                
                # Step 1: Select board 'Отдых'
                logger.info("Selecting board: Отдых")
                await self._select_board(page, "Отдых")
                await page.wait_for_timeout(2000)  # Wait for any dynamic loading
                
                # 📸 CAPTURE: After board selection
                await self.recorder.capture_form_state(page, "02_after_board_selection")
                
                # Step 2: Fill the form fields
                logger.info("Filling form fields...")
                await self._fill_form_fields(page)
                await page.wait_for_timeout(2000)
                
                # 📸 CAPTURE: After form fields filled
                await self.recorder.capture_form_state(page, "03_after_form_fields")
                
                # Step 3: Check terms agreement
                logger.info("Checking terms agreement...")
                await self._check_terms_agreement(page)
                await page.wait_for_timeout(1000)
                
                # 📸 CAPTURE: After terms agreement
                await self.recorder.capture_form_state(page, "04_after_terms_agreement")
                
                # Analyze form data before captcha
                logger.info("Form data before captcha:")
                await self._analyze_current_form_data(page)
                
                # Step 4: Solve reCAPTCHA
                logger.info("Solving reCAPTCHA...")
                await self._solve_captcha(page)
                
                # 📸 CAPTURE: After captcha solved
                await self.recorder.capture_form_state(page, "05_after_captcha_solved")
                await self.recorder.capture_page_snapshot(page, "05_after_captcha_solved")
                
                # Analyze form data after captcha
                logger.info("Form data after captcha:")
                await self._analyze_current_form_data(page)
                
                # Wait a moment before submission
                await page.wait_for_timeout(2000)
                
                # 📸 CAPTURE: Just before submission
                await self.recorder.capture_form_state(page, "06_before_submission")
                
                # Step 5: Submit form
                logger.info("Submitting form...")
                await self._submit_form(page)
                
                # 📸 CAPTURE: After submission
                await page.wait_for_timeout(3000)  # Wait for redirect/response
                await self.recorder.capture_form_state(page, "07_after_submission")
                await self.recorder.capture_page_snapshot(page, "07_after_submission")
                
                logger.info("Form submitted successfully!")
                
                # Save session summary
                self.recorder.save_session_summary()
                
                # Keep browser open to view results
                logger.info("Browser will remain open for you to view the results...")
                logger.info("Close the browser window manually when you're done.")
                
            except Exception as e:
                logger.error(f"Error filling form: {e}")
                
                # 📸 CAPTURE: Error state
                await self.recorder.capture_form_state(page, "99_error_state")
                await self.recorder.capture_page_snapshot(page, "99_error_state")
                self.recorder.save_session_summary()
                
                # Even on error, keep browser open for debugging
                logger.info("Browser will remain open for debugging...")
                logger.info("Close the browser window manually when you're done.")
                raise
            
            # Wait indefinitely (until user closes browser)
            try:
                while True:
                    await page.wait_for_timeout(10000)  # Check every 10 seconds
                    # Check if page is still alive
                    if page.is_closed():
                        break
            except:
                # Browser was closed or other error
                pass
            # Note: browser.close() removed - browser stays open
    
    async def _clear_browser_state(self, page):
        """Clear all browser state (cookies, storage) for clean session"""
        try:
            logger.info("🧹 Clearing browser state...")
            
            # Clear context-level data
            context = page.context
            await context.clear_cookies()
            await context.clear_permissions()
            
            # Clear page-level storage
            await page.evaluate("""
                () => {
                    try {
                        // Clear all storage types
                        localStorage.clear();
                        sessionStorage.clear();
                        console.log('Cleared localStorage and sessionStorage');
                    } catch (e) {
                        console.log('Could not clear storage (security restriction):', e.message);
                    }
                    
                    return true;
                }
            """)
            
            logger.info("✅ Browser state cleared")
            
        except Exception as e:
            logger.warning(f"Error clearing browser state: {e}")
    
    async def _analyze_form_structure(self, page):
        """Analyze the complete form structure to understand what fields exist"""
        try:
            form_analysis = await page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form');
                    return Array.from(forms).map(form => {
                        const inputs = form.querySelectorAll('input, textarea, select');
                        return {
                            action: form.action,
                            method: form.method,
                            fields: Array.from(inputs).map(field => ({
                                tagName: field.tagName,
                                type: field.type || 'text',
                                name: field.name,
                                id: field.id,
                                value: field.value,
                                placeholder: field.placeholder,
                                required: field.required,
                                className: field.className,
                                hidden: field.type === 'hidden' || field.style.display === 'none'
                            }))
                        };
                    });
                }
            """)
            
            logger.info("=== FORM STRUCTURE ANALYSIS ===")
            for i, form in enumerate(form_analysis):
                logger.info(f"Form {i+1}: action={form['action']}, method={form['method']}")
                logger.info(f"  Total fields: {len(form['fields'])}")
                
                # Group fields by type
                visible_fields = [f for f in form['fields'] if not f['hidden']]
                hidden_fields = [f for f in form['fields'] if f['hidden']]
                
                logger.info(f"  Visible fields ({len(visible_fields)}):")
                for field in visible_fields:
                    logger.info(f"    {field['tagName']}: name='{field['name']}', type='{field['type']}', id='{field['id']}', placeholder='{field['placeholder']}'")
                
                logger.info(f"  Hidden fields ({len(hidden_fields)}):")
                for field in hidden_fields:
                    logger.info(f"    {field['tagName']}: name='{field['name']}', value='{field['value'][:50]}...' ({len(field['value'])} chars)")
            
            logger.info("=== END FORM ANALYSIS ===")
            
        except Exception as e:
            logger.error(f"Error analyzing form structure: {e}")
    
    async def _analyze_current_form_data(self, page):
        """Analyze current form data to see what values are set"""
        try:
            form_data = await page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form');
                    return Array.from(forms).map(form => {
                        const formData = new FormData(form);
                        const data = {};
                        for (let [key, value] of formData.entries()) {
                            data[key] = value.toString().substring(0, 100); // Limit length for logging
                        }
                        return data;
                    });
                }
            """)
            
            logger.info("=== CURRENT FORM DATA ===")
            for i, data in enumerate(form_data):
                logger.info(f"Form {i+1} data:")
                for key, value in data.items():
                    if len(value) > 50:
                        logger.info(f"  {key}: {value[:50]}... ({len(value)} chars)")
                    else:
                        logger.info(f"  {key}: {value}")
            logger.info("=== END FORM DATA ===")
            
        except Exception as e:
            logger.error(f"Error analyzing form data: {e}")
    
    async def _select_board(self, page, board_name):
        """Select the specified board from dropdown"""
        # Try different selectors for board selection
        board_selectors = [
            'select[name="board_id"]',
            'select[name="board"]',
            '#board_id',
            'select.form-control'
        ]
        
        for selector in board_selectors:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                await page.select_option(selector, label=board_name)
                logger.info(f"Selected board '{board_name}' using selector: {selector}")
                return
            except:
                continue
        
        # If dropdown selection fails, try clicking approach
        try:
            board_element = await page.locator(f"text={board_name}").first
            await board_element.click()
            logger.info(f"Selected board '{board_name}' by clicking")
        except:
            logger.warning(f"Could not select board '{board_name}' - proceeding anyway")
    
    async def _fill_form_fields(self, page):
        """Fill the form fields with test data"""
        # Fill ad text (first textarea with name="info")
        try:
            # Let's be more specific about finding the right fields
            logger.info("Looking for form fields...")
            
            # Find all textareas and inputs to understand the structure
            all_fields = await page.evaluate("""
                () => {
                    const textareas = document.querySelectorAll('textarea');
                    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input:not([type])');
                    
                    const fields = [];
                    textareas.forEach((el, idx) => {
                        fields.push({
                            type: 'textarea',
                            index: idx,
                            name: el.name,
                            id: el.id,
                            placeholder: el.placeholder,
                            className: el.className,
                            value: el.value
                        });
                    });
                    
                    inputs.forEach((el, idx) => {
                        fields.push({
                            type: 'input',
                            inputType: el.type,
                            index: idx,
                            name: el.name,
                            id: el.id,
                            placeholder: el.placeholder,
                            className: el.className,
                            value: el.value
                        });
                    });
                    
                    return fields;
                }
            """)
            
            logger.info("Available form fields:")
            for field in all_fields:
                logger.info(f"  {field['type']}: name='{field['name']}', id='{field['id']}', placeholder='{field['placeholder']}'")
            
            # Fill the ad text in the first textarea with name="info"
            info_textareas = await page.locator('textarea[name="info"]').all()
            if len(info_textareas) >= 1:
                await info_textareas[0].fill("Отдохну")
                logger.info("✅ Filled ad text: Отдохну")
            else:
                # Try alternative selectors for ad text
                ad_text_selectors = [
                    'textarea[placeholder*="текст"]',
                    'textarea[placeholder*="объявления"]',
                    'textarea.form-control',
                    'textarea:first-of-type'
                ]
                
                filled = False
                for selector in ad_text_selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.count() > 0:
                            await element.fill("Отдохну")
                            logger.info(f"✅ Filled ad text using selector: {selector}")
                            filled = True
                            break
                    except:
                        continue
                
                if not filled:
                    logger.warning("❌ Could not find ad text field")
            
            # Fill email field
            email_filled = False
            
            # First try second textarea with name="info"
            if len(info_textareas) >= 2:
                await info_textareas[1].fill("111@gmail.com")
                logger.info("✅ Filled email in second info textarea: 111@gmail.com")
                email_filled = True
            else:
                # Try to find email field by other selectors
                email_selectors = [
                    'input[name="email"]',
                    'input[type="email"]',
                    'input[placeholder*="email"]',
                    'input[placeholder*="почта"]',
                    'textarea[placeholder*="email"]',
                    'textarea[placeholder*="почта"]'
                ]
                
                for selector in email_selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.count() > 0:
                            await element.fill("111@gmail.com")
                            logger.info(f"✅ Filled email using selector: {selector}")
                            email_filled = True
                            break
                    except:
                        continue
            
            if not email_filled:
                logger.warning("❌ Could not find email field")
            
            # Also try to fill any other required fields that might exist
            await self._fill_additional_required_fields(page)
                        
        except Exception as e:
            logger.warning(f"Error filling form fields: {e}")
    
    async def _fill_additional_required_fields(self, page):
        """Fill any additional required fields that might be needed"""
        try:
            # Check for city/location fields
            city_selectors = [
                'select[name*="city"]',
                'select[name*="location"]',
                'input[name*="city"]',
                'input[name*="location"]'
            ]
            
            for selector in city_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        if selector.startswith('select'):
                            # Try to select a city option
                            options = await page.evaluate(f"""
                                () => {{
                                    const select = document.querySelector('{selector}');
                                    if (select) {{
                                        return Array.from(select.options).map(opt => ({{
                                            value: opt.value,
                                            text: opt.text
                                        }}));
                                    }}
                                    return [];
                                }}
                            """)
                            
                            if options:
                                # Try to find "Ришон ле Цион" or similar
                                for option in options:
                                    if "ришон" in option['text'].lower() or "rishon" in option['text'].lower():
                                        await page.select_option(selector, value=option['value'])
                                        logger.info(f"✅ Selected city: {option['text']}")
                                        break
                                else:
                                    # Just select the first non-empty option
                                    if len(options) > 1:
                                        await page.select_option(selector, index=1)
                                        logger.info(f"✅ Selected default city option")
                        else:
                            await element.fill("Ришон ле Цион")
                            logger.info(f"✅ Filled city field: Ришон ле Цион")
                        break
                except:
                    continue
            
            # Check for phone number fields
            phone_selectors = [
                'input[name*="phone"]',
                'input[name*="tel"]',
                'input[type="tel"]'
            ]
            
            for selector in phone_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        await element.fill("0501234567")
                        logger.info(f"✅ Filled phone field")
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error filling additional fields: {e}")
    
    async def _check_terms_agreement(self, page):
        """Check the terms agreement checkbox"""
        try:
            terms_checkbox = page.locator('input[name="terms"]')
            await terms_checkbox.check()
            logger.info("Checked terms agreement checkbox")
        except Exception as e:
            logger.warning(f"Could not check terms agreement: {e}")
    
    async def _solve_captcha(self, page):
        """Solve reCAPTCHA using 2captcha service (same approach as main script)"""
        try:
            # Wait for reCAPTCHA to load
            await page.wait_for_selector('.g-recaptcha, [data-sitekey], .recaptcha-checkbox', timeout=10000)
            
            # Get site key
            site_key = await self._get_recaptcha_sitekey(page)
            if not site_key:
                raise Exception("Could not find reCAPTCHA site key")
            
            logger.info(f"Found reCAPTCHA site key: {site_key[:20]}...")
            
            # Initialize 2captcha solver (same as main script)
            solver = TwoCaptcha(self.captcha_api_key)
            
            # Get current page URL
            current_url = page.url
            logger.info(f"Page URL: {current_url}")
            
            # Submit reCAPTCHA to 2captcha
            logger.info("Submitting reCAPTCHA to 2captcha...")
            result = solver.recaptcha(
                sitekey=site_key,
                url=current_url,
                version='v2'
            )
            
            if result and 'code' in result:
                captcha_response = result['code']
                logger.info(f"reCAPTCHA solved! Token: {captcha_response[:50]}...")
                
                # Multiple injection methods to handle CSP issues
                await self._inject_captcha_response(page, captcha_response)
                
                # Wait for page to process the response
                await page.wait_for_timeout(3000)
                
                # Verify reCAPTCHA is solved
                verification_result = await self._verify_captcha_response(page)
                logger.info(f"Captcha verification: {verification_result}")
                
            else:
                raise Exception("Failed to solve reCAPTCHA - no valid response received")
                
        except Exception as e:
            logger.error(f"Error solving captcha: {e}")
            raise
    
    async def _inject_captcha_response(self, page, captcha_response):
        """Inject captcha response using multiple methods to handle CSP issues"""
        logger.info("Injecting reCAPTCHA response using multiple methods...")
        
        # Method 1: Direct DOM manipulation (most reliable)
        try:
            await page.evaluate(f"""
                () => {{
                    const responseElement = document.getElementById('g-recaptcha-response');
                    if (responseElement) {{
                        responseElement.innerHTML = '{captcha_response}';
                        responseElement.value = '{captcha_response}';
                        responseElement.style.display = '';
                        console.log('Method 1: Direct DOM injection successful');
                    }}
                    
                    // Set all hidden recaptcha response fields
                    const hiddenElements = document.querySelectorAll('[name="g-recaptcha-response"]');
                    hiddenElements.forEach(el => {{
                        el.value = '{captcha_response}';
                        console.log('Method 1: Hidden field set');
                    }});
                }}
            """)
            logger.info("✅ Method 1: Direct DOM injection completed")
        except Exception as e:
            logger.warning(f"Method 1 failed: {e}")
        
        # Method 2: Form data injection
        try:
            await page.evaluate(f"""
                () => {{
                    // Find the form and add hidden input if needed
                    const forms = document.querySelectorAll('form');
                    forms.forEach(form => {{
                        let existing = form.querySelector('[name="g-recaptcha-response"]');
                        if (!existing) {{
                            const input = document.createElement('input');
                            input.type = 'hidden';
                            input.name = 'g-recaptcha-response';
                            input.value = '{captcha_response}';
                            form.appendChild(input);
                            console.log('Method 2: Hidden input added to form');
                        }} else {{
                            existing.value = '{captcha_response}';
                            console.log('Method 2: Existing input updated');
                        }}
                    }});
                }}
            """)
            logger.info("✅ Method 2: Form data injection completed")
        except Exception as e:
            logger.warning(f"Method 2 failed: {e}")
        
        # Method 3: Global window variable (fallback)
        try:
            await page.evaluate(f"""
                () => {{
                    window.recaptchaResponse = '{captcha_response}';
                    if (window.grecaptcha) {{
                        window.grecaptcha.getResponse = function() {{ 
                            return '{captcha_response}'; 
                        }};
                        console.log('Method 3: Global variable and grecaptcha override set');
                    }}
                }}
            """)
            logger.info("✅ Method 3: Global variable injection completed")
        except Exception as e:
            logger.warning(f"Method 3 failed: {e}")
    
    async def _verify_captcha_response(self, page):
        """Verify that the captcha response was properly set"""
        try:
            result = await page.evaluate("""
                () => {
                    const responseElement = document.getElementById('g-recaptcha-response');
                    const hiddenElements = document.querySelectorAll('[name="g-recaptcha-response"]');
                    
                    return {
                        responseElementExists: !!responseElement,
                        responseElementValue: responseElement ? responseElement.value.length : 0,
                        hiddenElementsCount: hiddenElements.length,
                        hiddenElementsValues: Array.from(hiddenElements).map(el => el.value.length),
                        globalVariable: !!window.recaptchaResponse,
                        grecaptchaExists: !!window.grecaptcha
                    };
                }
            """)
            return result
        except Exception as e:
            logger.error(f"Error verifying captcha response: {e}")
            return {"error": str(e)}
    
    async def _get_recaptcha_sitekey(self, page):
        """Extract reCAPTCHA site key from the page (same approach as main script)"""
        try:
            # Try different methods to get the site key
            sitekey_selectors = [
                '[data-sitekey]',
                '.g-recaptcha[data-sitekey]',
                'div[data-sitekey]'
            ]
            
            for selector in sitekey_selectors:
                element = page.locator(selector).first
                if await element.count() > 0:
                    sitekey = await element.get_attribute('data-sitekey')
                    if sitekey:
                        return sitekey
            
            # If no sitekey found, try to extract from iframe src
            iframe_locator = page.locator('iframe[src*="recaptcha"]').first
            if await iframe_locator.count() > 0:
                iframe_src = await iframe_locator.get_attribute('src')
                if iframe_src and 'k=' in iframe_src:
                    sitekey = iframe_src.split('k=')[1].split('&')[0]
                    return sitekey
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting reCAPTCHA site key: {e}")
            return None
    
    async def _submit_form(self, page):
        """Submit the form with enhanced debugging"""
        try:
            logger.info("Attempting form submission...")
            
            # First, let's check what submit elements we have
            submit_info = await page.evaluate("""
                () => {
                    const submitButtons = document.querySelectorAll('#submit_but, input[name="add_message"], input[value*="Добавить"], .submit-data-search');
                    return Array.from(submitButtons).map(btn => ({
                        tagName: btn.tagName,
                        type: btn.type,
                        id: btn.id,
                        name: btn.name,
                        value: btn.value,
                        className: btn.className,
                        disabled: btn.disabled,
                        visible: btn.offsetParent !== null
                    }));
                }
            """)
            
            logger.info(f"Found submit elements: {submit_info}")
            
            # Try different submission methods
            submit_selectors = [
                '#submit_but',
                'input[name="add_message"]',
                'input[value="Добавить объявление"]',
                '.submit-data-search',
                'input[type="submit"]'
            ]
            
            submitted = False
            for selector in submit_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        
                        logger.info(f"Trying selector {selector}: visible={is_visible}, enabled={is_enabled}")
                        
                        if is_visible and is_enabled:
                            await element.click()
                            logger.info(f"✅ Successfully clicked submit button: {selector}")
                            submitted = True
                            break
                        else:
                            logger.warning(f"Submit button found but not clickable: {selector}")
                except Exception as e:
                    logger.warning(f"Failed to click {selector}: {e}")
                    continue
            
            if not submitted:
                logger.warning("No clickable submit button found, trying form submission")
                # Try to submit the form directly
                await page.evaluate("""
                    () => {
                        const forms = document.querySelectorAll('form');
                        if (forms.length > 0) {
                            forms[0].submit();
                            console.log('Form submitted programmatically');
                        }
                    }
                """)
                logger.info("✅ Form submitted programmatically")
            
            # Wait for response and check for errors
            await page.wait_for_timeout(3000)
            
            # Check for any error messages or success indicators
            page_status = await page.evaluate("""
                () => {
                    const url = window.location.href;
                    const title = document.title;
                    const errors = document.querySelectorAll('.error, .alert-danger, .text-danger');
                    const success = document.querySelectorAll('.success, .alert-success, .text-success');
                    
                    return {
                        url: url,
                        title: title,
                        hasErrors: errors.length > 0,
                        errorTexts: Array.from(errors).map(el => el.textContent.trim()),
                        hasSuccess: success.length > 0,
                        successTexts: Array.from(success).map(el => el.textContent.trim())
                    };
                }
            """)
            
            logger.info(f"Page status after submission: {page_status}")
            
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            raise

    async def monitor_manual_session(self):
        """Monitor a manual session for comparison - only record, don't fill automatically"""
        async with async_playwright() as p:
            # Launch browser with clean profile (no persistent cookies)
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-first-run',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create new context with clean state
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='ru-RU',
                timezone_id='Europe/Moscow'
            )
            
            page = await context.new_page()
            
            # Setup recorder for manual session
            manual_recorder = PageStateRecorder("manual_session")
            
            try:
                logger.info("🔍 MANUAL MONITORING MODE - Fill the form manually!")
                logger.info("This will record all your actions for comparison with automated filling")
                
                # Setup comprehensive monitoring
                await manual_recorder.setup_page_monitoring(page)
                
                # Clear any existing cookies/storage
                await context.clear_cookies()
                await context.clear_permissions()
                await page.evaluate("localStorage.clear(); sessionStorage.clear();")
                
                logger.info(f"Navigating to {self.site_url}")
                await page.goto(self.site_url)
                await page.wait_for_load_state('networkidle')
                
                # Wait a bit for page to fully load
                await page.wait_for_timeout(3000)
                
                # 📸 CAPTURE: Initial state
                await manual_recorder.capture_form_state(page, "01_manual_initial")
                await manual_recorder.capture_page_snapshot(page, "01_manual_initial")
                
                logger.info("🎯 NOW FILL THE FORM MANUALLY:")
                logger.info("   1. Select board: Отдых")
                logger.info("   2. Fill ad text: Отдохну")
                logger.info("   3. Fill email: 111@gmail.com")
                logger.info("   4. Check terms agreement")
                logger.info("   5. Solve captcha manually")
                logger.info("   6. Click submit")
                logger.info("")
                logger.info("⏱️  Monitoring will capture states automatically every 10 seconds...")
                logger.info("✋ Close the browser when done to stop monitoring")
                
                # Monitor continuously while user fills manually
                step_counter = 2
                while True:
                    try:
                        await page.wait_for_timeout(10000)  # Wait 10 seconds
                        
                        # Check if page is still alive
                        if page.is_closed():
                            break
                        
                        # Capture current state
                        timestamp = datetime.now().strftime("%H%M%S")
                        state_name = f"{step_counter:02d}_manual_step_{timestamp}"
                        await manual_recorder.capture_form_state(page, state_name)
                        
                        # Check for significant page changes
                        current_url = page.url
                        if "passport.orbita.co.il" in current_url:
                            logger.info("🔄 Detected redirect to login page!")
                            await manual_recorder.capture_page_snapshot(page, f"{state_name}_login_redirect")
                        elif "doska.orbita.co.il" in current_url and "add" not in current_url:
                            logger.info("✅ Detected successful submission!")
                            await manual_recorder.capture_page_snapshot(page, f"{state_name}_success")
                        
                        step_counter += 1
                        
                    except Exception as e:
                        if "page.is_closed" in str(e) or "Target closed" in str(e):
                            break
                        logger.warning(f"Monitoring error: {e}")
                        continue
                
                logger.info("Manual session monitoring completed!")
                manual_recorder.save_session_summary()
                
            except Exception as e:
                logger.error(f"Error in manual monitoring: {e}")
                manual_recorder.save_session_summary()
                raise
            
            logger.info("Manual monitoring session ended.")

async def main():
    """Main function to run the test"""
    # Validate API key from config
    if not CAPTCHA_API_KEY or CAPTCHA_API_KEY == "YOUR_API_KEY_HERE":
        logger.error("Please set your 2captcha API key in config.py!")
        logger.error("Get your API key from: https://2captcha.com/")
        return
    
    logger.info(f"Using 2captcha API key: {CAPTCHA_API_KEY[:8]}...")
    
    # Ask user which mode to run
    print("\n🤖 Choose mode:")
    print("1. Automated filling with recording (default)")
    print("2. Manual monitoring only (for comparison)")
    choice = input("Enter choice (1 or 2): ").strip()
    
    filler = OrbitaTestFormFiller(CAPTCHA_API_KEY)
    
    try:
        if choice == "2":
            logger.info("🔍 Starting manual monitoring mode...")
            await filler.monitor_manual_session()
        else:
            logger.info("🤖 Starting automated filling mode...")
            await filler.fill_test_form()
        
        logger.info("Test completed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 