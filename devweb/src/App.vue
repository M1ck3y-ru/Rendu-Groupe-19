<script setup lang="ts">
import { ref } from 'vue';
import ConnectionStatus from './components/ConnectionStatus.vue';
import SettingsPanel from './components/SettingsPanel.vue';
import ChatInterface from './components/ChatInterface.vue';

// Mobile responsiveness
const isSidebarOpen = ref(false);
</script>

<template>
  <div class="layout-container">
    <!-- Sidebar Toggle (Mobile only) -->
    <button 
      class="mobile-toggle-btn" 
      @click="isSidebarOpen = !isSidebarOpen"
      :aria-label="isSidebarOpen ? 'Fermer le menu' : 'Ouvrir le menu'"
    >
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="4" x2="20" y1="12" y2="12" />
        <line x1="4" x2="20" y1="6" y2="6" />
        <line x1="4" x2="20" y1="18" y2="18" />
      </svg>
    </button>

    <!-- Sidebar Panel -->
    <aside class="sidebar" :class="{ 'sidebar-open': isSidebarOpen }">
      <!-- Sidebar Header -->
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-symbol">T</span>
          <div class="logo-text">
            <h2>TECHCORP</h2>
            <span>INTELLIGENCE ARTIFICIELLE</span>
          </div>
        </div>
      </div>

      <!-- Settings Panel -->
      <div class="sidebar-content">
        <SettingsPanel />
      </div>

      <!-- Connection Status Banner -->
      <div class="sidebar-footer">
        <ConnectionStatus />
      </div>
    </aside>

    <!-- Overlay backdrop for mobile when sidebar is open -->
    <div 
      v-if="isSidebarOpen" 
      class="sidebar-overlay" 
      @click="isSidebarOpen = false"
    ></div>

    <!-- Main Chat Area -->
    <main class="main-content">
      <ChatInterface />
    </main>
  </div>
</template>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  width: 320px;
  overflow: hidden;
  z-index: 100;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-symbol {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--accent-emerald) 0%, var(--accent-blue) 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--bg-primary);
  font-weight: 800;
  font-size: 1.3rem;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

.logo-text h2 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: var(--text-primary);
}

.logo-text span {
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  text-transform: uppercase;
}

.sidebar-content {
  flex-grow: 1;
  padding: 20px;
  overflow-y: auto;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid var(--border-color);
  background: rgba(10, 14, 23, 0.3);
}

.main-content {
  height: 100vh;
  overflow: hidden;
  position: relative;
}

/* Mobile responsive styles */
.mobile-toggle-btn {
  display: none;
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 101;
  background: rgba(18, 24, 36, 0.8);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px;
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(8px);
}

@media (max-width: 768px) {
  .mobile-toggle-btn {
    display: flex;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    transform: translateX(-100%);
  }

  .sidebar.sidebar-open {
    transform: translateX(0);
  }

  .sidebar-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    z-index: 99;
  }
}
</style>
