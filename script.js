document.addEventListener('DOMContentLoaded', () => {
    /**
     * SmartMail Logic
     * Handles persistence, state management, and UI updates.
     */

    const STORAGE_KEY = 'smartmail_data_v1';
    
    // DOM Elements
    const onboardingView = document.getElementById('onboarding-view');
    const dashboardView = document.getElementById('dashboard-view');
    const appHeader = document.getElementById('app-header');
    const setupForm = document.getElementById('setup-form');
    const phoneInput = document.getElementById('phone-input');
    const headerPhoneNum = document.getElementById('header-phone-num');
    const notifList = document.getElementById('notif-list');
    const toastEl = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');
    
    // Stats Elements
    const statTotal = document.getElementById('stat-total');
    const statWeek = document.getElementById('stat-week');
    const statPending = document.getElementById('stat-pending');

    // Settings Elements
    const settingsModal = document.getElementById('settings-modal');
    const settingsInput = document.getElementById('settings-phone-input');
    const openSettingsBtn = document.getElementById('open-settings');
    const closeSettingsBtn = document.getElementById('close-settings');
    const saveSettingsBtn = document.getElementById('save-settings');
    const resetDataBtn = document.getElementById('reset-data');

    // State
    let appData = {
        phoneNumber: null,
        notifications: []
    };

    // --- Initialization ---
    function init() {
        loadData();
        
        if (appData.phoneNumber) {
            showDashboard();
        } else {
            showOnboarding();
        }
    }

    // --- Persistence ---
    function loadData() {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            appData = JSON.parse(stored);
        }
    }

    function saveData() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(appData));
        updateStats();
        renderNotifications();
    }

    // --- View Management ---
    function showOnboarding() {
        onboardingView.classList.add('active');
        dashboardView.classList.remove('active');
        appHeader.style.display = 'none';
    }

    function showDashboard() {
        onboardingView.classList.remove('active');
        dashboardView.classList.add('active');
        appHeader.style.display = 'flex';
        headerPhoneNum.textContent = formatPhoneNumber(appData.phoneNumber);
        settingsInput.value = appData.phoneNumber;
        updateStats();
        renderNotifications();
    }

    // --- Core Logic ---

    // Setup Number
    setupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const rawNum = phoneInput.value.trim();
        
        // Basic validation: integer only, length check
        if (!rawNum || isNaN(rawNum)) {
            showToast("Please enter a valid number", "error");
            return;
        }
        
        // Convert to integer as requested
        appData.phoneNumber = parseInt(rawNum, 10);
        
        // Add welcome notification
        //addNotification("System Connected", 
                        //"SmartMail Box is now active.", 
                        //"delivered");
        showToast("System connected successfully", "success");

        
        saveData();
        showToast("Number saved successfully!", "success");
        showDashboard();
    });

    // Add Notification (Internal Helper)
    function addNotification(title, desc, type = "delivered") {
        const newNotif = {
            id: Date.now(),
            title: title,
            desc: desc,
            type: type, // 'delivered' or 'pending'
            timestamp: new Date().toISOString(),
            read: false
        };
        // Add to beginning of array
        appData.notifications.unshift(newNotif);
        saveData();
    }

    // --- Stats Calculation ---
    function updateStats() {
        const total = appData.notifications.length;
        const pending = appData.notifications.filter(n => !n.read).length;
        
        // Calculate "This Week" (simple logic: within last 7 days)
        const oneWeekAgo = new Date();
        oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
        const weekCount = appData.notifications.filter(n => new Date(n.timestamp) > oneWeekAgo).length;

        // Animate numbers
        animateValue(statTotal, parseInt(statTotal.textContent), total, 500);
        animateValue(statWeek, parseInt(statWeek.textContent), weekCount, 500);
        animateValue(statPending, parseInt(statPending.textContent), pending, 500);
    }

    // --- UI Rendering ---

    function renderNotifications() {
        notifList.innerHTML = '';

        if (appData.notifications.length === 0) {
            notifList.innerHTML = `
                <div class="empty-state">
                    <i class="fa-regular fa-bell-slash"></i>
                    <p>No notifications yet.</p>
                </div>
            `;
            return;
        }

        appData.notifications.forEach(notif => {
            const dateObj = new Date(notif.timestamp);
            const timeStr = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const dateStr = dateObj.toLocaleDateString([], { month: 'short', day: 'numeric' });
            
            const iconClass = notif.type === 'delivered' ? 'delivered' : 'pending';
            const iconFa = notif.type === 'delivered' ? 'fa-check' : 'fa-clock';

            const item = document.createElement('div');
            item.className = 'notif-item';
            if (!notif.read) item.style.borderLeft = "4px solid var(--primary)";

            item.innerHTML = `
                <div class="notif-icon ${iconClass}">
                    <i class="fa-solid ${iconFa}"></i>
                </div>
                <div class="notif-content">
                    <div class="notif-header">
                        <span class="notif-title">${notif.title}</span>
                        <span class="notif-time">${timeStr}</span>
                    </div>
                    <div class="notif-desc">${notif.desc} &bull; ${dateStr}</div>
                </div>
            `;
            
            // Mark as read on click
            item.addEventListener('click', () => {
                notif.read = true;
                saveData();
            });

            notifList.appendChild(item);
        });
    }

    function formatPhoneNumber(num) {
        if (!num) return '';
        const s = num.toString();
        return `+${s.slice(0,1)} (${s.slice(1,4)}) ${s.slice(4,7)}-${s.slice(7)}`;
    }

    // --- Interactions & Utilities ---

    // Settings Modal
    openSettingsBtn.addEventListener('click', () => {
        settingsModal.classList.add('open');
    });

    closeSettingsBtn.addEventListener('click', () => {
        settingsModal.classList.remove('open');
    });

    saveSettingsBtn.addEventListener('click', () => {
        const newNum = parseInt(settingsInput.value, 10);
        if (newNum && !isNaN(newNum)) {
            appData.phoneNumber = newNum;
            saveData();
            headerPhoneNum.textContent = formatPhoneNumber(newNum);
            settingsModal.classList.remove('open');
            showToast("Settings updated", "success");
        } else {
            showToast("Invalid number", "error");
        }
    });

    resetDataBtn.addEventListener('click', () => {
        if(confirm("Are you sure? This will delete all history.")) {
            localStorage.removeItem(STORAGE_KEY);
            appData.phoneNumber = null;
            appData.notifications = [];
            settingsModal.classList.remove('open');
            location.reload();
        }
    });

    // Mark all read
    document.getElementById('mark-read').addEventListener('click', () => {
        appData.notifications.forEach(n => n.read = true);
        saveData();
        showToast("All marked as read", "success");
    });

    // --- Simulation Logic (For Demo Purposes) ---
    const carriers = ['FedEx', 'UPS', 'DHL', 'Amazon Logistics', 'USPS'];
    const senders = ['Apple Inc.', 'Best Buy', 'Amazon', 'eBay Seller', 'Mom'];
    
    document.getElementById('sim-btn').addEventListener('click', () => {
        // Generate random package data
        const randomCarrier = carriers[Math.floor(Math.random() * carriers.length)];
        const randomSender = senders[Math.floor(Math.random() * senders.length)];
        const trackingId = Math.floor(100000000 + Math.random() * 900000000);
        
        const title = `Package Delivered`;
        const desc = `From ${randomSender} via ${randomCarrier} (#${trackingId})`;
        
        addNotification(title, desc, "delivered");
        showToast("New Package Detected!", "success");
        
        // Scroll to top of list
        notifList.scrollTop = 0;
    });

    // Number animation helper
    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // Toast helper
    function showToast(msg, type = "normal") {
        toastMsg.textContent = msg;
        toastEl.className = `toast show ${type}`;
        setTimeout(() => {
            toastEl.classList.remove('show');
        }, 3000);
    }

    // Initialize App
    init();
});