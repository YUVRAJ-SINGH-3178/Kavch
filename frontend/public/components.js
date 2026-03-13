// ═══════════════════════════════════════════════════════════
//  Kavch Components.js — Shared UI + Auth + API Layer
// ═══════════════════════════════════════════════════════════

// ── Auth Helper Functions ────────────────────────────────
function getAuthToken() {
    return localStorage.getItem('shieldher_token');
}

function getUser() {
    const u = localStorage.getItem('shieldher_user');
    return u ? JSON.parse(u) : null;
}

function isLoggedIn() {
    return !!getAuthToken();
}

function saveAuth(token, user) {
    localStorage.setItem('shieldher_token', token);
    localStorage.setItem('shieldher_user', JSON.stringify(user));
}

function logout() {
    localStorage.removeItem('shieldher_token');
    localStorage.removeItem('shieldher_user');
    localStorage.removeItem('shieldher_vault');
    localStorage.removeItem('shieldher_certs');
    window.location.href = 'login.html';
}

// ── Navigation ───────────────────────────────────────────
function injectNavbar() {
    const currentPath = window.location.pathname;
    const user = getUser();

    const links = [
        { name: 'Report', href: 'report.html' },
        { name: 'Image Scan', href: 'image-scan.html' },
        { name: 'Vault', href: 'vault.html' },
        { name: 'Safe Net', href: 'safe-net.html' }
    ];

    const navLinksHtml = links.map(link => {
        const cleanHref = link.href.replace('.html', '');
        const isActive = currentPath.includes(cleanHref) || (currentPath === '/' && cleanHref === 'index');
        const colorClass = isActive ? 'text-white' : 'text-gray-400 hover:text-white';
        const dot = isActive ? '<div class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-[#FF4500] rounded-full"></div>' : '';
        return `<a href="${link.href}" class="relative text-sm transition-colors duration-300 ${colorClass}">${link.name}${dot}</a>`;
    }).join('');

    // Auth button — shows login or user profile
    let authButtonHtml = '';
    if (user) {
        const initials = user.name ? user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : '?';
        authButtonHtml = `
            <div class="relative group">
                <button id="userMenuBtn" class="flex items-center gap-2 px-3 py-2 rounded-full border border-white/10 hover:border-white/30 transition-all duration-300 bg-white/5">
                    <div class="w-7 h-7 rounded-full bg-[#FF4500] flex items-center justify-center text-white text-xs font-bold">${initials}</div>
                    <span class="text-sm text-white/80 hidden md:inline">${user.name.split(' ')[0]}</span>
                    <iconify-icon icon="lucide:chevron-down" class="text-xs text-gray-500"></iconify-icon>
                </button>
                <div id="userMenu" class="hidden absolute right-0 top-full mt-2 w-48 bg-[#111] border border-white/10 rounded-2xl shadow-2xl overflow-hidden z-[60]">
                    <div class="px-4 py-3 border-b border-white/5">
                        <p class="text-sm text-white font-medium">${user.name}</p>
                        <p class="text-xs text-gray-500">${user.email}</p>
                    </div>
                    <a href="dashboard.html" class="block px-4 py-2.5 text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors">
                        <iconify-icon icon="lucide:layout-dashboard" class="mr-2"></iconify-icon>Dashboard
                    </a>
                    <button onclick="logout()" class="w-full text-left px-4 py-2.5 text-sm text-gray-400 hover:text-red-400 hover:bg-white/5 transition-colors">
                        <iconify-icon icon="lucide:log-out" class="mr-2"></iconify-icon>Sign Out
                    </button>
                </div>
            </div>`;
    } else {
        authButtonHtml = `
            <a href="login.html" class="inline-flex shrink-0 items-center justify-center px-4 py-2 md:px-5 md:py-2.5 rounded-full text-xs md:text-sm font-medium border border-white/20 text-white hover:bg-white/5 transition-all duration-300">
                Sign In
            </a>`;
    }

    const navHtml = `
        <nav id="main-nav" class="fixed top-0 left-0 right-0 z-50 transition-all duration-500 py-8 bg-transparent">
            <div class="container mx-auto px-4 md:px-6 flex items-center justify-between">
                <a href="index.html" class="text-xl md:text-2xl font-bold tracking-tighter font-serif shrink-0">
                    Kavch.
                </a>
                
                <div class="hidden md:flex items-center space-x-8">
                    ${navLinksHtml}
                </div>

                <div class="flex items-center gap-2 md:gap-3">
                    <a href="vault.html" class="md:hidden inline-flex shrink-0 items-center justify-center w-10 h-10 rounded-full border border-white/20 text-white hover:bg-white/5 transition-all duration-300" aria-label="Open Vault">
                        <iconify-icon icon="lucide:lock" class="text-base"></iconify-icon>
                    </a>
                    <a href="report.html" class="inline-flex shrink-0 items-center justify-center px-4 py-2 md:px-6 md:py-3 rounded-full text-xs md:text-sm font-medium bg-white text-black hover:scale-105 hover:bg-gray-100 transition-all duration-300">
                        Report Threat
                    </a>
                    ${authButtonHtml}
                </div>
            </div>
        </nav>
    `;

    document.write(navHtml);

    // Navbar scroll effect
    setTimeout(() => {
        const nav = document.getElementById('main-nav');
        if (!nav) return;
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                nav.classList.add('py-4', 'bg-[#050505]/80', 'backdrop-blur-md', 'border-b', 'border-white/5');
                nav.classList.remove('py-8', 'bg-transparent');
            } else {
                nav.classList.remove('py-4', 'bg-[#050505]/80', 'backdrop-blur-md', 'border-b', 'border-white/5');
                nav.classList.add('py-8', 'bg-transparent');
            }
        });

        // User menu toggle
        const menuBtn = document.getElementById('userMenuBtn');
        const menu = document.getElementById('userMenu');
        if (menuBtn && menu) {
            menuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                menu.classList.toggle('hidden');
            });
            document.addEventListener('click', () => {
                menu.classList.add('hidden');
            });
        }
    }, 0);
}

