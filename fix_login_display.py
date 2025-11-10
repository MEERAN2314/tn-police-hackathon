#!/usr/bin/env python3
"""
Fix login display issues by creating a simple client-side solution
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_login_fix_js():
    """Create JavaScript fix for login display"""
    js_content = '''
// Login state management for TOR Analysis System
(function() {
    'use strict';
    
    // Check authentication state
    function checkAuthState() {
        const userSession = getCookie('user_session');
        const accessToken = getCookie('access_token');
        
        console.log('🔍 Checking auth state...');
        console.log('User session:', userSession);
        console.log('Access token:', accessToken ? 'Present' : 'Not found');
        
        if (userSession || accessToken) {
            showLoggedInState(userSession || 'user');
        } else {
            showLoggedOutState();
        }
    }
    
    // Get cookie value
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
    
    // Show logged in state
    function showLoggedInState(username) {
        console.log('✅ Showing logged in state for:', username);
        
        // Find the login button and replace with user profile
        const loginButton = document.querySelector('a[href="/auth/login"]');
        if (loginButton && loginButton.textContent.includes('Login to System')) {
            const sidebar = loginButton.closest('aside') || loginButton.closest('.sidebar');
            if (sidebar) {
                // Create user profile section
                const userProfileHTML = `
                    <div style="padding: 20px; border-bottom: 1px solid #e5e7eb;">
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #06b6d4, #3b82f6); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 18px;">
                                ${username.charAt(0).toUpperCase()}
                            </div>
                            <div style="flex: 1;">
                                <h3 style="font-size: 16px; font-weight: 600; color: #1f2937; margin: 0; line-height: 1.2;">${username}</h3>
                                <p style="font-size: 14px; color: #6b7280; margin: 0;">Administrator</p>
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: #f0fdf4; border-radius: 8px; border: 1px solid #bbf7d0;">
                            <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%;"></div>
                            <span style="font-size: 14px; color: #059669; font-weight: 500;">System Connected</span>
                        </div>
                    </div>
                `;
                
                // Replace login button with user profile
                const loginContainer = loginButton.parentElement;
                loginContainer.innerHTML = userProfileHTML;
                
                // Add logout button
                const logoutHTML = `
                    <a href="/auth/logout" style="display: flex; align-items: center; padding: 8px 0; color: #dc2626; text-decoration: none; font-weight: 500; transition: all 0.2s ease;"
                       onmouseover="this.style.color='#b91c1c'; this.style.background='#fef2f2'; this.style.borderRadius='6px'; this.style.padding='8px 12px'; this.style.margin='0 -12px';"
                       onmouseout="this.style.color='#dc2626'; this.style.background='transparent'; this.style.padding='8px 0'; this.style.margin='0';">
                        <svg style="width: 18px; height: 18px; margin-right: 12px;" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.59L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
                        </svg>
                        Logout
                    </a>
                `;
                
                // Find the bottom section and add logout
                const bottomSection = sidebar.querySelector('div[style*="position: absolute; bottom: 0"]');
                if (bottomSection) {
                    bottomSection.innerHTML = `
                        <div style="padding: 0 0 12px 0;">
                            <h4 style="font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin: 0;">Account</h4>
                        </div>
                        ${logoutHTML}
                    `;
                }
            }
        }
    }
    
    // Show logged out state
    function showLoggedOutState() {
        console.log('🔓 Showing logged out state');
        // The default template already handles this
    }
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Login state manager initialized');
        checkAuthState();
        
        // Check auth state periodically
        setInterval(checkAuthState, 5000);
    });
    
    // Listen for login events
    window.addEventListener('storage', function(e) {
        if (e.key === 'user_session' || e.key === 'access_token') {
            checkAuthState();
        }
    });
    
})();
'''
    
    # Write to static JS file
    with open('static/js/login-fix.js', 'w') as f:
        f.write(js_content)
    
    logger.info("✅ Created login fix JavaScript file")

def main():
    """Main function"""
    logger.info("🔧 Creating Login Display Fix")
    logger.info("=" * 40)
    
    create_login_fix_js()
    
    logger.info("✅ Login display fix created!")
    logger.info("")
    logger.info("📋 NEXT STEPS:")
    logger.info("1. The JavaScript fix will automatically detect login state")
    logger.info("2. Test login with: admin / admin123")
    logger.info("3. Check browser console for debug messages")
    logger.info("4. Visit: http://localhost:8004/debug/auth to check auth status")
    logger.info("")
    logger.info("🔍 DEBUG ENDPOINTS:")
    logger.info("• http://localhost:8004/debug/auth - Check authentication")
    logger.info("• Browser Console - See login state messages")
    logger.info("• Developer Tools > Application > Cookies - Check cookies")

if __name__ == "__main__":
    main()