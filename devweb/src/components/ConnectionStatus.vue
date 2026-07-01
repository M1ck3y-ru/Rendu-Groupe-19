<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useChatStore } from '../stores/chat';

const store = useChatStore();
const { serverUrl, isConnected, isChecking, lastChecked, latency } = storeToRefs(store);

// Periodic polling
let timer: ReturnType<typeof setInterval> | null = null;

const startPolling = () => {
  store.checkConnection();
  timer = setInterval(store.checkConnection, 5000);
};

const stopPolling = () => {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
};

// Re-check if the server URL changes
watch(serverUrl, () => {
  store.checkConnection();
});

onMounted(() => {
  startPolling();
});

onUnmounted(() => {
  stopPolling();
});
</script>

<template>
  <div class="status-container glass-panel">
    <div class="status-header">
      <span class="status-label">Ollama Service</span>
      <button 
        class="refresh-btn" 
        @click="store.checkConnection" 
        :disabled="isChecking"
        :title="'Dernière vérification : ' + lastChecked"
      >
        <svg 
          :class="{ 'spinning': isChecking }" 
          width="14" 
          height="14" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2" 
          stroke-linecap="round" 
          stroke-linejoin="round"
        >
          <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
          <path d="M3 3v5h5" />
          <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
          <path d="M16 16h5v5" />
        </svg>
      </button>
    </div>
    
    <div class="status-badge" :class="isConnected ? 'connected' : 'disconnected'">
      <span class="status-dot"></span>
      <span class="status-text">
        {{ isConnected ? 'CONNECTÉ' : 'DÉCONNECTÉ' }}
      </span>
      <span v-if="isConnected && latency !== null" class="latency">
        {{ latency }}ms
      </span>
    </div>
    
    <div class="status-meta">
      <span class="meta-label">Node :</span>
      <span class="meta-value">{{ serverUrl }}</span>
    </div>
  </div>
</template>

<style scoped>
.status-container {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: rgba(18, 24, 36, 0.4);
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 4px;
  color: var(--text-secondary);
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.status-badge.connected {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: var(--accent-emerald);
}

.status-badge.disconnected {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: var(--accent-danger);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.connected .status-dot {
  background-color: var(--accent-emerald);
  animation: pulse-green 2s infinite;
}

.disconnected .status-dot {
  background-color: var(--accent-danger);
  animation: pulse-red 2s infinite;
}

.status-text {
  flex-grow: 1;
}

.latency {
  font-size: 0.75rem;
  font-weight: 400;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.status-meta {
  display: flex;
  gap: 6px;
  font-size: 0.75rem;
  font-family: var(--font-mono);
  overflow: hidden;
}

.meta-label {
  color: var(--text-muted);
  white-space: nowrap;
}

.meta-value {
  color: var(--text-secondary);
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}
</style>