function injectFooter() {
    const footerHtml = `
        <footer class="py-20 border-t border-white/5 bg-[#050505] relative overflow-hidden mt-auto">
            <div class="container mx-auto px-6 relative z-10">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-12">
                    <div class="w-full md:w-auto">
                        <h2 class="text-[10vw] leading-[0.8] tracking-tighter text-white/10 font-bold select-none pointer-events-none">
                            Kavch.
                        </h2>
                    </div>
                    
                    <div class="flex flex-col gap-8 text-right">
                        <div class="flex flex-col gap-4 text-gray-400 text-sm">
                            <p>Helpline: <span class="text-white font-medium">1930</span> (National Cybercrime)</p>
                            <p>Women's: <span class="text-white font-medium">181</span></p>
                        </div>
                        <p class="text-sm text-gray-600">© 2026 Kavch. Built for Indian women.</p>
                    </div>
                </div>
            </div>
        </footer>
    `;

    document.write(footerHtml);
}

function initNoise() {
    if (!document.querySelector('.noise-overlay')) {
        const noiseHtml = '<div class="noise-overlay" style="position: fixed; inset: 0; z-index: 50; pointer-events: none; opacity: 0.05; mix-blend-mode: overlay; background-image: url(\'https://grainy-gradients.vercel.app/noise.svg\');"></div>';
        document.body.insertAdjacentHTML('afterbegin', noiseHtml);
    }
}

// Auto-initialize reveal observer and noise on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initNoise();
    
    // Inject Favicon if not present
    if (!document.querySelector('link[rel="icon"]')) {
        const favicon = document.createElement('link');
        favicon.rel = 'icon';
        favicon.href = 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🛡️</text></svg>';
        document.head.appendChild(favicon);
    }

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));
});

// ── Toast Notifications ──────────────────────────────────
function showToast(message, type = 'success') {
    let borderClass = 'border-white/10 border-l-[#FF4500]';
    if (type === 'error') borderClass = 'border-white/10 border-l-red-500';
    if (type === 'warning') borderClass = 'border-white/10 border-l-amber-500';

    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="fixed bottom-6 right-6 z-[100] bg-[#111] border ${borderClass} border-l-4 rounded-2xl px-6 py-4 text-sm font-inter text-white shadow-2xl transform translate-x-full transition-transform duration-500 flex items-center gap-3">
            <div>${message}</div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', toastHtml);
    const toastEl = document.getElementById(toastId);
    
    // Animate in
    setTimeout(() => {
        toastEl.classList.remove('translate-x-full');
    }, 10);

    // Auto dismiss
    setTimeout(() => {
        toastEl.classList.add('translate-x-full');
        setTimeout(() => toastEl.remove(), 500);
    }, 4000);
}

// ── API Layer (with automatic auth token injection) ──────
const API_BASE = window.API_URL || 'http://localhost:8000';

async function apiCall(endpoint, data, method = 'POST') {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);
        
        const options = {
            method: method,
            signal: controller.signal
        };
        
        // Handle FormData directly vs JSON
        if (data instanceof FormData) {
            options.body = data;
            // Add auth header for FormData too
            const token = getAuthToken();
            if (token) {
                options.headers = {
                    'Authorization': `Bearer ${token}`
                };
            }
        } else if (data && method !== 'GET') {
            const headers = {
                'Content-Type': 'application/json'
            };
            // ✨ Automatically attach auth token if logged in
            const token = getAuthToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            options.headers = headers;
            options.body = JSON.stringify(data);
        } else {
            // GET requests
            const headers = {};
            const token = getAuthToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            if (Object.keys(headers).length > 0) {
                options.headers = headers;
            }
        }
        
        const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}/api/${endpoint}`;
        
        const response = await fetch(url, options);
        clearTimeout(timeoutId);
        
        // Handle 401 — token expired or invalid
        if (response.status === 401) {
            // Don't redirect if we're already on login/signup page
            const path = window.location.pathname;
            if (!path.includes('login') && !path.includes('signup')) {
                localStorage.removeItem('shieldher_token');
                localStorage.removeItem('shieldher_user');
                showToast('Session expired. Please log in again.', 'warning');
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1500);
            }
            throw new Error('Authentication required');
        }
        
        if (!response.ok) {
            let errorMsg = 'API Error: ' + response.status;
            try {
                const errorData = await response.json();
                if (errorData.detail) errorMsg = errorData.detail;
            } catch(e) {}
            throw new Error(errorMsg);
        }
        return await response.json();
    } catch (error) {
        const msg = error.name === 'AbortError' ? 'Request timed out' : (error.message || 'Network error occurred');
        if (msg !== 'Authentication required') {
            showToast(msg, 'error');
        }
        console.error(error);
        throw error;
    }
}

// ── Auth Guard (use on protected pages) ──────────────────
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}
